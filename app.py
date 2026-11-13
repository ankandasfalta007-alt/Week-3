"""Gradio UI for the multi-agent research assistant."""
from __future__ import annotations

import os
import re
import tempfile

import gradio as gr

from research_assistant import ResearchOrchestrator
from research_assistant.llm import LLMClient


def research(topic: str, api_key: str, num_queries: int, results_per_query: int):
    topic = (topic or "").strip()
    if not topic:
        yield "⚠️ Please enter a research topic.", "", None
        return
    try:
        orchestrator = ResearchOrchestrator(LLMClient(api_key=api_key or None))
    except ValueError as e:
        yield f"⚠️ {e}", "", None
        return

    log: list[str] = []
    try:
        for p in orchestrator.stream(topic, int(num_queries), int(results_per_query)):
            log.append(p.message)
            if p.report:
                md = p.report.to_markdown()
                slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:40] or "report"
                path = os.path.join(tempfile.mkdtemp(), f"{slug}.md")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(md)
                yield "\n\n".join(log), md, path
                return
            yield "\n\n".join(log), "", None
    except Exception as e:  # surface API/network failures in the UI
        log.append(f"❌ Error: {e}")
        yield "\n\n".join(log), "", None


with gr.Blocks(title="AI Research Assistant") as demo:
    gr.Markdown(
        "# 🔬 AI Research Assistant\n"
        "Three agents collaborate: **Search** → **Summarize** → **Report**."
    )
    with gr.Row():
        with gr.Column(scale=1):
            topic = gr.Textbox(label="Research topic", lines=2, placeholder="e.g. State of solid-state batteries in 2026")
            api_key = gr.Textbox(
                label="Anthropic API key (optional if set in .env)", type="password", placeholder="sk-ant-…"
            )
            num_queries = gr.Slider(1, 6, value=3, step=1, label="Search queries")
            results_per_query = gr.Slider(1, 8, value=4, step=1, label="Results per query")
            run_btn = gr.Button("Run research", variant="primary")
            progress = gr.Markdown(label="Agent activity")
            download = gr.File(label="Download report (.md)")
        with gr.Column(scale=2):
            report_md = gr.Markdown(label="Report")

    inputs = [topic, api_key, num_queries, results_per_query]
    outputs = [progress, report_md, download]
    run_btn.click(research, inputs, outputs)
    topic.submit(research, inputs, outputs)

if __name__ == "__main__":
    demo.queue().launch()
