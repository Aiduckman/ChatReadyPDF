# Contributing

Thanks for wanting to improve this project.

## Local development

This is a static HTML app. You can open `index.html` directly, but a local web server is recommended:

```bash
python3 -m http.server 8080
```

Then visit `http://localhost:8080`.

## Suggested improvements

- Vendor PDF.js, JSZip, Tesseract.js, and OCR language data for offline use
- Add automated browser tests
- Improve multi-column and table extraction
- Add OCR progress per page
- Add drag-and-drop folder support
- Add optional Markdown cleanup

## Pull request checklist

- Keep the app usable as a static site
- Avoid uploading user files to a server
- Test at least one digital PDF, one scanned PDF, and one image file
- Update the README if behavior changes
