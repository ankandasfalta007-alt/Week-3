"""Agent 1: plans queries, searches the web, and fetches page text."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .. import config
from ..llm import LLMClient
from ..models import SearchResult

try:
    from ddgs import DDGS
except ImportError:  # older package name
    from duckduckgo_search import DDGS

SYSTEM = (
    "You are a research search planner. Given a topic, produce diverse, specific web search "
    "queries that together cover its key facets (background, current state, data, debates)."
)


class SearchAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def plan_queries(self, topic: str, n: int = 3) -> list[str]:
        data = self.llm.complete_json(
            SYSTEM,
            f'Topic: "{topic}"\nReturn {{"queries": [...]}} with exactly {n} queries.',
            max_tokens=400,
        )
        queries = [q.strip() for q in data.get("queries", []) if isinstance(q, str) and q.strip()]
        return queries[:n] or [topic]

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        try:
            hits = DDGS().text(query, max_results=max_results) or []
        except Exception:
            return []
        return [
            SearchResult(title=h.get("title", ""), url=h.get("href", ""), snippet=h.get("body", ""))
            for h in hits
            if h.get("href")
        ]

    def search_all(self, queries: list[str], per_query: int = 5) -> list[SearchResult]:
        seen, results = set(), []
        for q in queries:
            for r in self.search(q, per_query):
                key = r.url.rstrip("/")
                if key not in seen:
                    seen.add(key)
                    results.append(r)
        return results

    @staticmethod
    def fetch_text(url: str) -> str:
        if urlparse(url).scheme not in ("http", "https"):
            return ""
        try:
            resp = requests.get(
                url, timeout=config.FETCH_TIMEOUT, headers={"User-Agent": config.USER_AGENT}
            )
            if resp.status_code != 200 or "html" not in resp.headers.get("content-type", ""):
                return ""
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()
            text = " ".join(soup.get_text(" ", strip=True).split())
            return text[: config.MAX_PAGE_CHARS]
        except requests.RequestException:
            return ""

    def fetch_all(self, results: list[SearchResult]) -> list[SearchResult]:
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as pool:
            texts = list(pool.map(lambda r: self.fetch_text(r.url), results))
        for r, t in zip(results, texts):
            r.content = t or r.snippet  # fall back to the search snippet
        return results
