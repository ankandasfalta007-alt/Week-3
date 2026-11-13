"""Coordinates the three agents and streams progress events to the UI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .agents import ReportAgent, SearchAgent, SummarizerAgent
from .llm import LLMClient
from .models import ResearchReport


@dataclass
class Progress:
    stage: str  # planning | searching | reading | summarizing | writing | done | error
    message: str
    report: ResearchReport | None = None


class ResearchOrchestrator:
    def __init__(self, llm: LLMClient):
        self.searcher = SearchAgent(llm)
        self.summarizer = SummarizerAgent(llm)
        self.reporter = ReportAgent(llm)

    def stream(self, topic: str, num_queries: int = 3, results_per_query: int = 5) -> Iterator[Progress]:
        yield Progress("planning", "🧭 Search agent: planning queries…")
        queries = self.searcher.plan_queries(topic, num_queries)
        yield Progress("planning", "Queries: " + " | ".join(queries))

        yield Progress("searching", "🔎 Search agent: searching the web…")
        results = self.searcher.search_all(queries, results_per_query)
        if not results:
            yield Progress("error", "No search results found. Try rephrasing the topic.")
            return

        yield Progress("reading", f"📄 Search agent: fetching {len(results)} pages…")
        results = self.searcher.fetch_all(results)

        yield Progress("summarizing", "🧠 Summarizer agent: analysing sources…")
        summaries = self.summarizer.summarize_all(topic, results)
        if not summaries:
            yield Progress("error", "No sources were relevant or readable enough to summarize.")
            return
        yield Progress("summarizing", f"Kept {len(summaries)} of {len(results)} sources.")

        yield Progress("writing", "📝 Report agent: writing the report…")
        report = self.reporter.generate(topic, summaries)
        yield Progress("done", "✅ Report ready.", report)

    def run(self, topic: str, **kwargs) -> ResearchReport:
        report = None
        for p in self.stream(topic, **kwargs):
            if p.stage == "error":
                raise RuntimeError(p.message)
            report = p.report or report
        return report
