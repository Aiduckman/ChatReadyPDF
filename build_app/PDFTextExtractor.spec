# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PDF Text Extractor.

Builds a self-contained macOS .app bundle that includes Python, PyQt6,
and PyMuPDF — clients only need to drag the .app to /Applications.

Build with:
    pyinstaller --noconfirm PDFTextExtractor.spec

(Or just run `./build_app.sh` which handles the venv + deps.)
"""

import os
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
SPEC_DIR    = Path(SPECPATH).resolve()           # build_app/
PROJECT_DIR = SPEC_DIR.parent                    # pdf-text-extractor/
SCRIPT      = str(PROJECT_DIR / "pdf_text_extractor.py")
ICON_PNG    = PROJECT_DIR / "AppIcon.png"
ICON_ICNS   = SPEC_DIR / "AppIcon.icns"

# Prefer .icns if present; fall back to .png (PyInstaller converts).
if ICON_ICNS.exists():
    icon_path = str(ICON_ICNS)
elif ICON_PNG.exists():
    icon_path = str(ICON_PNG)
else:
    icon_path = None

# ── Analysis ─────────────────────────────────────────────────────────────────
a = Analysis(
    [SCRIPT],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # PyMuPDF
        "fitz",
        "fitz._fitz",
        # PyQt6 modules actually used by the app
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.sip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Trim modules we don't ship to keep the bundle small.
    excludes=[
        "tkinter",
        "test",
        "unittest",
        "pydoc",
        "pdb",
        "doctest",
        "PyQt6.QtNetwork",
        "PyQt6.QtQml",
        "PyQt6.QtQuick",
        "PyQt6.QtMultimedia",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebChannel",
        "PyQt6.QtSql",
        "PyQt6.QtTest",
        "PyQt6.QtBluetooth",
        "PyQt6.QtPositioning",
        "PyQt6.QtSensors",
        "PyQt6.QtSerialPort",
        "PyQt6.QtNfc",
        "PyQt6.QtRemoteObjects",
        "PyQt6.Qt3DCore",
        "PyQt6.Qt3DRender",
        "PyQt6.Qt3DInput",
        "PyQt6.Qt3DLogic",
        "PyQt6.Qt3DAnimation",
        "PyQt6.Qt3DExtras",
        "PyQt6.QtCharts",
        "PyQt6.QtDataVisualization",
        "matplotlib",
        "numpy.tests",
        "scipy",
        "pandas",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

# ── Executable inside the .app ───────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PDFTextExtractor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,                  # GUI app — no terminal window
    disable_windowed_traceback=False,
    argv_emulation=True,            # Receive Finder "Open With" file paths via sys.argv
    target_arch=None,               # Build for the host arch (universal2 needs universal Python)
    codesign_identity=None,         # Unsigned — clients right-click → Open the first time
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="PDFTextExtractor",
)

# ── macOS .app bundle ────────────────────────────────────────────────────────
app = BUNDLE(
    coll,
    name="PDFTextExtractor.app",
    icon=icon_path,
    bundle_identifier="com.geev.pdftextextractor",
    version="2.1.0",
    info_plist={
        "CFBundleName": "PDF Text Extractor",
        "CFBundleDisplayName": "PDF Text Extractor",
        "CFBundleShortVersionString": "2.1.0",
        "CFBundleVersion": "2.1.0",
        "CFBundleIdentifier": "com.geev.pdftextextractor",
        "CFBundleExecutable": "PDFTextExtractor",
        "CFBundlePackageType": "APPL",
        "LSMinimumSystemVersion": "11.0",
        "LSApplicationCategoryType": "public.app-category.productivity",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,   # supports Dark Mode
        "NSHumanReadableCopyright": "© 2026 Geev. MIT License.",
        # File-association: drop / "Open With" PDF support
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeName": "PDF Document",
                "CFBundleTypeRole": "Viewer",
                "LSHandlerRank": "Alternate",
                "LSItemContentTypes": ["com.adobe.pdf"],
            }
        ],
    },
)
