"""Unit tests for schema & utils."""
import pytest
from ai_structurer.schema import enforce_schema
from ai_structurer.utils import attempt_local_json_repair, infer_urgency_from_deadline


def test_enforce_schema_casts_and_drops_extra():
    obj = {
        "material_name": "Screws",
        "quantity": "20",
        "unit": "boxes",
        "project_name": "Phoenix",
        "location": "Warehouse 12",
        "urgency": "HIGH",
        "deadline": "2026-01-15",
        "extra": "should be dropped",
    }
    out = enforce_schema(obj)
    assert out["material_name"] == "Screws"
    assert isinstance(out["quantity"], float)
    assert out["urgency"] == "high"
    assert out.get("extra") is None


def test_attempt_local_json_repair_single_obj():
    bad = "{ 'material_name': 'Screws', 'quantity': 20, }"
    repaired = attempt_local_json_repair(bad)
    assert repaired is not None
    assert isinstance(repaired, list)
    assert repaired[0]["material_name"] == "Screws"


def test_infer_urgency_from_deadline():
    # far future
    assert infer_urgency_from_deadline("2099-01-01") == "low"
    # near
    from datetime import datetime, timedelta

    d = (datetime.now() + timedelta(days=5)).date().isoformat()
    assert infer_urgency_from_deadline(d) == "high"

    d2 = (datetime.now() + timedelta(days=15)).date().isoformat()
    assert infer_urgency_from_deadline(d2) == "medium"
