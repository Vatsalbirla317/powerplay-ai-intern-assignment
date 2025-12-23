"""Top-level process_all_inputs and write_outputs functions.

- process_all_inputs: loads test inputs, calls LLM for each, attempts parse and repair, and applies schema.
- write_outputs: writes a JSON array to file.

This module separates I/O and core logic to help testing.
"""
from typing import List
import json
from pathlib import Path

from .utils import load_inputs
from .llm import call_groq_llm
from .parser import parse_and_repair_json


def process_all_inputs(input_path: str, model: str = "llama3-70b-8192") -> List[dict]:
    """Process each line in input file by calling LLM and parsing output.

    For each input line, we:
      - call Groq LLM once
      - parse locally
      - if parse fails, the LLM call_groq_llm is configured to retry once with correction
      - if still fails, parse_and_repair_json provides final fallback

    Returns a list of schema-enforced records.
    """
    lines = load_inputs(input_path)
    results = []
    for line in lines:
        # Call LLM for this line
        try:
            raw = call_groq_llm(_make_instructions(line), model=model)
        except Exception:
            raw = ""

        # First attempt: parse & local repair only
        parsed = parse_and_repair_json(raw)

        # If parsing failed locally, retry LLM once with a correction prompt
        if parsed is None:
            try:
                correction_prompt = (
                    _make_instructions(line)
                    + "\n\nThe previous response was invalid JSON. Return ONLY a strictly valid JSON array that follows the exact schema (no commentary)."
                )
                corrected_raw = call_groq_llm(correction_prompt, model=model, max_tokens=2048, retry_with_correction=False)
            except Exception:
                corrected_raw = ""

            parsed = parse_and_repair_json(corrected_raw)

        # Final fallback: if still None, append one null-filled schema
        if parsed is None:
            from .schema import strict_schema_template

            parsed = [strict_schema_template()]

        results.extend(parsed)
    return results


def write_outputs(records: List[dict], output_path: str):
    p = Path(output_path)
    p.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_instructions(line: str) -> str:
    """Construct the prompt to extract the required JSON array.

    The prompt must instruct the model to output only JSON and follow the schema exactly.
    """
    schema_str = (
        "Return a strictly valid JSON array and nothing else. Each element must be an object with exactly these keys:"
        " material_name (string), quantity (number), unit (string), project_name (string|null),"
        " location (string|null), urgency (\"low\"|\"medium\"|\"high\"), deadline (ISO date string|null)."
    )
    prompt = f"Extract structured data from the following business text line. {schema_str}\n\nText: {line}\n"
    return prompt