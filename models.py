# Describing what we expect the extension to send us (the article the user is viewing)
from pydantic import BaseModel

class ArticleIn(BaseModel):
    url: str
    title: str
    description: str = ""

# Model that describes 1 article in the response
class RelatedArticle(BaseModel):
    title: str
    url: str
    source: str
    bias: str | None = None  # None is default

# Wrapper model
class RelatedArticlesOut(BaseModel):
    related: list[RelatedArticle]