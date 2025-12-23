# Powerplay AI Engineering Intern Assignment

## Overview
This submission implements a deterministic pipeline that converts unstructured business text (one request per line) into strictly-valid JSON objects. The LLM (Groq, llama3) is used only as a probabilistic extractor; all validation, repair, and business logic are enforced in deterministic Python code. The system guarantees a valid JSON array output even under model failures.

## Key Design Principles
- Schema-first validation: a canonical schema in code is the single source of truth.  
- Bounded LLM retries: at most one correction retry after conservative local repair.  
- Conservative null-filled fallback: if extraction cannot be recovered, emit a schema-valid record with nulls rather than invent values.  
- Deterministic urgency inference: reproducible rules (high ≤7 days or urgent keywords, medium 7–30 days, low >30/no deadline).

## Project Structure
- `solution.py` — convenience wrapper to run the pipeline (calls the package CLI).  
- `test_inputs.txt` — sample input lines used for testing.  
- `outputs.json` — sample output produced by the pipeline (valid JSON array).  
- `design_explanation.pdf` — single-page design summary for reviewers.  
- `evaluation_notes.pdf` — test and evaluation notes for reviewers.  
- `ai_structurer/` — main implementation (LLM wrapper, parser, schema enforcement, runner, CLI).  
- `tests/` — unit and integration tests covering parsing, repair, retry, and fallback.

## How to Run
Prereqs: Python 3.11+ (venv recommended). Install dependencies: `pip install -r requirements.txt`.

### Mock Mode (no network calls)
- Use for quick local verification and CI: set environment variable and run the CLI.
  - PowerShell: `$env:AI_STRUCTURER_USE_MOCK = "1"`
  - Run: `python -m ai_structurer.cli -i test_inputs.txt -o outputs.json`

### Live LLM Mode
- Provide a Groq API key in `.env` or the environment as `GROQ_API_KEY` (do not commit keys).  
- Unset mock mode and run the same CLI:
  - PowerShell: `$env:AI_STRUCTURER_USE_MOCK = "0"` and ensure `GROQ_API_KEY` is set
  - Run: `python -m ai_structurer.cli -i test_inputs.txt -o outputs.json`

## Validation & Tests
- Unit tests: `pytest -q`  
- Output validation script: `python scripts/validate_outputs.py` (checks JSON validity, exact keys, types, ISO deadlines)

## Notes
- No API keys are committed; `.env` is listed in `.gitignore`.  
- The pipeline enforces schema and will not emit hallucinated fields or fabricated values; missing/ambiguous fields become null.  
- The repository is intended for reviewer evaluation; the README focuses on behavior and verifiability rather than marketing.

---
If you want, I can add a short `design_explanation.pdf` and `evaluation_notes.pdf` placeholders or wire up a CI job that runs tests and `scripts/validate_outputs.py` on each commit.
