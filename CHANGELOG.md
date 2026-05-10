# Changelog

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
