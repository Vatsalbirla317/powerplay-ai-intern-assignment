from ai_structurer.parser import parse_and_repair_json
from ai_structurer.schema import strict_schema_template


def test_parse_and_repair_fails_locally():
    bad = "This is not JSON and contains no data"
    out = parse_and_repair_json(bad)
    # Parser should return None when it cannot repair locally; caller (runner) applies fallback
    assert out is None
