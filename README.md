# Kaleido

Most news apps show you more of what you already agree with. Kaleido does the opposite. When you're reading a news article, it surfaces coverage of the same story from outlets with a different point of view, so you can see how the story looks from more than one side. Kaleido browser extension that shows readers alternate-perspective coverage of the news article they're currently viewing.

## How it works

1. A browser extension detects when you're reading a news article
2. The backend looks up related coverage of the same story from other outlets
3. Articles are filtered so you see perspectives *different* from the one you're currently reading (e.g. reading a right-leaning article surfaces left-leaning and center coverage instead)

## Status

This is a work-in-progress learning project. Currently implemented:

- ✅ FastAPI backend with request/response validation via Pydantic
- ✅ Outlet-level bias lookup (`services/bias_lookup.py`)
- ✅ Contrast-selection logic that filters out same-bias articles (`services/contrast_selector.py`)
- 🔲 Real article retrieval — currently returns hardcoded fake articles; a vector DB + ingestion pipeline is planned
- 🔲 Per-article bias scoring via an ML model (as opposed to today's per-outlet static lookup)
- ✅ Browser extension (manifest, content script, popup)

## Project structure

```
main.py                          # FastAPI app and routes
models.py                        # Pydantic models (request/response schemas)
services/
  bias_lookup.py                 # Outlet -> bias label lookup (static table)
  bias_classifier.py             # Classify article (left/center/right) using pretrained HuggingFace model
  contrast_selector.py           # Filters related articles to show contrasting perspectives
extension/
  manifest.json                  # Extension config — permissions, popup/content-script/background registration
  detect-article.js              # Content script: detects if the current page is a news article, extracts (title, url, description)
  service-worker.js              # Background script: stores the detected article per tab, relays it to the popup on request
  icon/
    icon.png                     # Toolbar/extensions-page icon (single image, scaled by Chrome for all sizes)
  popup/
    popup.html                   # Popup UI shown when the toolbar icon is clicked
    popup.css                    # Dark-themed styling for the popup (bias chips, confidence bars)
    popup.js                     # Fetches the detected article, calls the backend, renders results
```

## Running locally

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync
uv run uvicorn main:app --reload
```

Then visit:
- `http://127.0.0.1:8000/health` — basic health check
- `http://127.0.0.1:8000/docs` — interactive API docs (Swagger UI) for testing endpoints


### Extension
 
The backend must be running locally (previous step) before the extension can fetch results.
 
1. Open `chrome://extensions` in Chrome
2. Enable **Developer mode** (toggle, top right)
3. Click **Load unpacked** and select the `extension/` folder (contains manifest.json)
4. Visit any news article, then click the extension icon in the toolbar
5. To pick up changes to any extension file, click the refresh icon on the extension's card in `chrome://extensions`

## License

MIT
