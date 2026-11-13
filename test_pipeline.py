"""Offline pipeline test: fake LLM + stubbed web, so no API key or network is needed."""
from research_assistant import ResearchOrchestrator
from research_assistant.agents import search_agent
from research_assistant.llm import extract_json
from research_assistant.models import SearchResult


class FakeLLM:
    def complete_json(self, system, user, max_tokens=1500, retries=1):
        if "search planner" in system:
            return {"queries": ["q one", "q two"]}
        if "research analyst" in system:
            return {"summary": "A summary.", "key_points": ["fact"], "relevance": 8}
        return {
            "title": "T",
            "executive_summary": "ES",
            "sections": [{"heading": "H", "content": "Body [1]"}],
            "conclusion": "C",
            "limitations": "L",
        }


def test_extract_json_handles_fences():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('Sure! {"a": 1} done') == {"a": 1}


def test_full_pipeline(monkeypatch):
    monkeypatch.setattr(
        search_agent.SearchAgent, "search",
        lambda self, q, n=5: [SearchResult("Title", f"https://example.com/{q.replace(' ', '')}", "snip")],
    )
    monkeypatch.setattr(search_agent.SearchAgent, "fetch_text", staticmethod(lambda url: "page text"))

    report = ResearchOrchestrator(FakeLLM()).run("anything")
    md = report.to_markdown()
    assert report.title == "T" and len(report.sources) == 2
    assert "## Sources" in md and "Body [1]" in md
