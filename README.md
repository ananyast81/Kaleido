# Kaleido

> **One event. Multiple perspectives. Better understanding.**

Most news apps show you more of what you already agree with. **Kaleido does the opposite.**

When you're reading a news article, Kaleido surfaces coverage of the same story from outlets with a different point of view, helping you understand how the same event is presented from multiple perspectives.

Kaleido is a browser extension that shows readers alternate-perspective coverage of the news article they are currently viewing.

---

## How It Works

1. A browser extension detects when you're reading a news article.
2. The detected article metadata is sent to the FastAPI backend.
3. The backend analyzes the article's political leaning using a pretrained Hugging Face model.
4. Related coverage is filtered so that the reader sees perspectives different from the article they are currently reading.
5. Article text can be processed, chunked, and converted into embeddings as part of the developing semantic-retrieval pipeline.

For example, reading a right-leaning article can surface left-leaning and center coverage.

---

## Semantic Processing Pipeline

Kaleido is being extended from a metadata-based prototype toward semantic article retrieval.

### Current Processing Flow

```text
Article
   ↓
Article Processing
   ↓
Sentence-Aware Chunking
   ↓
Embedding Generation
   ↓
Semantic Retrieval
```

The newly implemented processing components are:

- `services/article_processor.py` — prepares article content for downstream semantic processing.
- `services/chunker.py` — splits article text into smaller sentence-aware chunks.
- `services/embedding_service.py` — converts article chunks into numerical embeddings for semantic comparison.
- Tokenizer/chunking tests — validate the text-processing pipeline.

> Persistent vector storage, full semantic retrieval, and live-news ingestion are still under development.

---

## Status

This is a **work-in-progress learning project**.

### Implemented

- ✅ FastAPI backend with request/response validation via Pydantic
- ✅ Chrome Manifest V3 browser extension
- ✅ Automatic news article detection and metadata extraction
- ✅ Per-tab article storage through the background service worker
- ✅ Extension popup connected to the backend
- ✅ Outlet-level bias lookup (`services/bias_lookup.py`)
- ✅ Per-article political-leaning classification using a pretrained Hugging Face transformer model (`services/bias_classifier.py`)
- ✅ Contrast-selection logic that filters out same-bias articles (`services/contrast_selector.py`)
- ✅ Article processing pipeline (`services/article_processor.py`)
- ✅ Sentence-aware text chunking (`services/chunker.py`)
- ✅ Embedding generation (`services/embedding_service.py`)
- ✅ Tokenizer/chunking tests

### In Progress

- 🟡 Semantic retrieval pipeline  
  Article processing, chunking, and embedding generation are implemented, while persistent vector storage and complete retrieval are still being developed.

### Planned

- 🔲 Real live-news retrieval
- 🔲 Vector database integration
- 🔲 Retrieval-Augmented Generation (RAG) for multi-source comparison
- 🔲 Indian political/news classification
- 🔲 Broader multilingual support
- 🔲 Full Chrome Side Panel interface

---

## Current Classifier Scope

The pretrained political-leaning classifier currently focuses on **U.S. political/news context**.

Future development will extend the system to include:

- Indian news and political context
- Indian news outlets
- Broader language support
- Region-specific political framing
- More flexible political and perspective labels

---

## Project Structure

```text
Kaleido/
│
├── main.py
├── models.py
├── pyproject.toml
├── uv.lock
│
├── services/
│   ├── __init__.py
│   ├── bias_lookup.py
│   ├── bias_classifier.py
│   ├── contrast_selector.py
│   ├── article_processor.py
│   ├── chunker.py
│   └── embedding_service.py
│
├── extension/
│   ├── manifest.json
│   ├── detect-article.js
│   ├── service-worker.js
│   │
│   ├── icon/
│   │   └── icon.png
│   │
│   └── popup/
│       ├── popup.html
│       ├── popup.css
│       └── popup.js
│
├── test/
│   └── test_tokenizer.py
│
└── test_tokenizer.py
```

### Main Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI application and API routes |
| `models.py` | Pydantic request and response schemas |
| `pyproject.toml` | Project dependencies and configuration |
| `uv.lock` | Locked dependency versions |

---

## Browser Extension Flow

The browser extension follows this flow:

```text
News Page
   ↓
detect-article.js
   ↓
service-worker.js
   ↓
Popup UI
   ↓
FastAPI Backend
   ↓
Perspective Analysis
   ↓
Contrast Selection
   ↓
Alternative Coverage
```

---

## Article Detection

### `extension/detect-article.js`

Detects whether the current webpage is likely to be a news article.

The script uses signals such as:

- Schema.org / JSON-LD article metadata
- `og:type = article`
- `<article>` elements containing substantial text

The extension extracts:

- Article title
- Article URL
- Article description

---

## Background Service Worker

### `extension/service-worker.js`

The service worker:

- Receives detected article information
- Stores article data separately for each browser tab
- Relays article data to the popup when requested
- Acts as the communication bridge between the content script and popup

---

## Popup

The popup:

1. Requests the detected article from the background service worker.
2. Calls the FastAPI backend.
3. Receives political-leaning and contrasting-perspective results.
4. Displays the returned coverage and perspective information.

---

## Political Perspective Analysis

Kaleido currently uses two forms of perspective information.

