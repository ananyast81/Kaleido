from models import RelatedArticle

def select_contrasting(curr_bias: str | None, related_articles: list[RelatedArticle]) -> list[RelatedArticle]:
    if curr_bias is None:
        return related_articles
    return [article for article in related_articles if article.bias != curr_bias]