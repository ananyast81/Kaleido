"""Indexing, cosine retrieval, and URL deduplication over SQLite chunks."""
import hashlib
import json

import numpy as np

from services.bias_classifier import classify_bias
from services.bias_lookup import get_outlet_bias
from services.news_provider import fetch_related
from services.storage import all_chunks, upsert_article


def article_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def index_articles(articles: list[dict]) -> None:
    from services.embedding_service import create_embeddings
    items = [item for item in articles if item.get("url") and item.get("title")]
    if not items:
        return
    vectors = create_embeddings([
        f"{item['title']}. {item.get('description', '')}" for item in items
    ])
    for item, vector in zip(items, vectors, strict=True):
        bias = item.get("bias") or get_outlet_bias(item["url"])
        confidence = item.get("bias_confidence")
        if not bias:
            bias, confidence = classify_bias(
                f"{item['title']}. {item.get('description', '')}"
            )
        identifier = article_id(item["url"])
        upsert_article(
            {**item, "id": identifier, "bias": bias, "bias_confidence": confidence},
            [{"chunk_id": f"{identifier}-chunk-0", "text": item["title"],
              "embedding": vector.tolist(), "token_count": len(item["title"].split())}],
        )


def retrieve(article: dict, limit: int = 5) -> list[dict]:
    from services.embedding_service import create_embeddings
    query = create_embeddings([
        f"{article.get('title', '')}. {article.get('description', '')}"
    ])[0]
    matches, seen_urls = [], set()
    for row in all_chunks():
        if row["url"] == article.get("url") or row["url"] in seen_urls:
            continue
        score = float(np.dot(query, np.asarray(json.loads(row["embedding"]), dtype=np.float32)))
        seen_urls.add(row["url"])
        matches.append({
            "title": row["title"], "url": row["url"], "source": row["source"],
            "bias": row["bias"], "confidence": row["bias_confidence"],
            "similarity": round(score, 4), "published_at": row["published_at"],
        })
    return sorted(matches, key=lambda item: item["similarity"], reverse=True)[:limit]


def find_contrasting(article: dict, limit: int = 5):
    current_bias, _ = classify_bias(
        f"{article.get('title', '')}. {article.get('description', '')}"
    )
    index_articles(fetch_related(article.get("title", ""), limit=30))
    from models import RelatedArticle
    from services.contrast_selector import select_contrasting
    candidates = [RelatedArticle(**item) for item in retrieve(article, limit * 2)]
    return select_contrasting(current_bias, candidates)[:limit]
