from services.news_provider import _source
from services.retrieval import retrieve
from services.storage import connect, upsert_article


def test_source_normalizes_www_host():
    assert _source("https://www.example.com/story") == "example.com"


def test_storage_round_trip_and_url_deduplication(tmp_path, monkeypatch):
    monkeypatch.setenv("KALEIDO_DB_PATH", str(tmp_path / "kaleido.sqlite3"))
    upsert_article(
        {
            "id": "one",
            "url": "https://example.com/story",
            "title": "A story",
            "source": "example.com",
            "bias": "left",
            "bias_confidence": 0.8,
        },
        [{"chunk_id": "one-chunk-0", "text": "A story", "embedding": [1.0, 0.0]}],
    )
    with connect() as connection:
        row = connection.execute("SELECT title FROM articles").fetchone()
    assert row["title"] == "A story"


def test_retrieve_deduplicates_urls(tmp_path, monkeypatch):
    monkeypatch.setenv("KALEIDO_DB_PATH", str(tmp_path / "kaleido.sqlite3"))
    upsert_article(
        {"id": "one", "url": "https://example.com/one", "title": "One", "source": "example"},
        [{"chunk_id": "one-chunk-0", "text": "One", "embedding": [1.0, 0.0]}],
    )
    upsert_article(
        {"id": "two", "url": "https://example.com/two", "title": "Two", "source": "example"},
        [{"chunk_id": "two-chunk-0", "text": "Two", "embedding": [0.9, 0.1]}],
    )
    import services.embedding_service as embedding_service
    monkeypatch.setattr(embedding_service, "create_embeddings", lambda _: [[1.0, 0.0]])
    results = retrieve({"url": "https://current.example/story", "title": "Current"}, limit=5)
    assert [item["url"] for item in results] == [
        "https://example.com/one", "https://example.com/two"
    ]
