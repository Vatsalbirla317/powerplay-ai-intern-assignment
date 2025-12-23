"""High-level parsing & repair pipeline.

Implements parse_and_repair_json which accepts raw LLM text and attempts to
parse it into a list of strict schema objects, following the rules:
- Try json.loads
- Try local repair
- If still fails, allow LLM retry (caller handles LLM retry) -- here we implement a helper
- Final fallback: produce null-filled schema for one record
"""
from typing import List, Dict, Any, Optional
import json
from .utils import attempt_local_json_repair, ensure_array_of_objects, process_record
from .schema import strict_schema_template


def parse_and_repair_json(raw_text: str) -> Optional[List[Dict[str, Any]]]:
    """Try to parse raw_text into list[dict], auto-repair locally when possible.

    Returns a list of processed records (schema-enforced) when parsing succeeds,
    or None when parsing cannot be recovered locally. The caller is responsible
    for invoking the LLM retry and providing a final fallback when needed.
    """
    # Try direct JSON parse
    try:
        data = json.loads(raw_text)
    except Exception:
        data = attempt_local_json_repair(raw_text)

    if data is None:
        return None

    arr = ensure_array_of_objects(data)
    if not arr:
        return None

    processed = [process_record(obj) for obj in arr]
    return processed
