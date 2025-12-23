import json
import re
from pathlib import Path

EXPECTED_KEYS = [
    "material_name",
    "quantity",
    "unit",
    "project_name",
    "location",
    "urgency",
    "deadline",
]

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

p = Path("outputs.json")
if not p.exists():
    raise SystemExit("ERROR: outputs.json not found")

text = p.read_text(encoding="utf-8")
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    raise SystemExit(f"ERROR: outputs.json is not valid JSON: {e}")

if not isinstance(data, list):
    raise SystemExit("ERROR: outputs.json must be a JSON array")

for i, obj in enumerate(data):
    if not isinstance(obj, dict):
        raise SystemExit(f"ERROR: item {i} is not an object")
    keys = list(obj.keys())
    if set(keys) != set(EXPECTED_KEYS):
        extra = set(keys) - set(EXPECTED_KEYS)
        missing = set(EXPECTED_KEYS) - set(keys)
        raise SystemExit(f"ERROR: item {i} keys mismatch. extra={sorted(extra)}, missing={sorted(missing)}")
    for k in EXPECTED_KEYS:
        v = obj.get(k)
        # quantity must be number or null
        if k == "quantity":
            if v is not None and not isinstance(v, (int, float)):
                raise SystemExit(f"ERROR: item {i} field 'quantity' must be number or null, got {type(v).__name__}")
        # urgency must be one of allowed or null
        if k == "urgency":
            if v is not None and v not in {"low", "medium", "high"}:
                raise SystemExit(f"ERROR: item {i} field 'urgency' invalid value: {v}")
        # deadline must be ISO or null
        if k == "deadline":
            if v is not None:
                if not isinstance(v, str) or not ISO_RE.match(v):
                    raise SystemExit(f"ERROR: item {i} field 'deadline' must be ISO YYYY-MM-DD or null, got: {v}")

print("OK: outputs.json is valid and conforms to the schema")