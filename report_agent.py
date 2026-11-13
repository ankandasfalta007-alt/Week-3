"""Agent 3: turns source summaries into a structured, cited report."""
from __future__ import annotations

from ..llm import LLMClient
from ..models import ReportSection, ResearchReport, SourceSummary

SYSTEM = (
    "You are a senior research writer. Write a well-structured report using ONLY the numbered "
    "source notes provided. Cite sources inline as [1], [2], etc. Flag disagreements between "
    "sources and note gaps honestly. Do not add facts that are not in the notes."
)

PROMPT = """Research topic: "{topic}"

Source notes:
{notes}

Return JSON:
{{"title": "report title",
"executive_summary": "3-5 sentences",
"sections": [{{"heading": "...", "content": "markdown prose with inline [n] citations"}}],
"conclusion": "short paragraph",
"limitations": "what the sources do not cover or where they conflict"}}

Use 3-5 sections organised by theme, not by source."""


class ReportAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, topic: str, summaries: list[SourceSummary]) -> ResearchReport:
        notes = "\n\n".join(
            f"[{i}] {s.source.title} ({s.source.url})\n{s.summary}\n"
            + "\n".join(f"- {p}" for p in s.key_points)
            for i, s in enumerate(summaries, 1)
        )
        data = self.llm.complete_json(SYSTEM, PROMPT.format(topic=topic, notes=notes), max_tokens=3500)
        return ResearchReport(
            topic=topic,
            title=data.get("title", f"Research Report: {topic}"),
            executive_summary=data.get("executive_summary", ""),
            sections=[
                ReportSection(s.get("heading", ""), s.get("content", ""))
                for s in data.get("sections", [])
            ],
            conclusion=data.get("conclusion", ""),
            limitations=data.get("limitations", ""),
            sources=[s.source for s in summaries],
        )
