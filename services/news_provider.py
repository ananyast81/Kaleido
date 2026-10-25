"""No-secret RSS retrieval, with a documented optional JSON API provider."""
import json
import os
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree

DEFAULT_RSS_FEEDS = (
    "https://feeds.bbci.co.uk/news/world/rss.xml,"
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
)


def _source(url: str) -> str:
    return (urlparse(url).hostname or "").removeprefix("www.")


def fetch_related(query: str, limit: int = 30) -> list[dict]:
    if os.getenv("NEWS_PROVIDER", "rss").lower() == "api":
        endpoint = os.getenv("NEWS_API_URL")
        if not endpoint:
            raise RuntimeError("NEWS_API_URL is required when NEWS_PROVIDER=api")
        headers = {}
        if os.getenv("NEWS_API_KEY"):
            headers["Authorization"] = f"Bearer {os.environ['NEWS_API_KEY']}"
        with urlopen(Request(endpoint, headers=headers), timeout=10) as response:
            return json.load(response).get("articles", [])[:limit]

    terms = {word.casefold() for word in query.split() if len(word) > 3}
    results = []
    for feed in os.getenv("RSS_FEEDS", DEFAULT_RSS_FEEDS).split(","):
        try:
            request = Request(feed.strip(), headers={"User-Agent": "Kaleido/0.1"})
            with urlopen(request, timeout=10) as response:
                root = ElementTree.fromstring(response.read())
        except Exception:
            continue
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            url = (item.findtext("link") or "").strip()
            description = (item.findtext("description") or "").strip()
            if url and (not terms or any(term in f"{title} {description}".casefold() for term in terms)):
                results.append({
                    "url": url, "title": title, "description": description,
                    "content": description, "source": _source(url),
                    "published_at": item.findtext("pubDate"),
                })
            if len(results) >= limit:
                return results
    return results
