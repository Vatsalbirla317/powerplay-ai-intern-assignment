"""Schema enforcement utilities.

Functions:
- strict_schema_template(): returns the strict keys and types
- enforce_schema(obj): returns an object that strictly matches the schema
"""
from typing import Any, Dict, Optional
from datetime import datetime
import re

SCHEMA_KEYS = [
    "material_name",
    "quantity",
    "unit",
    "project_name",
    "location",
    "urgency",
    "deadline",
]


def strict_schema_template() -> Dict[str, Optional[Any]]:
    return {
        "material_name": None,
        "quantity": None,
        "unit": None,
        "project_name": None,
        "location": None,
        "urgency": None,
        "deadline": None,
    }


def _to_number(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        # remove commas
        s2 = s.replace(",", "")
        try:
            return float(s2)
        except ValueError:
            # try extracting leading number
            m = re.match(r"^[^0-9-]*([0-9]+(?:\.[0-9]+)?)", s2)
            if m:
                return float(m.group(1))
            return None
    return None


def _to_iso_date_or_null(value) -> Optional[str]:
    if not value:
        return None
    if isinstance(value, str):
        s = value.strip()
        # Check common vague phrases that must be null
        vague_keywords = ["soon", "asap", "urgent", "next month", "next week", "whenever", "no rush", "sometime"]
        if any(k in s.lower() for k in vague_keywords):
            return None
        # Try parse with datetime for a few formats, prefer ISO
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d", "%b %d %Y", "%B %d, %Y", "%d %b %Y"):
            try:
                dt = datetime.strptime(s, fmt)
                return dt.date().isoformat()
            except Exception:
                pass
        # Try ISO parsing
        try:
            dt = datetime.fromisoformat(s)
            return dt.date().isoformat()
        except Exception:
            pass
        # Try to extract a yyyy-mm-dd pattern
        m = re.search(r"(\d{4}-\d{2}-\d{2})", s)
        if m:
            return m.group(1)
    return None


def enforce_schema(obj: Dict) -> Dict:
    """Return a new dict that strictly matches the schema.

    - Drop unknown keys
    - Insert missing keys with null
    - Cast values where possible
    - Ensure urgency is in allowed set or set to 'low' if unknown
    - Ensure deadline is ISO date string or None
    """
    out = strict_schema_template()

    # material_name
    out["material_name"] = obj.get("material_name") if isinstance(obj.get("material_name"), str) else (str(obj.get("material_name")) if obj.get("material_name") is not None else None)

    # quantity
    out["quantity"] = _to_number(obj.get("quantity"))

    # unit
    out["unit"] = obj.get("unit") if isinstance(obj.get("unit"), str) else (str(obj.get("unit")) if obj.get("unit") is not None else None)

    # project_name & location
    out["project_name"] = obj.get("project_name") if isinstance(obj.get("project_name"), str) else None
    out["location"] = obj.get("location") if isinstance(obj.get("location"), str) else None

    # urgency deterministic enforcement
    urgency = obj.get("urgency")
    if isinstance(urgency, str) and urgency.lower() in {"low", "medium", "high"}:
        out["urgency"] = urgency.lower()
    else:
        out["urgency"] = None

    # deadline
    out["deadline"] = _to_iso_date_or_null(obj.get("deadline"))

    return out