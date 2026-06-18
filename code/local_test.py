"""Run the lead qualifier locally without Pipedream.

Usage:
    python code/local_test.py test-payloads/hot-lead.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lead_qualifier.gemini_client import call_gemini_with_retry
from lead_qualifier.parsing import parse_or_fallback
from lead_qualifier.prompts import build_qualification_prompt
from lead_qualifier.validators import validate_lead


def run(lead_file: str) -> None:
    with open(lead_file, "r") as f:
        lead = json.load(f)

    validate_lead(lead)
    prompt = build_qualification_prompt(lead)
    raw = call_gemini_with_retry(prompt)
    parsed = parse_or_fallback(raw)

    print(json.dumps({**lead, **parsed}, indent=2))


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "test-payloads/hot-lead.json"
    run(path)
    