### Per-Article Bias Classification

`services/bias_classifier.py`

Uses a pretrained Hugging Face text-classification transformer model.

#### Input

```text
Article Title + Description
```

#### Output

```text
Political Leaning Classification
Confidence Score
```

The current model scope is centered on **U.S. political/news data**.

Indian news classification and broader language support are planned as the project develops.

---

## Outlet-Level Bias Lookup

### `services/bias_lookup.py`

Provides a static domain-based baseline bias mapping for known outlets.

Examples:

```text
Reuters       → Center
Fox News      → Right
The Guardian  → Left
```

This acts as an additional perspective signal for known publishers.

---

## Contrast Selection

### `services/contrast_selector.py`

Filters same-perspective articles from the available candidate results.

```text
Current Article
      ↓
Bias Classification
      ↓
Current Perspective
      ↓
Contrast Filter
      ↓
Alternative Perspectives
```

The goal is **not** to decide which article is correct.

Kaleido instead gives readers access to different viewpoints so they can compare coverage and form their own understanding.

---

## Article Processing and Embeddings

The semantic-processing pipeline introduces three main components.

### Article Processor

`services/article_processor.py`

Responsible for preparing extracted article content before chunking and embedding.

---

### Chunker

`services/chunker.py`

Splits long article text into smaller sentence-aware chunks so that semantic representations can be generated from manageable pieces of text.

The chunking process helps:

- Preserve sentence meaning
- Keep chunks within manageable sizes
- Prepare text for embedding generation
- Support future semantic retrieval

---

### Embedding Service

`services/embedding_service.py`

Converts article chunks into numerical vector embeddings.

These embeddings are intended to support **semantic similarity search**, allowing Kaleido to find articles covering the same event even when different publishers use different wording.

> The persistent vector database and complete semantic retrieval pipeline are not yet integrated.

---

## Semantic Retrieval Pipeline

The planned semantic-retrieval workflow is:

```text
Article
   ↓
Article Processing
   ↓
Chunking
   ↓
Embedding Generation
   ↓
Vector Database
   ↓
Semantic Search
   ↓
Related News Articles
```

### Currently Implemented

- Article processing
- Sentence-aware chunking
- Embedding generation

### Still Under Development

- Persistent vector storage
- Live article ingestion
- Vector similarity search
- Full semantic retrieval

---

## Running Locally

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

### 1. Install Dependencies

```bash
uv sync
```

### 2. Start the FastAPI Backend

```bash
uv run uvicorn main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

---

## API Endpoints

### Health Check

```text
http://127.0.0.1:8000/health
```

Used to verify that the backend is running.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically provides interactive Swagger documentation for testing API endpoints.

---

## Running the Chrome Extension

The FastAPI backend must be running before the extension can fetch results.

1. Open Chrome.
2. Navigate to:

   ```text
   chrome://extensions
   ```

3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the `extension/` folder containing `manifest.json`.
6. Open a news article.
7. Click the Kaleido extension icon in the Chrome toolbar.

If you modify extension files:

1. Return to `chrome://extensions`.
2. Find the Kaleido extension.
3. Click the refresh icon.

---

## Current Limitations

Kaleido is still under active development.

Current limitations include:

- Related articles still use prototype/static data rather than a live news-retrieval system.
- Real-time live news retrieval is not fully connected.
- The political-leaning classifier is currently centered on U.S. political/news context.
- Indian political/news classification is planned but not yet integrated.
- Broader multilingual support is planned.
- Persistent vector database storage is not yet connected.
- Full semantic retrieval from live article sources is not yet complete.
- RAG-based multi-source comparison is not yet integrated.
- The extension currently uses a popup instead of the planned full Chrome Side Panel experience.

---

## Planned Development

### Phase 1 — Indian News and Broader Language Support

Extend perspective analysis beyond the current U.S.-focused classifier to support:

- Indian political/news context
- Indian news outlets
- Region-specific political framing
- Broader language coverage

---

### Phase 2 — Real News Retrieval

Replace prototype/static related articles with live news retrieved through:

- News APIs
- Search services
- RSS feeds
- Automated ingestion pipelines

---

### Phase 3 — Vector Database Integration

Store generated article embeddings in a vector database so Kaleido can retrieve semantically similar articles.

```text
Article Chunks
      ↓
Embeddings
      ↓
Vector Database
      ↓
Semantic Similarity Search
```

---

### Phase 4 — Semantic Article Matching

Use embeddings to find coverage of the same event even when different news organizations use different words or sentence structures.

---

### Phase 5 — Retrieval-Augmented Generation (RAG)

Retrieved source articles will be provided to an LLM as grounded context.

Planned outputs include:

- Event summary
- Shared facts
- Key differences
- Disputed claims
- Different stakeholder viewpoints
- Direct source links

---

### Phase 6 — Enhanced Browser Interface

Move from the current popup-based interface to a full **Chrome Side Panel** for richer multi-source side-by-side comparison.

---

## Project Goal

Kaleido does not tell readers what to think.

Its goal is to make contrasting coverage easier to discover, reduce dependence on single-source news consumption, and help readers develop a broader understanding of the same event.

> **Kaleido does not decide what is right — it helps readers see what others are saying.**

---

## License

This project is licensed under the **MIT License**.