import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool

from models import ArticleIn,ArticleNLPOut, RelatedArticle, RelatedArticlesOut
from services.bias_lookup import get_outlet_bias
from services.contrast_selector import select_contrasting
from services.bias_classifier import classify_bias
from services.article_processor import process_article_text
from services.chunker import create_chunks
from models import (
    ArticleIn,
    ArticleNLPOut,
    ArticleChunkOut,
    ChunkedArticleOut,
    EmbeddedChunkOut,
    EmbeddedArticleOut,
    RelatedArticle,
    RelatedArticlesOut,
)
from services.embedding_service import (
    add_embeddings_to_chunks,
)
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/echo")
async def echo(article: ArticleIn):
    return {"received": article}

@app.post("/articles/related", response_model=RelatedArticlesOut)
async def get_related_articles(article: ArticleIn):
    fake_results = [
        RelatedArticle(title="Example coverage from Outlet A", url="https://reuters.com/example", source="Reuters"),
        RelatedArticle(title="Example coverage from Outlet B", url="https://foxnews.com/example", source="Fox News"),
        RelatedArticle(title="Example coverage from Outlet C", url="https://theguardian.com/example", source="The Guardian"),
    ]
    for a in fake_results:
        a.bias = get_outlet_bias(a.url)

    curr_bias, curr_confidence = classify_bias(f"{article.title}. {article.description}")

    results = select_contrasting(curr_bias=curr_bias, related_articles=fake_results)
    return RelatedArticlesOut(related=results)
@app.post(
    "/articles/process",
    response_model=ArticleNLPOut
)
async def process_current_article(article: ArticleIn):
    if len(article.content.strip()) < 200:
        raise HTTPException(
            status_code=422,
            detail=(
                "Article content is too short. "
                "The extension may not have extracted the complete article."
            ),
        )

    try:
        processed = await run_in_threadpool(
            process_article_text,
            article.content,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return ArticleNLPOut(
        url=article.url,
        title=article.title,
        **processed,
    )

@app.post(
    "/articles/chunk",
    response_model=ChunkedArticleOut,
)
async def chunk_current_article(article: ArticleIn):
    if len(article.content.strip()) < 200:
        raise HTTPException(
            status_code=422,
            detail=(
                "Article content is too short. "
                "The extension may not have extracted "
                "the complete article."
            ),
        )

    try:
        # Clean text, split sentences and extract entities.
        processed = await run_in_threadpool(
            process_article_text,
            article.content,
        )

        # Generate a repeatable ID from the article URL.
        article_id = hashlib.sha256(
            article.url.encode("utf-8")
        ).hexdigest()[:16]

        # Group the sentences into chunks.
        chunks = await run_in_threadpool(
            create_chunks,
            article_id,
            processed["sentences"],
            processed["entities"],
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return ChunkedArticleOut(
        article_id=article_id,
        url=article.url,
        title=article.title,
        sentence_count=processed["sentence_count"],
        chunk_count=len(chunks),
        chunks=chunks,
    )

@app.post(
    "/articles/embed",
    response_model=EmbeddedArticleOut,
)
async def embed_current_article(article: ArticleIn):
    if len(article.content.strip()) < 200:
        raise HTTPException(
            status_code=422,
            detail=(
                "Article content is too short. "
                "At least 200 characters are required."
            ),
        )

    try:
        # 1. Clean text, split sentences and extract entities.
        processed = await run_in_threadpool(
            process_article_text,
            article.content,
        )

        # 2. Generate a consistent article ID.
        article_id = hashlib.sha256(
            article.url.encode("utf-8")
        ).hexdigest()[:16]

        # 3. Group sentences into chunks.
        chunks = await run_in_threadpool(
            create_chunks,
            article_id,
            processed["sentences"],
            processed["entities"],
        )

        # 4. Generate one embedding per chunk.
        embedding_result = await run_in_threadpool(
            add_embeddings_to_chunks,
            chunks,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return EmbeddedArticleOut(
        article_id=article_id,
        url=article.url,
        title=article.title,
        embedding_model=embedding_result[
            "embedding_model"
        ],
        embedding_dimension=embedding_result[
            "embedding_dimension"
        ],
        chunk_count=len(
            embedding_result["chunks"]
        ),
        chunks=embedding_result["chunks"],
    )