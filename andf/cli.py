"""
ANDF Command-Line Interface

Usage:
    python -m andf.cli new <output.andf>
    python -m andf.cli open <file.andf>
    python -m andf.cli parse <file.andf> [--pretty]
    python -m andf.cli validate <file.andf>
    python -m andf.cli info <file.andf>
    python -m andf.cli ai <file.andf>
"""
from __future__ import annotations

import argparse
import json
import os
import sys


def cmd_new(args):
    from .document import ANDFDocument
    output = args.output
    doc = ANDFDocument()
    doc.set_metadata(title="New ANDF Document", authors=["Author"])
    sec = doc.add_section("introduction", "Introduction")
    sec.paragraph("This is a new ANDF document. Edit it using the ANDF Python library.")
    doc.save(output)
    print(f"Created: {output}")


def _app_is_installed(target_dir: str = "~/Applications") -> bool:
    """Return True if ANDF Viewer.app is installed."""
    app_path = os.path.join(os.path.expanduser(target_dir), "ANDF Viewer.app")
    return os.path.isdir(app_path)


def _open_in_browser(path: str) -> None:
    """Open a .andf file in the browser.

    Strategy (in order):
    1. macOS + app installed → `open file.andf` (OS routes to ANDF Viewer.app,
       no server needed here — the app handles it internally).
    2. Fallback (app not installed, Linux, Windows) → ephemeral localhost server
       so the browser gets the file as http://localhost:PORT/file.andf.
    """
    import platform
    import subprocess

    abs_path = os.path.abspath(path)
    system = platform.system()

    if system == "Darwin" and _app_is_installed():
        # Clean path: the installed app owns .andf, no server required.
        subprocess.run(["open", abs_path])
        return

    # Fallback: serve over localhost (works everywhere, no install needed).
    _serve_and_open(abs_path)


def _serve_and_open(abs_path: str) -> None:
    """Ephemeral localhost HTTP server — fallback when app is not installed."""
    import http.server
    import platform
    import socket
    import subprocess
    import threading

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
            pass

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

    url = f"http://localhost:{port}/{filename}"
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["open", url])
    elif system == "Windows":
        os.startfile(url)
    else:
        subprocess.run(["xdg-open", url])

    served.wait(timeout=15)
    server.shutdown()


