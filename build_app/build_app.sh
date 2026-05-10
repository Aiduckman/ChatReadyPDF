#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  PDF Text Extractor — one-command .app builder
#
#  Produces a self-contained macOS .app bundle (no Python required on the
#  client machine). Output: ../dist/PDFTextExtractor.app
#
#  Usage:
#      cd build_app
#      ./build_app.sh
#
#  The first run is slow (it downloads PyQt6 + PyMuPDF + PyInstaller into a
#  local virtualenv at .venv/). Re-runs use the cached venv.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Resolve paths ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SPEC="$SCRIPT_DIR/PDFTextExtractor.spec"
VENV="$SCRIPT_DIR/.venv"
DIST="$PROJECT_DIR/dist"
WORK="$SCRIPT_DIR/build"

if [[ ! -f "$SPEC" ]]; then
    echo "❌  Spec file not found: $SPEC"
    exit 1
fi

# ── Pick Python ──────────────────────────────────────────────────────────────
# Prefer Homebrew 3.12 (best PyQt6 wheel availability), fall back to 3.11/3.10.
choose_python() {
    for cand in python3.12 python3.11 python3.10 python3; do
        if command -v "$cand" >/dev/null 2>&1; then
            local ver
            ver=$("$cand" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            local maj=${ver%.*} min=${ver#*.}
            if [[ $maj -eq 3 && $min -ge 10 && $min -le 12 ]]; then
                echo "$cand"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON=$(choose_python || true)
if [[ -z "$PYTHON" ]]; then
    echo "❌  Need Python 3.10, 3.11, or 3.12 (PyQt6 wheels). Install via:"
    echo "       brew install python@3.12"
    exit 1
fi
echo "✓  Using $($PYTHON --version) ($PYTHON)"

# ── Create / refresh venv ────────────────────────────────────────────────────
# A venv hardcodes its own absolute path inside bin/activate. If the project
# directory got moved/renamed, the old activate file points at a non-existent
# path and `pip` won't be on $PATH after sourcing it. Detect that and rebuild.
venv_is_stale() {
    [[ -f "$VENV/bin/activate" ]] || return 0
    grep -q "^export VIRTUAL_ENV=\"\?${VENV}\"\?\$" "$VENV/bin/activate" && return 1
    return 0
}

if [[ ! -d "$VENV" ]]; then
    echo "📦  Creating build venv at $VENV"
    "$PYTHON" -m venv "$VENV"
elif venv_is_stale; then
    echo "♻️   Existing venv was created at a different path — rebuilding."
    rm -rf "$VENV"
    "$PYTHON" -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "📦  Upgrading pip + installing build deps…"
pip install --quiet --upgrade pip wheel
pip install --quiet --upgrade \
    "PyMuPDF>=1.24.0" \
    "PyQt6>=6.6.0" \
    "pyinstaller>=6.6.0"

# ── (Optional) generate .icns from AppIcon.png for a sharper Finder icon ────
ICON_PNG="$PROJECT_DIR/AppIcon.png"
ICON_ICNS="$SCRIPT_DIR/AppIcon.icns"
if [[ -f "$ICON_PNG" && ! -f "$ICON_ICNS" ]] && command -v sips >/dev/null && command -v iconutil >/dev/null; then
    echo "🎨  Generating AppIcon.icns from AppIcon.png…"
    ICONSET="$SCRIPT_DIR/AppIcon.iconset"
    rm -rf "$ICONSET"
    mkdir -p "$ICONSET"
    for size in 16 32 64 128 256 512; do
        sips -z "$size" "$size" "$ICON_PNG" --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
        sips -z $((size*2)) $((size*2)) "$ICON_PNG" --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
    done
    iconutil -c icns "$ICONSET" -o "$ICON_ICNS"
    rm -rf "$ICONSET"
fi

# ── Clean previous build artifacts ───────────────────────────────────────────
echo "🧹  Cleaning previous build…"
rm -rf "$DIST" "$WORK"
mkdir -p "$DIST"

# ── Run PyInstaller ──────────────────────────────────────────────────────────
echo "🔨  Building PDFTextExtractor.app… (this takes a minute)"
cd "$SCRIPT_DIR"
pyinstaller \
    --noconfirm \
    --clean \
    --workpath "$WORK" \
    --distpath "$DIST" \
    "$SPEC"

# ── Strip code signature so the app is portable to other Macs ────────────────
APP="$DIST/PDFTextExtractor.app"
if [[ -d "$APP" ]]; then
    echo "🔐  Removing ad-hoc signature for portability (clients will right-click → Open the first time)…"
    # Re-sign with --force --deep using ad-hoc identity. This makes the binary
    # runnable on Apple Silicon and Intel without quarantine surprises locally.
    codesign --force --deep --sign - "$APP" 2>/dev/null || true
fi

# ── Cleanup intermediate folders ─────────────────────────────────────────────
rm -rf "$WORK"
rm -rf "$DIST/PDFTextExtractor"   # the unbundled COLLECT folder PyInstaller also writes

# ── Report ───────────────────────────────────────────────────────────────────
if [[ -d "$APP" ]]; then
    SIZE=$(du -sh "$APP" | awk '{print $1}')
    echo ""
    echo "─────────────────────────────────────────────────────────────────────"
    echo "✅  Build succeeded"
    echo "    .app:    $APP"
    echo "    Size:    $SIZE"
    echo "─────────────────────────────────────────────────────────────────────"
    echo ""
    echo "Next steps:"
    echo "  • Test it:        open \"$APP\""
    echo "  • Ship it:        zip the .app and send to clients."
    echo "  • Clients run it: drag PDFTextExtractor.app to /Applications,"
    echo "                    then right-click → Open the first time"
    echo "                    (unsigned app — Gatekeeper bypass)."
    echo ""
else
    echo "❌  Build failed — no .app produced. See PyInstaller output above."
    exit 1
fi
