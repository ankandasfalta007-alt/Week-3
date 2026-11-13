import os

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("RESEARCH_MODEL", "claude-sonnet-5-5")
MAX_PAGE_CHARS = 6000       # per-page text sent to the summarizer
FETCH_TIMEOUT = 10          # seconds
MAX_WORKERS = 5             # parallel fetches / summaries
MIN_RELEVANCE = 4           # summaries scored below this are dropped
USER_AGENT = "Mozilla/5.0 (compatible; AIResearchAssistant/1.0)"
