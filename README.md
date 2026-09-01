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
- 🔲 Browser extension (manifest, content script, popup)

## Project structure

```
main.py                          # FastAPI app and routes
models.py                        # Pydantic models (request/response schemas)
services/
  bias_lookup.py                 # Outlet -> bias label lookup (static table)
  contrast_selector.py           # Filters related articles to show contrasting perspectives
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

## License

MIT
