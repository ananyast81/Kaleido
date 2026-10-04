from pydantic import BaseModel

# Describing what we expect the extension to send us (the article the user is viewing)
class ArticleIn(BaseModel):
    url: str
    title: str
    description: str = ""
    content: str = ""
    published_at: str | None = None
    publisher: str | None = None
    
class EntityOut(BaseModel):
    text: str
    label: str
    meaning: str


class ArticleNLPOut(BaseModel):
    url: str
    title: str
    cleaned_text: str
    sentences: list[str]
    entities: list[EntityOut]
    sentence_count: int
    word_count: int
# Model that describes 1 article in the response
class RelatedArticle(BaseModel):
    title: str
    url: str
    source: str
    bias: str | None = None  # None is default
    confidence: float | None = None

# Wrapper model
class RelatedArticlesOut(BaseModel):
    related: list[RelatedArticle]

class EntityOut(BaseModel):
    text: str
    label: str
    meaning: str


class ArticleChunkOut(BaseModel):
    chunk_id: str
    text: str
    token_count: int
    start_sentence: int
    end_sentence: int
    entities: list[EntityOut]


class ChunkedArticleOut(BaseModel):
    article_id: str
    url: str
    title: str
    sentence_count: int
    chunk_count: int
    chunks: list[ArticleChunkOut]
class EmbeddedChunkOut(ArticleChunkOut):
    embedding: list[float]
    embedding_norm: float


class EmbeddedArticleOut(BaseModel):
    article_id: str
    url: str
    title: str
    embedding_model: str
    embedding_dimension: int
    chunk_count: int
    chunks: list[EmbeddedChunkOut]