#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  PDF Text Extractor — launcher script
#  Installs dependencies (once) then launches the app.
#
#  Usage:
#    chmod +x run.sh    (first time only)
#    ./run.sh
#
#  To open specific PDFs immediately:
#    ./run.sh ~/Documents/report.pdf invoice.pdf
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$SCRIPT_DIR/pdf_text_extractor.py"
REQS="$SCRIPT_DIR/requirements.txt"

# ── Locate python3 ───────────────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
    PYTHON=python3
else
    echo "❌  python3 not found."
    echo "    Please install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi

PY_VER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$("$PYTHON" -c "import sys; print(sys.version_info.major)")
PY_MINOR=$("$PYTHON" -c "import sys; print(sys.version_info.minor)")

if [[ "$PY_MAJOR" -lt 3 ]] || [[ "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 9 ]]; then
    echo "❌  Python $PY_VER found, but 3.9+ is required."
    exit 1
fi

echo "✓  Python $PY_VER"

# ── Install / upgrade dependencies ────────────────────────────────────────────
echo "📦  Checking dependencies…"

INSTALL_FLAGS="--quiet --upgrade"
# On macOS system Python or Homebrew, --break-system-packages may be needed
"$PYTHON" -m pip install $INSTALL_FLAGS -r "$REQS" 2>/dev/null || \
"$PYTHON" -m pip install $INSTALL_FLAGS --break-system-packages -r "$REQS" || {
    echo ""
    echo "⚠️   pip install failed. Trying with --user flag…"
    "$PYTHON" -m pip install $INSTALL_FLAGS --user -r "$REQS"
}

echo "✅  Dependencies ready"
echo ""
echo "🚀  Launching PDF Text Extractor…"
echo ""

# ── Launch ────────────────────────────────────────────────────────────────────
exec "$PYTHON" "$APP" "$@"
