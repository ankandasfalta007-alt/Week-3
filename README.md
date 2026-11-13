# 🔬 AI Research Assistant

A multi-agent research pipeline with a Gradio UI. Give it a topic and three cooperating agents produce a cited, structured report.

```
Topic ─► Search Agent ─► Summarizer Agent ─► Report Agent ─► Markdown report
         plans queries    summarizes each     writes sections,
         searches web     page + scores       citations, limits
         fetches pages    relevance
```

| Agent | Responsibility |
|---|---|
| **SearchAgent** | LLM plans diverse queries → DuckDuckGo search (no key needed) → fetches and cleans page text in parallel |
| **SummarizerAgent** | Summarizes each source in parallel, extracts key points, scores relevance 1–10 and drops weak sources |
| **ReportAgent** | Synthesizes the notes into a themed report with inline `[n]` citations, a conclusion and a limitations section |

The `ResearchOrchestrator` wires them together and streams progress to the UI.

## Quick start

```bash
git clone <your-repo-url> && cd ai-research-assistant
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                # add your ANTHROPIC_API_KEY
python app.py                                       # opens http://127.0.0.1:7860
```

You can also paste your API key into the UI instead of using `.env`.

## Use it from code

```python
from research_assistant import ResearchOrchestrator
from research_assistant.llm import LLMClient

report = ResearchOrchestrator(LLMClient()).run("Solid-state batteries in 2026")
print(report.to_markdown())
```

## Configuration

Edit `research_assistant/config.py` or set env vars: `RESEARCH_MODEL` (default `claude-sonnet-5-5`), page length cap, timeouts, parallelism, and the minimum relevance threshold.

## Tests

```bash
pytest
```
Tests run offline with a fake LLM and stubbed web access.

## Notes and limitations

- Web page text is treated as untrusted data; agents are instructed to ignore instructions embedded in pages.
- Some sites block scraping, so those sources fall back to the search snippet.
- Reports are only as good as the sources found. Always verify important claims via the cited links.

## Ideas for extension

Swap DuckDuckGo for Tavily/Serper, add a critic agent that fact-checks the report, cache fetched pages, or export to PDF/DOCX.
