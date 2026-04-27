# PDF OCR Text Converter

A small, browser-based tool that converts PDFs and images into plain text.

It extracts embedded PDF text with PDF.js and can use OCR for scanned PDFs or photos of text through Tesseract.js. It runs as a static web page, so you can host it on GitHub Pages, Netlify, Vercel, or open it locally in a browser.

## Features

- Convert normal PDFs with selectable page ranges
- OCR scanned PDFs by rendering pages to canvas first
- OCR image files such as PNG, JPG/JPEG, WEBP, BMP, and TIFF
- Auto OCR fallback for pages with little or no embedded text
- Force OCR mode for fully scanned documents
- Multi-language OCR using Tesseract language codes such as `eng`, `fra`, `deu`, `ell`, or `eng+ell`
- Batch queue with per-file progress
- Download individual `.txt` / `.md` files or export everything as a `.zip`
- No server-side processing by this project

## Privacy note

Your selected files are processed in your browser by this page. The app does not upload your PDFs or images to a server controlled by this project.

However, the default version loads PDF.js, JSZip, Tesseract.js, and OCR language data from public CDNs. For sensitive/offline use, vendor those dependencies locally and update the script URLs in `index.html`.

## Quick start

Open `index.html` in a modern browser.

For best results, especially with OCR workers, serve it from a local web server:

```bash
python3 -m http.server 8080
```

Then open:

```text
http://localhost:8080
```

## Deploy to GitHub Pages

1. Create a new GitHub repository.
2. Upload these project files.
3. Go to **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**.
5. Select the `main` branch and root folder `/`.
6. Save. GitHub will give you a public URL.

More details are in [`docs/GITHUB_PAGES.md`](docs/GITHUB_PAGES.md).

## OCR tips

- Use clear, high-contrast scans or photos.
- For Greek, use `ell`; for English + Greek, use `eng+ell`.
- Increase OCR scale for sharper recognition, but expect slower processing.
- Use **Text layer only** for normal digital PDFs when speed matters.
- Use **Force OCR every page** for image-only/scanned PDFs.

## Limitations

- OCR can be slow on large PDFs.
- Complex layouts, columns, tables, rotated text, handwriting, and low-quality photos may produce imperfect text.
- The tool does not currently preserve exact table structure.
- Tesseract.js does not read PDF files directly; this app renders PDF pages to canvas first, then runs OCR on those images.

## Project structure

```text
pdf-ocr-text-converter/
├── index.html
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .gitignore
├── .nojekyll
└── docs/
    └── GITHUB_PAGES.md
```

## License

MIT. See [`LICENSE`](LICENSE).
