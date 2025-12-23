"""Groq LLM wrapper utilities.

Provides call_groq_llm() which calls the Groq REST API (configurable) and
returns the raw text output from the model. It supports a single retry
with a correction prompt when asked.

Note: Network errors bubble up to the caller for testability.
"""
from typing import Optional, Dict
import os
import requests

GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/v1/engines")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class GroqError(RuntimeError):
    pass


def call_groq_llm(prompt: str, model: str = "llama3-70b-8192", max_tokens: int = 2048, retry_with_correction: bool = True) -> str:
    """Call the Groq LLM and return raw text.

    - prompt: prompt to send
    - model: model id
    - retry_with_correction: if True, performs one additional call with a correction prompt when response is empty or obviously malformed

    Raises GroqError on non-200 or API key missing.
    """
    # Development/mock mode: when AI_STRUCTURER_USE_MOCK=1, return deterministic JSON for testing.
    if os.getenv("AI_STRUCTURER_USE_MOCK") == "1":
        # Return a simple deterministic JSON array for a single input line.
        mock = '[{"material_name":"Screws","quantity":20,"unit":"boxes","project_name":null,"location":null,"urgency":"low","deadline":null}]'
        return mock

    if not GROQ_API_KEY:
        raise GroqError("GROQ_API_KEY not set in environment")

    url = f"{GROQ_API_URL}/{model}/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "prompt": prompt,
        "max_tokens": max_tokens,
    }

    resp = requests.post(url, json=body, headers=headers, timeout=60)
    if resp.status_code != 200:
        raise GroqError(f"Groq API error: {resp.status_code} {resp.text}")

    j = resp.json()
    # This code assumes the Groq API returns a 'choices' list with 'text' fields
    text = ""
    try:
        text = j.get("choices", [{}])[0].get("text", "")
    except Exception:
        text = resp.text

    # If content looks empty or non-json and we want to retry, do so once with correction prompt
    if retry_with_correction and (not text.strip() or text.strip().startswith("Error") or "{" not in text):
        correction_prompt = (
            "The previous output was invalid JSON. Please return a strictly valid JSON array (only JSON, no explanatory text)"
            " where each item follows this schema exactly:"
            " {\n  \"material_name\": string,\n  \"quantity\": number,\n  \"unit\": string,\n  \"project_name\": string|null,\n  \"location\": string|null,\n  \"urgency\": \"low\"|\"medium\"|\"high\",\n  \"deadline\": string(ISO date)|null\n}\n"
        )
        # Append correction instruction to original prompt
        resp2 = requests.post(url, json={"prompt": prompt + "\n\n" + correction_prompt, "max_tokens": max_tokens}, headers=headers, timeout=60)
        if resp2.status_code != 200:
            raise GroqError(f"Groq correction API error: {resp2.status_code} {resp2.text}")
        try:
            text2 = resp2.json().get("choices", [{}])[0].get("text", "")
        except Exception:
            text2 = resp2.text
        return text2

    return text
