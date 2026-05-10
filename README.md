# PDF Text Extractor

A beautiful, **100% offline** desktop app for extracting text from PDF files. Available for **macOS** and **Windows**.

Save your token usage in LLMs by converting your PDFs to `.txt` files. You can also combine it with my document anonymization tool for 100% anonymity on LLMs (and EU GDPR compliance).

![UI preview](ui_preview.png)

---

## For users — install in 30 seconds

Grab the build for your OS from the [latest Release](https://github.com/Aiduckman/ChatReadyPDF/releases/latest):

### macOS — `PDFTextExtractor.zip`

1. Download `PDFTextExtractor.zip` and unzip it (Finder unzips automatically on double-click).
2. Drag **PDFTextExtractor.app** into your **Applications** folder.
3. The very first time you launch it: **right-click the app → Open**, then click **Open** in the dialog.
   *(macOS shows that warning for any app that isn't notarized by Apple. It's a one-time click — after that it opens normally from Launchpad/Spotlight.)*

> **Requires macOS 11 (Big Sur) or newer, Apple Silicon or Intel.**

### Windows — `PDFTextExtractor.exe`

1. Download `PDFTextExtractor.exe`.
2. Double-click it.
3. The first time, Windows SmartScreen may show **"Windows protected your PC"** — click **More info** → **Run anyway**. *(One-time bypass for any unsigned app.)*

> **Requires Windows 10 (1809) or newer, x64.**

That's it on either platform. No Python, no Terminal, no `pip install`. The app is fully self-contained and runs entirely offline — your PDFs never leave your computer.

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

### Keyboard shortcuts

| Shortcut | Action |
|---|---|
| ⌘O | Open PDF(s) |
| ⌘F | Show search bar |
| Escape | Close search bar |
| ⇧⌘C | Copy extracted text |
| ⌘S | Save as .txt |
| ⌘W | Remove current file |

---

## For developers — building the apps

The same `pdf_text_extractor.py` source compiles to both platforms. You only need this section if you're rebuilding the binary yourself.

### macOS .app — one command

```bash
cd build_app
./build_app.sh
```

Outputs `dist/PDFTextExtractor.app` (~120 MB). First run takes ~1–2 minutes (downloads PyQt6 + PyMuPDF + PyInstaller into `build_app/.venv/`); rebuilds take ~20 seconds. Requires macOS 11+ with Command Line Tools and Homebrew Python 3.10–3.12.

### Windows .exe — one command

On a Windows machine:

```cmd
cd windows
build_app.bat
```

Outputs `windows\dist\PDFTextExtractor.exe` (single self-contained file, ~80 MB). Requires Python 3.10–3.12 from [python.org](https://www.python.org/downloads/) with **"Add python.exe to PATH"** checked. See [`windows/README.md`](windows/README.md) for details.

**Don't have a Windows machine?** Push a tag like `v2.1.0` and the [`build-windows.yml`](.github/workflows/build-windows.yml) GitHub Actions workflow builds the `.exe` on a Windows runner and attaches it to the matching Release automatically.

### Run from source instead (for quick iteration)

macOS:

```bash
chmod +x run.sh
./run.sh
```

Windows:

```cmd
pip install -r requirements.txt
python pdf_text_extractor.py
```

This installs PyMuPDF + PyQt6 into your active Python env and launches the script directly — handy while editing `pdf_text_extractor.py`.

---

## SwiftUI / Xcode version (alternative — fully native)

The `SwiftUI_Xcode/` folder contains a SwiftUI + PDFKit version of the app. PDFKit ships with macOS, so this version has zero runtime dependencies and the resulting binary is only ~2–5 MB.

To build it:

1. Open **Xcode** → File → New → Project → macOS → App
2. Name it `PDFTextExtractor`, set Interface to **SwiftUI**, Language to **Swift**
3. Delete the auto-generated `ContentView.swift`
4. Drag all four `.swift` files from `SwiftUI_Xcode/` into the project
5. Press **⌘R**

Requires Xcode 14+ and macOS 13+.

---

## How the Python version works

PDF text extraction uses **PyMuPDF** (the `fitz` library) — one of the fastest and most accurate PDF parsing libraries available. It pulls the actual text layer embedded in the PDF, so no OCR is needed for normal digital PDFs. Scanned-only PDFs without an embedded text layer will show "(No extractable text found)".

The SwiftUI version uses Apple's **PDFKit** framework, which ships with macOS and does the same thing natively.

---

## Distributing to clients

The release pipeline is intentionally boring. To cut a new release covering both platforms:

1. **Update the version** in `build_app/PDFTextExtractor.spec`, `windows/version_info.txt`, and `CHANGELOG.md`.
2. **Build and zip the macOS app:**

   ```bash
   cd build_app && ./build_app.sh
   cd ../dist && zip -ry PDFTextExtractor.zip PDFTextExtractor.app
   ```

3. **Tag and push:**

   ```bash
   git tag -a v2.1.1 -m "Release v2.1.1"
   git push origin v2.1.1
   ```

4. **GitHub Actions** automatically builds `PDFTextExtractor.exe` on a Windows runner and attaches it to the v2.1.1 Release.
5. **Upload the macOS zip** to the same Release:

   ```bash
   gh release upload v2.1.1 dist/PDFTextExtractor.zip
   ```

Clients then grab whichever file matches their OS from the Releases page.

> **Want to skip the SmartScreen / right-click→Open step on clients' machines?** That requires code signing — Apple notarization for macOS (~$99/yr Developer account) and an OV/EV code-signing certificate for Windows (~$200–400/yr). Both build scripts have clearly marked spots to plug those in.

---

## Repo layout

```
ChatReadyPDF/
├── pdf_text_extractor.py            ← Shared cross-platform app source
├── requirements.txt                 ← PyMuPDF + PyQt6
├── run.sh                           ← Run from source on macOS/Linux
├── AppIcon.png                      ← Source icon (used by both platforms)
├── ui_preview.png                   ← Screenshot for the README
├── generate_assets.py               ← Helper for regenerating screenshots
│
├── build_app/                       ← macOS build
│   ├── PDFTextExtractor.spec        ← PyInstaller config (.app bundle)
│   ├── build_app.sh                 ← One-command builder
│   ├── AppIcon.icns                 ← Generated by build_app.sh (gitignored)
│   └── .venv/                       ← Build venv (gitignored)
│
├── windows/                         ← Windows build
│   ├── PDFTextExtractor_win.spec    ← PyInstaller config (single .exe)
│   ├── version_info.txt             ← VERSIONINFO resource for the .exe
│   ├── build_app.bat                ← One-command builder
│   ├── AppIcon.ico                  ← Multi-resolution Windows icon
│   └── README.md                    ← Windows-specific build notes
│
├── .github/workflows/
│   └── build-windows.yml            ← Auto-builds .exe on tag push
│
├── dist/                            ← macOS build output (gitignored)
│   └── PDFTextExtractor.app
│
└── SwiftUI_Xcode/                   ← Alternative native macOS version
    ├── PDFTextExtractorApp.swift
    ├── DocumentStore.swift
    ├── ContentView.swift
    ├── SidebarView.swift
    └── TextDetailView.swift
```

---

## License

MIT. See [`LICENSE`](LICENSE).
