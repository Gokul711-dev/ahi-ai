"""
tools/web_search.py
DuckDuckGo web search + RSS news fetching.
"""
import feedparser
from typing import Optional


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using DuckDuckGo. Returns list of {title, url, snippet}."""
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            }
            for r in results
        ]
    except Exception as e:
        return [{"title": "Search Error", "url": "", "snippet": str(e)}]


def get_news(topic: Optional[str] = None, max_results: int = 5, feeds: list[dict] = None) -> list[dict]:
    """Fetch latest news from RSS feeds, optionally filtered by topic."""
    default_feeds = [
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage"},
        {"name": "BBC Technology", "url": "http://feeds.bbci.co.uk/news/technology/rss.xml"},
        {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    ]
    feed_list = feeds or default_feeds
    articles = []
    for feed_info in feed_list:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "")[:300]
                link = entry.get("link", "")
                if topic and topic.lower() not in (title + summary).lower():
                    continue
                articles.append({
                    "source": feed_info["name"],
                    "title": title,
                    "summary": summary,
                    "url": link,
                })
                if len(articles) >= max_results * len(feed_list):
                    break
        except Exception:
            continue
    # Deduplicate and limit
    seen = set()
    unique = []
    for a in articles:
        if a["title"] not in seen:
            seen.add(a["title"])
            unique.append(a)
    return unique[:max_results]


def format_search_results(results: list[dict]) -> str:
    """Format search results as a readable string."""
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. **{r.get('title', 'Untitled')}**")
        if r.get('url'):
            lines.append(f"   URL: {r['url']}")
        if r.get('snippet') or r.get('summary'):
            lines.append(f"   {r.get('snippet', r.get('summary', ''))}")
    return "\n".join(lines)
