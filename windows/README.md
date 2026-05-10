# PDF Text Extractor — Windows build

This folder contains everything needed to produce a Windows `PDFTextExtractor.exe` from the same `pdf_text_extractor.py` source as the macOS build.

## For end users

You don't need anything in this folder. Just grab `PDFTextExtractor.exe` from the [latest Release](https://github.com/Aiduckman/ChatReadyPDF/releases/latest), double-click to run, and click "Run anyway" the first time SmartScreen complains (unsigned app — one-time bypass).

> **Requires Windows 10 (1809) or newer, x64.**

## For developers — building locally

### One command (Windows)

```cmd
cd windows
build_app.bat
```

The script:

- Picks Python 3.10, 3.11, or 3.12 (via the `py` launcher or `python` on PATH)
- Creates an isolated build venv at `windows\.venv\`
- Installs **PyInstaller**, **PyQt6**, and **PyMuPDF**
- Runs PyInstaller against `PDFTextExtractor_win.spec`
- Outputs `windows\dist\PDFTextExtractor.exe` (~80 MB, single file)

First run takes ~2 minutes (downloads ~150 MB of build deps). Subsequent rebuilds reuse the cached venv and finish in ~30 seconds.

### Requirements

- Windows 10/11 x64
- Python 3.10, 3.11, or 3.12 — install from [python.org](https://www.python.org/downloads/) and check **"Add python.exe to PATH"** during install
- ~500 MB free disk for the build venv

### Building via GitHub Actions instead

The repo includes `.github/workflows/build-windows.yml`. Push a tag like `v2.1.0` and CI will build the `.exe` on a Windows runner and attach it to the matching GitHub Release automatically — no Windows machine required.

## Files

```
windows/
├── PDFTextExtractor_win.spec   ← PyInstaller config (single-file .exe, GUI mode)
├── version_info.txt            ← Windows VERSIONINFO resource for the .exe
├── build_app.bat               ← One-command builder
├── AppIcon.ico                 ← Multi-resolution Windows icon
└── dist/
    └── PDFTextExtractor.exe    ← Build output (gitignored)
```

## Notes

- **Single-file mode** — On launch the bundled .exe extracts itself to `%TEMP%\_MEI*` and runs from there. First launch is ~3 seconds slower than a folder build, but you ship one tidy file.
- **No code signing** — Clients see a SmartScreen warning the first time. To make that go away, sign the `.exe` with a code-signing certificate (~$200–400/year for an OV cert). Hook it in by adding the signing step at the end of `build_app.bat` or as a workflow step in CI.
- **Antivirus false positives** — PyInstaller's bootloader is sometimes flagged by overzealous AV vendors. The fix is the same as code signing — a signed binary almost never trips heuristics. UPX compression is disabled in the spec because it amplifies these false positives.
- **The same `pdf_text_extractor.py` runs on both macOS and Windows.** It already branches font choices on `sys.platform`, so the UI uses Segoe UI / Consolas on Windows automatically.
