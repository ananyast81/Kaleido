from models import RelatedArticlesOut

def select_contrasting(curr_bias: str | None, related_articles: RelatedArticlesOut) -> RelatedArticlesOut:
    if curr_bias is None:
        return related_articles
    results = []
    for article in related_articles:
        if article.bias != curr_bias:
            results.append(article)
    return results