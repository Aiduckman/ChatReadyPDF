# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PDF Text Extractor — Windows.

Builds a single self-contained PDFTextExtractor.exe (~80 MB). Clients
double-click to run; Python, PyQt6, and PyMuPDF are all bundled inside.

Build with:
    pyinstaller --noconfirm PDFTextExtractor_win.spec

(Or just run `build_app.bat` which handles the venv + deps.)
"""

import os
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
SPEC_DIR    = Path(SPECPATH).resolve()           # windows/
PROJECT_DIR = SPEC_DIR.parent                    # repo root
SCRIPT      = str(PROJECT_DIR / "pdf_text_extractor.py")
ICON_ICO    = SPEC_DIR / "AppIcon.ico"
icon_path   = str(ICON_ICO) if ICON_ICO.exists() else None

# ── Analysis ─────────────────────────────────────────────────────────────────
a = Analysis(
    [SCRIPT],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # PyMuPDF
        "fitz",
        # PyQt6 modules used by the app
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.sip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Trim modules we don't ship to keep the .exe small.
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

# ── One-file Windows EXE ─────────────────────────────────────────────────────
# By passing a.binaries + a.datas + a.zipfiles into EXE() (instead of using a
# separate COLLECT() step), PyInstaller produces a single self-extracting .exe.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PDFTextExtractor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                        # UPX often trips antivirus heuristics
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                    # GUI app — no terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
    # Windows version-info (shows in File Explorer → Properties → Details)
    version="version_info.txt" if (SPEC_DIR / "version_info.txt").exists() else None,
)
