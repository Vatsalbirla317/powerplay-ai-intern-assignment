import os
from ai_structurer.runner import process_all_inputs


def test_process_all_inputs_with_mock(monkeypatch):
    # Use mock mode to avoid real LLM calls
    monkeypatch.setenv("AI_STRUCTURER_USE_MOCK", "1")
    records = process_all_inputs("test_inputs.txt")
    assert isinstance(records, list)
    assert len(records) >= 1
    # Ensure keys strictly match schema
    keys = {"material_name", "quantity", "unit", "project_name", "location", "urgency", "deadline"}
    for r in records:
        assert set(r.keys()) == keys


def test_process_all_inputs_llm_retry(monkeypatch):
    calls = {"n": 0}

    def fake_call(prompt, model="", max_tokens=2048, retry_with_correction=True):
        # First call returns malformed JSON, second call returns valid JSON
        calls["n"] += 1
        if calls["n"] == 1:
            return "NOT JSON"
        return '[{"material_name":"Paint","quantity":10,"unit":"liters","project_name":"Aurora","location":null,"urgency":"low","deadline":"2025-12-31"}]'

    monkeypatch.setenv("AI_STRUCTURER_USE_MOCK", "0")
    monkeypatch.setattr("ai_structurer.runner.call_groq_llm", fake_call)

    records = process_all_inputs("test_inputs.txt")
    # After first malformed output, the runner retries and should get parsed result
    assert any(r["material_name"] in {"Paint", "Screws"} for r in records)


def test_process_all_inputs_final_fallback(monkeypatch):
    # Both initial and correction responses are bad → fallback to null-filled schema
    def always_bad(prompt, model="", max_tokens=2048, retry_with_correction=True):
        return "garbage"

    monkeypatch.setenv("AI_STRUCTURER_USE_MOCK", "0")
    monkeypatch.setattr("ai_structurer.runner.call_groq_llm", always_bad)

    records = process_all_inputs("test_inputs.txt")
    # All records will be fallback null-filled objects
    for r in records:
        assert r["material_name"] is None
        assert r["quantity"] is None
        assert r["urgency"] is None or r["urgency"] == "low"
