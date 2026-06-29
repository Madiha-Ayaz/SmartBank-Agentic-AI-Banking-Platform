import os
import json
import logging
from typing import Optional

import httpx

logger = logging.getLogger("smartbank.loan_agent.llm")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"

SYSTEM_PROMPT_BASE = """You are Zara, a professional AI Loan Assistant at SmartBank. You help customers apply for loans through natural conversation.

RULES:
- Be professional, friendly, and empathetic
- Ask ONE question at a time
- Extract structured data from customer responses
- Validate information as you receive it
- Never ask for sensitive data like PINs or passwords
- Support both English and Urdu (Roman Urdu)
- Keep responses concise and clear

Current step: {step}
Data collected so far: {data}
"""


def call_llm(
    messages: list[dict],
    system_prompt: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 500,
) -> str:
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set, using fallback response")
        return ""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://smartbank.ai",
        "X-Title": "SmartBank Loan Agent",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if system_prompt:
        payload["messages"].append({"role": "system", "content": system_prompt})

    for m in messages:
        payload["messages"].append(m)

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{OPENROUTER_BASE}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return ""


def extract_json(text: str) -> Optional[dict]:
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        return None
