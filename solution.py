"""Convenience wrapper for running the ai_structurer CLI as `solution.py`.

This file exists so reviewers can run `python solution.py` as a single-step entrypoint.
"""
import os
import argparse
from ai_structurer.cli import main as cli_main


def _run_as_script():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", default="test_inputs.txt")
    parser.add_argument("--output", "-o", default="outputs.json")
    parser.add_argument("--model", "-m", default="llama3-70b-8192")
    args = parser.parse_args()
    os.environ.setdefault("AI_STRUCTURER_USE_MOCK", os.environ.get("AI_STRUCTURER_USE_MOCK", "1"))
    # Delegate to package CLI
    cli_main()


if __name__ == "__main__":
    _run_as_script()
