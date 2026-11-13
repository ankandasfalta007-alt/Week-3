"""Plain data containers passed between the agents."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str = ""
    content: str = ""  # full page text, filled in by the search agent


@dataclass
class SourceSummary:
    source: SearchResult
    summary: str
    key_points: list[str] = field(default_factory=list)
    relevance: int = 5  # 1-10, judged by the summarizer


@dataclass
class ReportSection:
    heading: str
    content: str


@dataclass
class ResearchReport:
    topic: str
    title: str
    executive_summary: str
    sections: list[ReportSection]
    conclusion: str
    limitations: str
    sources: list[SearchResult]
    generated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    def to_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            f"*Topic: {self.topic} · Generated {self.generated_at}*",
            "",
            "## Executive Summary",
            self.executive_summary,
            "",
        ]
        for s in self.sections:
            lines += [f"## {s.heading}", s.content, ""]
        lines += ["## Conclusion", self.conclusion, ""]
        if self.limitations:
            lines += ["## Limitations", self.limitations, ""]
        lines.append("## Sources")
        for i, src in enumerate(self.sources, 1):
            lines.append(f"{i}. [{src.title or src.url}]({src.url})")
        return "\n".join(lines)
