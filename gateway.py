"""
Server-side only. Reads gateway credentials from environment variables.
Only imported by app.py / search.py — never sent to the browser.
"""
import os

from openai import OpenAI

GATEWAY_BASE_URL = (os.environ.get("GATEWAY_BASE_URL") or "").rstrip("/")
CLASSGW_KEY = os.environ.get("CLASSGW_KEY")

GATEWAY_CONFIGURED = bool(GATEWAY_BASE_URL and CLASSGW_KEY)

CHAT_MODEL = "gpt-5.6-terra"
EMBEDDING_MODEL = "openai/text-embedding-3-small"

# Chat completions (catalogue Q&A) go through the OpenAI-compatible door.
chat_client = (
    OpenAI(base_url=f"{GATEWAY_BASE_URL}/v1", api_key=CLASSGW_KEY)
    if GATEWAY_CONFIGURED
    else None
)

# Embeddings (natural-language search) go through the OpenRouter door.
embedding_client = (
    OpenAI(base_url=f"{GATEWAY_BASE_URL}/openrouter/v1", api_key=CLASSGW_KEY)
    if GATEWAY_CONFIGURED
    else None
)
