# Changelog

## 2.1.0 — Windows support

**Added**
- `windows/` folder with a Windows build of the same app: PyInstaller spec, `build_app.bat`, version-info resource, and a multi-resolution `AppIcon.ico` generated from `AppIcon.png`.
- Single-file `PDFTextExtractor.exe` output (~80 MB), no install required.
- `.github/workflows/build-windows.yml` — pushing a `v*` tag now auto-builds the `.exe` on a Windows runner and attaches it to the matching GitHub Release.
- README documents the Windows install path (download the `.exe`, double-click, "Run anyway" on first launch) alongside the existing macOS instructions.

**Notes**
- The same `pdf_text_extractor.py` runs on both platforms — it already branches font choices (`SF Pro Text` vs `Segoe UI`) on `sys.platform`. No source changes were needed for Windows compatibility.

## 2.0.0 — Native macOS app

This is a full pivot. The previous browser-based PDF + OCR converter (PDF.js + Tesseract.js, hosted on GitHub Pages) has been replaced with a native macOS desktop app that runs **fully offline**, with **no Python, Node, or Terminal required** for clients.

**Added**
- Native macOS app (PyQt6 + PyMuPDF) bundled into a self-contained `.app` via PyInstaller
- One-command `build_app/build_app.sh` that produces a shippable `PDFTextExtractor.app` from a clean checkout
- Multi-file sidebar with switch-between-docs UX
- Drag-and-drop PDF support directly on the window
- ⌘F search with yellow-highlight matching
- ⌘O / ⇧⌘C / ⌘S / ⌘W keyboard shortcuts
- Page markers in extracted text for easy navigation
- Automatic Dark Mode following system appearance
- Background PDF loading so large docs don't freeze the UI
- App icon (programmatic + `AppIcon.png` source)
- SwiftUI/PDFKit alternative implementation in `SwiftUI_Xcode/` for a fully-native zero-dependency build
- macOS file-association metadata (Open With → PDF Text Extractor)

**Removed**
- The browser-based static site (`index.html`, `package.json`, `docs/GITHUB_PAGES.md`)
- Tesseract.js OCR (the new native app focuses on text-layer extraction; OCR fallback is on the roadmap)

## 1.0.0

Initial shareable GitHub project release.

- PDF text-layer extraction
- OCR fallback for scanned PDFs
- OCR for common image formats
- Batch queue
- Individual text downloads
- ZIP export
- GitHub Pages-ready static app
