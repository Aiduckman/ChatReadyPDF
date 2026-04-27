# Deploying to GitHub Pages

This project is a static site. No build step is required.

## Option A: Upload through the browser

1. Create a new repository on GitHub.
2. Click **Add file → Upload files**.
3. Upload all files from this folder.
4. Commit the files to `main`.
5. Go to **Settings → Pages**.
6. Select **Deploy from a branch**.
7. Choose branch `main` and folder `/root` or `/` depending on GitHub's wording.
8. Click **Save**.

Your site will usually be available at:

```text
https://YOUR_USERNAME.github.io/YOUR_REPOSITORY_NAME/
```

## Option B: Use Git locally

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git push -u origin main
```

Then enable Pages in **Settings → Pages**.

## Important privacy/dependency note

The app processes files in the browser, but the default `index.html` loads JavaScript libraries and OCR language data from CDNs. For fully offline or sensitive use, download those dependencies into a local `vendor/` folder and update the script URLs.
