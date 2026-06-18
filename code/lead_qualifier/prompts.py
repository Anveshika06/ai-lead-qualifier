"""Prompt templates for the lead qualifier.

Keeping prompts in their own module makes it easy to iterate on or A/B test
prompt variations without touching API or parsing logic.
"""


def build_qualification_prompt(lead: dict) -> str:
    """Construct the full qualification prompt for a given lead.

    Args:
        lead: Dict with keys name, email, phone, property_interest, message, source.

    Returns:
        The complete prompt string to send to Gemini.
    """
    return f"""You are an AI lead qualifier for a real estate sales team. \
Score this lead and respond ONLY with valid JSON, no markdown.

Lead data:
Name: {lead.get('name', '')}
Email: {lead.get('email', '')}
Phone: {lead.get('phone', '')}
Property Interest: {lead.get('property_interest', '')}
Message: {lead.get('message', '')}
Source: {lead.get('source', '')}

Return JSON with this exact shape:
{{
  "lead_score": "Hot" | "Warm" | "Cold",
  "qualification_reason": "1-2 sentences explaining the score, citing specific signals from the message",
  "suggested_next_action": "1 sentence recommending the next step for the sales rep"
}}

Scoring guide:
- Hot: clear timeline, budget signal, urgency, or financing certainty
- Warm: genuine interest but missing one key signal
- Cold: vague, no timeline, or low-intent"""