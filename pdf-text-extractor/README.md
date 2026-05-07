# PDF Text Extractor

A beautiful, **100% offline** macOS desktop app for extracting text from PDF files.

---

## Quick Start (Python — runs today, no Xcode needed)

```bash
cd PDFTextExtractor
chmod +x run.sh
./run.sh
```

`run.sh` automatically installs the two required packages (PyMuPDF + PyQt6) then
launches the app. You only need **Python 3.9+** — which comes pre-installed on
macOS 12+, or install from [python.org](https://www.python.org/downloads/).

Open specific files directly from the terminal:
```bash
./run.sh ~/Documents/report.pdf
```

### Manual install

```bash
pip install PyMuPDF PyQt6
python3 pdf_text_extractor.py
```

---

## Features

| Feature | Description |
|---|---|
| **Drag & Drop** | Drop PDFs directly onto the window |
| **Open dialog** | ⌘O — open one or many PDFs at once |
| **Multi-file sidebar** | Switch between docs instantly |
| **Page markers** | Text is split by page for easy navigation |
| **Search** | ⌘F — highlights all matches in yellow |
| **Copy text** | ⇧⌘C — copy all extracted text to clipboard |
| **Save as .txt** | ⌘S — save extracted text as a plain-text file |
| **Remove file** | ⌘W — remove current doc from the list |
| **Show in Finder** | Right-click any sidebar item |
| **Dark mode** | Automatically follows system appearance |
| **Background loading** | Large PDFs load without freezing the UI |

---

## SwiftUI / Xcode Version (bonus — best native look)

The `SwiftUI_Xcode/` folder contains a fully written **SwiftUI + PDFKit** app.
PDFKit is built into macOS — no dependencies at all.

### How to use it

1. Open **Xcode** → File → New → Project → macOS → App
2. Name it `PDFTextExtractor`, set Interface to **SwiftUI**, Language to **Swift**
3. Delete the auto-generated `ContentView.swift`
4. Drag **all four `.swift` files** from `SwiftUI_Xcode/` into the Xcode project
5. Press **⌘R** to build and run

Requires Xcode 14+ and macOS 13+.

---

## Files

```
PDFTextExtractor/
├── pdf_text_extractor.py   ← Main Python app (run this)
├── requirements.txt        ← PyMuPDF + PyQt6
├── run.sh                  ← One-click launcher & installer
└── SwiftUI_Xcode/          ← Bonus: native SwiftUI source files
    ├── PDFTextExtractorApp.swift
    ├── DocumentStore.swift
    ├── ContentView.swift
    ├── SidebarView.swift
    └── TextDetailView.swift
```

---

## How it works

PDF text extraction uses **PyMuPDF** (the `fitz` library), one of the fastest and
most accurate PDF parsing libraries available. It extracts the actual text layer
embedded in the PDF — no OCR needed for standard PDFs. Scanned-only PDFs without
an embedded text layer will show "(No extractable text found)".

The SwiftUI version uses Apple's **PDFKit** framework, which ships with macOS and
does the same thing natively.

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| ⌘O | Open PDF(s) |
| ⌘F | Show search bar |
| Escape | Close search bar |
| ⇧⌘C | Copy extracted text |
| ⌘S | Save as .txt |
| ⌘W | Remove current file |
