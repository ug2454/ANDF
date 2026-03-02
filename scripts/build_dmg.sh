#!/bin/bash
# build_dmg.sh — Build a distributable ANDF Viewer.dmg
#
# Produces: dist/ANDF-Viewer-1.0.dmg
#
# What the DMG contains:
#   ANDF Viewer.app  — double-click installer (user drags to Applications)
#   Install ANDF.command — double-click to register .andf file type
#   README.txt
#
# The .app itself embeds the Python helper using the system python3
# (/usr/bin/python3) which ships on every macOS 12+ machine.
# No Python installation required by the end user.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST="$ROOT/dist"
DMG_NAME="ANDF-Viewer-1.0"
STAGING="$DIST/dmg_staging"
APP_NAME="ANDF Viewer.app"

echo "── Building ANDF Viewer.app ────────────────────────"
python3 -c "
import sys; sys.path.insert(0, '$ROOT')
from andf.installer import install
app = install('$STAGING')
print('  App built:', app)
"

echo "── Writing installer command ───────────────────────"
cat > "$STAGING/Install ANDF.command" << 'INSTALL_EOF'
#!/bin/bash
# Double-click this to register .andf with Launch Services.
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
APP_DIR="$(dirname "$0")"
"$LSREGISTER" -f "$APP_DIR/ANDF Viewer.app"
osascript -e 'display dialog "ANDF Viewer registered!" & return & return & "You can now double-click .andf files to open them." with title "ANDF Viewer" buttons {"OK"} default button "OK"'
INSTALL_EOF
chmod +x "$STAGING/Install ANDF.command"

echo "── Writing README ──────────────────────────────────"
cat > "$STAGING/README.txt" << 'README_EOF'
ANDF Viewer 1.0
═══════════════

INSTALL
  1. Drag "ANDF Viewer.app" to your Applications folder.
  2. Double-click "Install ANDF.command" to register .andf as a file type.

After installation, double-clicking any .andf file opens it in your
browser — exactly like a PDF.

UNINSTALL
  Delete ANDF Viewer.app from Applications.

DEVELOPER
  pip install andf
  andf --help

  https://github.com/andf-format/andf
README_EOF

echo "── Creating DMG ────────────────────────────────────"
mkdir -p "$DIST"
DMG_PATH="$DIST/$DMG_NAME.dmg"

# Remove previous build
[ -f "$DMG_PATH" ] && rm "$DMG_PATH"

hdiutil create \
    -volname "ANDF Viewer" \
    -srcfolder "$STAGING" \
    -ov \
    -format UDZO \
    "$DMG_PATH"

echo ""
echo "✓ Built: $DMG_PATH"
echo "  Size:  $(du -sh "$DMG_PATH" | cut -f1)"
echo ""
echo "End users:"
echo "  1. Open the DMG"
echo "  2. Drag ANDF Viewer.app → Applications"
echo "  3. Double-click 'Install ANDF.command'"
echo "  4. Double-click any .andf file"
echo ""
echo "Developers: pip install andf"