def cmd_open(args):
    path = args.file
    if not os.path.exists(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    _open_in_browser(path)
    print(f"Opened: file://{os.path.abspath(path)}")


def cmd_parse(args):
    from .parser import ANDFParser
    path = args.file
    if not os.path.exists(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    data = ANDFParser.extract_json(content)
    indent = 2 if args.pretty else None
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def cmd_validate(args):
    from .parser import ANDFParser
    path = args.file
    if not os.path.exists(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        data = ANDFParser.extract_json(content)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"INVALID — could not parse JSON: {e}", file=sys.stderr)
        sys.exit(1)
    ok, errors = ANDFParser.validate(data)
    if ok:
        print("VALID — no errors found.")
    else:
        print(f"INVALID — {len(errors)} error(s):")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)


def cmd_info(args):
    from .document import ANDFDocument
    path = args.file
    if not os.path.exists(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    doc = ANDFDocument.from_file(path)
    meta = doc._metadata
    layout = doc._layout
    theme = doc._theme

    def row(label, value):
        print(f"  {label:<22} {value}")

    print("\n─── ANDF Document Info ──────────────────")
    row("Title:", meta.get("title", ""))
    row("Subtitle:", meta.get("subtitle", "") or "—")
    row("Authors:", ", ".join(meta.get("authors", [])) or "—")
    row("Created:", meta.get("created", "")[:10])
    row("Modified:", meta.get("modified", "")[:10])
    row("Status:", meta.get("status", ""))
    row("Version:", meta.get("version", ""))
    row("Language:", meta.get("language", "en"))
    row("Category:", meta.get("category", "") or "—")
    row("Keywords:", ", ".join(meta.get("keywords", [])) or "—")
    row("License:", meta.get("license", "") or "—")
    print("─── Layout ──────────────────────────────")
    row("Page size:", layout.get("page_size", "A4"))
    row("Orientation:", layout.get("orientation", "portrait"))
    row("Columns:", layout.get("columns", 1))
    print("─── Theme ───────────────────────────────")
    row("Theme:", theme.get("name", "default"))
    row("Body font:", theme.get("font_body", ""))
    print("─── Content ─────────────────────────────")
    row("Sections:", len(doc._sections))
    row("Blocks:", len(doc._blocks))
    row("Assets:", len(doc._assets))
    row("References:", len(doc._references))
    print("─────────────────────────────────────────\n")


def cmd_ai(args):
    from .ai_layer import ANDFAILayer
    from .document import ANDFDocument
    path = args.file
    if not os.path.exists(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    doc = ANDFDocument.from_file(path)
    layer = ANDFAILayer(doc)
    summary = layer.document_summary()

    print("\n─── ANDF AI Layer ───────────────────────")
    print(f"  Title:          {summary['title']}")
    print(f"  Summary:        {summary['summary'][:200] or '(none)'}")
    print(f"  Complexity:     {summary['complexity']}")
    print(f"  Reading time:   {summary['reading_time_minutes']} min")
    print(f"  Sections:       {summary['section_count']}")
    print(f"  Blocks:         {summary['block_count']}")
    print(f"  References:     {summary['reference_count']}")

    if summary["key_points"]:
        print("\n  Key Points:")
        for kp in summary["key_points"]:
            print(f"    • {kp}")

    if summary["topics"]:
        print("\n  Topics:")
        for t in summary["topics"]:
            label = t.get("label", t) if isinstance(t, dict) else str(t)
            conf = t.get("confidence", "") if isinstance(t, dict) else ""
            conf_str = f" ({conf:.0%})" if conf else ""
            print(f"    • {label}{conf_str}")

    entities = summary.get("entities", {})
    for kind, items in entities.items():
        if items:
            print(f"\n  {kind.capitalize()}:")
            for item in items:
                print(f"    • {item}")

    if summary["questions_answered"]:
        print("\n  Questions Answered:")
        for q in summary["questions_answered"]:
            print(f"    Q: {q}")

    chunks = layer.context_chunks()
    print(f"\n  RAG chunks (4000 chars): {len(chunks)}")
    print("─────────────────────────────────────────\n")


def cmd_install(args):
    import platform
    if platform.system() != "Darwin":
        print("Error: 'andf install' is macOS only.", file=sys.stderr)
        sys.exit(1)
    from .installer import install
    target = getattr(args, "dir", "~/Applications")
    print("Building ANDF Viewer.app ...")
    app_path = install(target)
    print(f"Installed:  {app_path}")
    print()
    print("Double-click any .andf file in Finder to open it in your browser.")
    print("To uninstall: andf uninstall")


def cmd_uninstall(args):
    import platform
    if platform.system() != "Darwin":
        print("Error: 'andf uninstall' is macOS only.", file=sys.stderr)
        sys.exit(1)
    from .installer import uninstall
    target = getattr(args, "dir", "~/Applications")
    try:
        app_path = uninstall(target)
        print(f"Removed:    {app_path}")
        print(".andf file association cleared.")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="andf",
        description="ANDF — AI Native Document Format CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # new
    p_new = sub.add_parser("new", help="Create a blank ANDF document")
    p_new.add_argument("output", help="Output file path (e.g. doc.andf)")

    # open
    p_open = sub.add_parser("open", help="Open an ANDF file in the browser")
    p_open.add_argument("file", help="Path to .andf file")

    # parse
    p_parse = sub.add_parser("parse", help="Extract and print embedded JSON")
    p_parse.add_argument("file", help="Path to .andf file")
    p_parse.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    # validate
    p_val = sub.add_parser("validate", help="Validate ANDF format")
    p_val.add_argument("file", help="Path to .andf file")

    # info
    p_info = sub.add_parser("info", help="Show document metadata")
    p_info.add_argument("file", help="Path to .andf file")

    # ai
    p_ai = sub.add_parser("ai", help="Show AI layer summary")
    p_ai.add_argument("file", help="Path to .andf file")

    # install (macOS only)
    p_install = sub.add_parser(
        "install",
        help="(macOS) Install ANDF Viewer.app — registers .andf as a file type",
    )
    p_install.add_argument(
        "--dir", default="~/Applications",
        help="Where to install the app (default: ~/Applications)",
    )

    # uninstall (macOS only)
    p_uninstall = sub.add_parser(
        "uninstall",
        help="(macOS) Remove ANDF Viewer.app and deregister .andf",
    )
    p_uninstall.add_argument(
        "--dir", default="~/Applications",
        help="Where the app was installed (default: ~/Applications)",
    )

    args = parser.parse_args()
    dispatch = {
        "new": cmd_new,
        "open": cmd_open,
        "parse": cmd_parse,
        "validate": cmd_validate,
        "info": cmd_info,
        "ai": cmd_ai,
        "install": cmd_install,
        "uninstall": cmd_uninstall,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
