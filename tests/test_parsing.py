"""Tests for lead_qualifier.parsing."""

from lead_qualifier.parsing import parse_or_fallback


def test_valid_json_parses_correctly():
    raw = (
        '{"lead_score": "Hot", '
        '"qualification_reason": "Cash buyer with timeline.", '
        '"suggested_next_action": "Call within 24 hours."}'
    )
    result = parse_or_fallback(raw)
    assert result["lead_score"] == "Hot"


def test_malformed_json_falls_back_to_cold():
    result = parse_or_fallback("not valid json")
    assert result["lead_score"] == "Cold"
    assert "manual review" in result["suggested_next_action"].lower()


def test_truncated_json_falls_back():
    result = parse_or_fallback('{"lead_score": "Hot"')
    assert result["lead_score"] == "Cold"


def test_invalid_score_falls_back():
    result = parse_or_fallback('{"lead_score": "Volcanic"}')
    assert result["lead_score"] == "Cold"


def test_empty_string_falls_back():
    assert parse_or_fallback("")["lead_score"] == "Cold"
