"""Parse and validate Gemini's JSON output, with graceful fallback."""

import json


VALID_SCORES = {"Hot", "Warm", "Cold"}


def parse_or_fallback(raw_text: str) -> dict[str, str]:
    """Parse Gemini's JSON output, falling back to a safe default if malformed.

    LLMs occasionally return broken JSON (missing brackets, wrong types, extra
    commentary). Rather than crashing the pipeline, this returns a flagged
    'Cold + manual review' record so the workflow keeps running and failures
    can be audited later.

    Args:
        raw_text: The raw string returned by Gemini.

    Returns:
        A dict with keys: lead_score, qualification_reason, suggested_next_action.
    """
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError):
        return _fallback_record(raw_text)

    if not isinstance(parsed, dict):
        return _fallback_record(raw_text)

    score = parsed.get("lead_score")
    if score not in VALID_SCORES:
        return _fallback_record(
            raw_text, reason=f"AI returned invalid lead_score: {score!r}"
        )

    return {
        "lead_score": score,
        "qualification_reason": parsed.get("qualification_reason", ""),
        "suggested_next_action": parsed.get("suggested_next_action", ""),
    }


def _fallback_record(raw_text: str, reason: str | None = None) -> dict[str, str]:
    """Return a safe default record when parsing fails."""
    preview = (raw_text or "")[:200]
    explanation = reason or f"Failed to parse AI response. Raw text: {preview}"
    return {
        "lead_score": "Cold",
        "qualification_reason": explanation,
        "suggested_next_action": "Manual review required — AI output was malformed.",
    }