"""Tests for lead_qualifier.prompts."""

from lead_qualifier.prompts import build_qualification_prompt


def test_prompt_includes_lead_fields():
    lead = {
        "name": "Sarah Johnson",
        "email": "sarah@example.com",
        "phone": "555",
        "property_interest": "3BR Downtown",
        "message": "Cash buyer.",
        "source": "Zillow",
    }
    prompt = build_qualification_prompt(lead)
    assert "Sarah Johnson" in prompt
    assert "Cash buyer." in prompt
    assert "Zillow" in prompt


def test_prompt_contains_scoring_guide():
    prompt = build_qualification_prompt(
        {"name": "x", "email": "x", "phone": "x", "message": "x"}
    )
    assert "Hot:" in prompt
    assert "Warm:" in prompt
    assert "Cold:" in prompt