"""Pipedream handler for AI lead qualification.

This handler is intentionally thin. All real logic lives in the
lead_qualifier package so it can be tested in isolation.
"""

import os
import sys

# Make the lead_qualifier package importable from this script.
sys.path.insert(0, os.path.dirname(__file__))

from lead_qualifier.gemini_client import call_gemini_with_retry
from lead_qualifier.parsing import parse_or_fallback
from lead_qualifier.prompts import build_qualification_prompt
from lead_qualifier.validators import LeadValidationError, validate_lead


def handler(pd):
    """Entry point invoked by Pipedream on each webhook event.

    Args:
        pd: The Pipedream context object.

    Returns:
        A dict combining the incoming lead data with Gemini's qualification.
    """
    lead = pd.steps["trigger"]["event"]["body"]

    try:
        validate_lead(lead)
    except LeadValidationError as e:
        raise ValueError(str(e))

    prompt = build_qualification_prompt(lead)
    raw_response = call_gemini_with_retry(prompt)
    parsed = parse_or_fallback(raw_response)

    return {**lead, **parsed}

