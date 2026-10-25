"""Durable local storage for normalized articles and chunk embeddings."""
import json
import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path("data") / "kaleido.sqlite3"


def connect() -> sqlite3.Connection:
    path = Path(os.getenv("KALEIDO_DB_PATH", str(DEFAULT_DB_PATH)))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS articles (
          id TEXT PRIMARY KEY, url TEXT NOT NULL UNIQUE, title TEXT NOT NULL,
          description TEXT NOT NULL DEFAULT '', content TEXT NOT NULL DEFAULT '',
          source TEXT NOT NULL, published_at TEXT, bias TEXT, bias_confidence REAL,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chunks (
          id TEXT PRIMARY KEY, article_id TEXT NOT NULL REFERENCES articles(id),
          text TEXT NOT NULL, embedding TEXT NOT NULL, token_count INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS chunks_article_idx ON chunks(article_id);
        """
    )
    return connection


def upsert_article(article: dict, chunks: list[dict]) -> None:
    with connect() as connection:
        connection.execute(
            """INSERT INTO articles
            (id,url,title,description,content,source,published_at,bias,bias_confidence)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(url) DO UPDATE SET title=excluded.title,
            description=excluded.description, content=excluded.content,
            source=excluded.source, published_at=excluded.published_at,
            bias=excluded.bias, bias_confidence=excluded.bias_confidence,
            updated_at=CURRENT_TIMESTAMP""",
            (article["id"], article["url"], article["title"],
             article.get("description", ""), article.get("content", ""),
             article.get("source", ""), article.get("published_at"),
             article.get("bias"), article.get("bias_confidence")),
        )
        connection.execute("DELETE FROM chunks WHERE article_id = ?", (article["id"],))
        connection.executemany(
            "INSERT INTO chunks(id,article_id,text,embedding,token_count) VALUES(?,?,?,?,?)",
            [(chunk["chunk_id"], article["id"], chunk["text"],
              json.dumps(chunk["embedding"]), chunk.get("token_count", 0))
             for chunk in chunks],
        )


def all_chunks() -> list[sqlite3.Row]:
    with connect() as connection:
        return connection.execute(
            "SELECT c.*, a.url, a.title, a.source, a.published_at, a.bias, a.bias_confidence "
            "FROM chunks c JOIN articles a ON a.id = c.article_id"
        ).fetchall()
