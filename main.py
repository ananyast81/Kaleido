from fastapi import FastAPI

from models import ArticleIn, RelatedArticle, RelatedArticlesOut
from services.bias_lookup import get_outlet_bias
from services.contrast_selector import select_contrasting

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
    curr_bias = get_outlet_bias(article.url)

    results = select_contrasting(curr_bias=curr_bias, related_articles=fake_results)
    return RelatedArticlesOut(related=results)