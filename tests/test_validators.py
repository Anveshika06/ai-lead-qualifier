"""Tests for lead_qualifier.validators."""

import pytest

from lead_qualifier.validators import LeadValidationError, validate_lead


def test_valid_lead_passes():
    lead = {
        "name": "Sarah Johnson",
        "email": "sarah@example.com",
        "phone": "+1-412-555-0142",
        "message": "Cash buyer, need to close in 6 weeks.",
    }
    validate_lead(lead)  # should not raise


def test_empty_lead_fails():
    with pytest.raises(LeadValidationError, match="No lead data"):
        validate_lead({})


def test_missing_field_fails():
    lead = {"name": "Sarah", "email": "s@example.com"}
    with pytest.raises(LeadValidationError, match="Missing required field"):
        validate_lead(lead)


def test_empty_name_fails():
    lead = {"name": "   ", "email": "s@example.com", "phone": "555", "message": "hi"}
    with pytest.raises(LeadValidationError, match="cannot be empty"):
        validate_lead(lead)
