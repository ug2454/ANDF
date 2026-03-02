"""
macOS ANDF Viewer app installer.

Creates a minimal .app bundle using osacompile (ships with every Mac),
patches its Info.plist to declare the com.andf.document UTI and register
.andf as a document type, then tells Launch Services to pick it up immediately
— no logout required.

Usage:
    python -m andf.cli install          # → ~/Applications/ANDF Viewer.app
    python -m andf.cli uninstall
"""
from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
import tempfile

# ─────────────────────────────────────────────────────────────────────────────
# Python helper embedded inside the app bundle (Resources/open_andf.py).
# Pure stdlib — opens the .andf file in the default browser via local HTTP.
# ─────────────────────────────────────────────────────────────────────────────

_OPENER_PY = '''\
#!/usr/bin/env python3
"""
ANDF Viewer helper.
Called by ANDF Viewer.app when the user opens a .andf file.
Serves the file over localhost so the browser opens it as
    http://localhost:PORT/filename.andf
"""
import http.server
import os
import socket
import subprocess
import sys
import threading


def open_andf(path: str) -> None:
    abs_path = os.path.abspath(path)
    directory = os.path.dirname(abs_path)
    filename = os.path.basename(abs_path)

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    served = threading.Event()

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def log_message(self, *args):
            pass  # silence server log

        def send_response(self, code, message=None):
            super().send_response(code, message)
            if code == 200:
                served.set()

        def guess_type(self, path):
            if str(path).endswith(".andf"):
                return "text/html; charset=utf-8"
            return super().guess_type(path)

    server = http.server.HTTPServer(("127.0.0.1", port), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    subprocess.run(["open", f"http://localhost:{port}/{filename}"])
    served.wait(timeout=15)
    server.shutdown()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)
    open_andf(sys.argv[1])
'''

# ─────────────────────────────────────────────────────────────────────────────
# AppleScript source.
# "on open" receives Apple Events from Finder when the user double-clicks
# a .andf file — the same mechanism PDF viewers use.
# PYTHON3_PATH is replaced at install time with the real python3 binary.
# ─────────────────────────────────────────────────────────────────────────────

_APPLESCRIPT_TEMPLATE = '''\
on open theFiles
    set helperScript to POSIX path of (path to resource "open_andf.py")
    repeat with aFile in theFiles
        set filePath to POSIX path of aFile
        do shell script "PYTHON3_PATH " & quoted form of helperScript & " " & quoted form of filePath & " &"
    end repeat
end open

on run
    display dialog "ANDF Viewer" & return & return & \
        "Double-click any .andf file to open it in your browser." & return & return & \
        "To open a file now, use:" & return & \
        "  andf open <file.andf>" \
        with title "ANDF Viewer" buttons {"OK"} default button "OK"
end run
'''

# ─────────────────────────────────────────────────────────────────────────────
# UTI + document type declarations for Info.plist
# ─────────────────────────────────────────────────────────────────────────────

_UTI_EXPORT = {
    "UTTypeIdentifier": "com.andf.document",
    "UTTypeDescription": "ANDF Document",
    "UTTypeConformsTo": ["public.html"],
    "UTTypeTagSpecification": {
        "public.filename-extension": ["andf"],
        "public.mime-type": "application/andf+html",
    },
}

_DOC_TYPE = {
    "CFBundleTypeName": "ANDF Document",
    "CFBundleTypeRole": "Viewer",
    "LSHandlerRank": "Owner",
    "LSItemContentTypes": ["com.andf.document"],
    "CFBundleTypeExtensions": ["andf"],
    "CFBundleTypeIconFile": "droplet",
}

_LSREGISTER = (
    "/System/Library/Frameworks/CoreServices.framework"
    "/Frameworks/LaunchServices.framework/Support/lsregister"
)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def install(target_dir: str = "~/Applications") -> str:
    """
    Build ANDF Viewer.app in *target_dir* and register it with Launch Services.

    Returns the absolute path to the installed .app bundle.
    """
    target_dir = os.path.expanduser(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    app_path = os.path.join(target_dir, "ANDF Viewer.app")

    # Remove old install if present
    if os.path.exists(app_path):
        shutil.rmtree(app_path)

    # Find python3
    python3 = shutil.which("python3") or "/usr/bin/python3"

    # Build AppleScript source with the real python3 path baked in
    applescript = _APPLESCRIPT_TEMPLATE.replace("PYTHON3_PATH", python3)

    # Compile into an .app bundle with osacompile
    with tempfile.NamedTemporaryFile(suffix=".applescript", delete=False, mode="w") as f:
        f.write(applescript)
        as_path = f.name
    try:
        result = subprocess.run(
            ["osacompile", "-o", app_path, as_path],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"osacompile failed:\n{result.stderr}")
    finally:
        os.unlink(as_path)

    # Copy Python helper into Resources/
    resources_dir = os.path.join(app_path, "Contents", "Resources")
    helper_path = os.path.join(resources_dir, "open_andf.py")
    with open(helper_path, "w") as f:
        f.write(_OPENER_PY)
    os.chmod(helper_path, 0o755)

    # Patch Info.plist — add UTI export + document type
    plist_path = os.path.join(app_path, "Contents", "Info.plist")
    with open(plist_path, "rb") as f:
        plist = plistlib.load(f)

    plist["CFBundleIdentifier"] = "com.andf.viewer"
    plist["CFBundleName"] = "ANDF Viewer"
    plist["CFBundleDisplayName"] = "ANDF Viewer"
    plist["CFBundleShortVersionString"] = "1.0"
    plist["CFBundleVersion"] = "1"
    plist["UTExportedTypeDeclarations"] = [_UTI_EXPORT]
    plist["CFBundleDocumentTypes"] = [_DOC_TYPE]

    with open(plist_path, "wb") as f:
        plistlib.dump(plist, f)

    # Register with Launch Services (takes effect immediately, no logout needed)
    subprocess.run([_LSREGISTER, "-f", app_path],
                   capture_output=True)

    return app_path


def uninstall(target_dir: str = "~/Applications") -> str:
    """Remove ANDF Viewer.app and deregister it from Launch Services."""
    app_path = os.path.join(os.path.expanduser(target_dir), "ANDF Viewer.app")
    if not os.path.exists(app_path):
        raise FileNotFoundError(f"Not found: {app_path}")
    subprocess.run([_LSREGISTER, "-u", app_path], capture_output=True)
    shutil.rmtree(app_path)
    return app_path
