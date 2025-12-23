"""Utilities: input loading, local JSON repair, urgency inference, processing pipeline."""
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime, timedelta

from .schema import enforce_schema, strict_schema_template


def load_inputs(path: str) -> List[str]:
    """Load raw lines from text file. Returns non-empty stripped lines."""
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


def attempt_local_json_repair(text: str) -> Optional[Any]:
    """Try to repair common malformed JSON issues and return parsed Python object or None.

    Repairs attempted:
    - Extract first JSON array or object substring
    - Replace single quotes with double quotes (careful)
    - Remove trailing commas
    - Wrap top-level object in array if single object returned
    """
    if not text or not text.strip():
        return None

    s = text.strip()

    # If there's surrounding text, try extract first { ... } or [ ... ] block
    m = re.search(r"(\[.*\]|\{.*\})", s, flags=re.DOTALL)
    if m:
        s = m.group(1)

    # Replace trailing commas before closing braces/brackets
    s = re.sub(r",\s*([}\]])", r"\1", s)

    # Replace single quotes with double quotes when safe-ish (not perfect)
    if "'" in s and '"' not in s:
        s = s.replace("'", '"')

    # Remove non-JSON leading/trailing garbage
    s = s.strip()

    try:
        parsed = json.loads(s)
    except Exception:
        # Try wrapping object into array
        try:
            parsed2 = json.loads("[" + s + "]")
            return parsed2
        except Exception:
            return None
    # If parsed is single object, wrap into list
    if isinstance(parsed, dict):
        return [parsed]
    return parsed


def ensure_array_of_objects(obj: Any) -> List[Dict[str, Any]]:
    """Normalize to list of dicts. If not possible, return empty list."""
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        return [obj]
    return []


def infer_urgency_from_deadline(deadline_iso: Optional[str]) -> Optional[str]:
    """Deterministic urgency inference based on deadline date only.

    - high → <= 7 days
    - medium → 7–30 days
    - low → >30 days or None
    """
    if not deadline_iso:
        return None
    try:
        dt = datetime.fromisoformat(deadline_iso)
    except Exception:
        try:
            dt = datetime.strptime(deadline_iso, "%Y-%m-%d")
        except Exception:
            return None
    today = datetime.now()
    delta = (dt - today).days
    if delta <= 7:
        return "high"
    if 7 < delta <= 30:
        return "medium"
    if delta > 30:
        return "low"
    return None


def process_record(raw_obj: Dict[str, Any]) -> Dict[str, Any]:
    """Enforce schema and deterministically infer urgency if missing.

    Returns an object that strictly matches the schema (no extra keys).
    """
    enforced = enforce_schema(raw_obj)
    # If urgency missing/null, infer from deadline
    if not enforced.get("urgency"):
        inferred = infer_urgency_from_deadline(enforced.get("deadline"))
        enforced["urgency"] = inferred or "low"
    return enforced
