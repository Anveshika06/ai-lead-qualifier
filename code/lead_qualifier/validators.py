"""Input validation for incoming lead webhook payloads."""


REQUIRED_FIELDS = ["name", "email", "phone", "message"]


class LeadValidationError(ValueError):
    """Raised when a lead payload fails validation."""
    pass


def validate_lead(lead: dict) -> None:
    """Validate that an incoming lead payload has the required fields.

    Args:
        lead: The dict parsed from the webhook request body.

    Raises:
        LeadValidationError: If the lead is missing required fields or
            has an empty name.
    """
    if not lead:
        raise LeadValidationError(
            "No lead data in request body. Send a POST with JSON containing "
            "name, email, phone, and message at minimum."
        )

    if not isinstance(lead, dict):
        raise LeadValidationError(
            f"Expected lead to be a JSON object, got {type(lead).__name__}."
        )

    missing = [field for field in REQUIRED_FIELDS if field not in lead]
    if missing:
        raise LeadValidationError(
            f"Missing required field(s): {', '.join(missing)}."
        )

    if not str(lead.get("name", "")).strip():
        raise LeadValidationError("Field 'name' cannot be empty.")