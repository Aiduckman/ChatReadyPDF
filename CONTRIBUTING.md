# Contributing

Thanks for wanting to improve PDF Text Extractor.

## Local development

The app is a single-file PyQt6 + PyMuPDF Python script. The fastest iteration loop is:

```bash
chmod +x run.sh
./run.sh
```

`run.sh` installs PyMuPDF and PyQt6 into your current Python environment and launches `pdf_text_extractor.py`. You don't need to rebuild the `.app` while iterating — just re-run.

For a clean Python sandbox that won't pollute your system:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python pdf_text_extractor.py
```

## Rebuilding the distributable .app

```bash
cd build_app
./build_app.sh
```

Output lands in `dist/PDFTextExtractor.app`. See the [README](README.md) for details on what the script does and how to ship the result.

## Suggested improvements

- **OCR fallback** for scanned PDFs (using `tesseract` / `pytesseract`) so users aren't stuck with "No extractable text found"
- **Universal2 build** so a single `.app` runs on both Apple Silicon and Intel
- **Apple notarization** in `build_app.sh` so clients skip the right-click → Open step
- **Multi-column / table** extraction quality (PyMuPDF supports `get_text("dict")` for richer layouts)
- **Export to Markdown** with preserved structure
- **Batch export** — drop a folder, get a folder of `.txt` files
- **Windows / Linux** builds via the same PyInstaller spec (small tweaks needed)

## Pull request checklist

- The app still launches and opens at least one digital PDF correctly
- `cd build_app && ./build_app.sh` still produces a working `dist/PDFTextExtractor.app`
- Update `README.md` if user-facing behavior changes
- Update `CHANGELOG.md` with a one-line entry
- Don't commit `dist/`, `build_app/.venv/`, `build_app/build/`, `__pycache__/`, or `.DS_Store` — these are gitignored
