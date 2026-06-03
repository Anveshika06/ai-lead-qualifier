import json
import time
import requests
import os

def handler(pd: "pipedream"):
    # Get the lead data from the webhook trigger
    lead = pd.steps["trigger"]["event"]["body"]
    
    # Input validation
    if not lead or "name" not in lead:
        raise ValueError("No lead data in request body. Send a POST with JSON containing name, email, phone, etc.")
    
    prompt = f"""You are an AI lead qualifier for a real estate sales team. Score this lead and respond ONLY with valid JSON, no markdown.

Lead data:
Name: {lead.get('name')}
Email: {lead.get('email')}
Phone: {lead.get('phone')}
Property Interest: {lead.get('property_interest')}
Message: {lead.get('message')}
Source: {lead.get('source')}

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

    api_key = os.environ["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }
    
    # Retry with exponential backoff for rate limits
    max_retries = 3
    response_data = None
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            
            if response.status_code == 429 and attempt < max_retries - 1:
                wait_seconds = 2 ** attempt * 2  # 2s, 4s, 8s
                print(f"Rate limited. Waiting {wait_seconds}s before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_seconds)
                continue
            
            response.raise_for_status()
            response_data = response.json()
            break
        except requests.exceptions.HTTPError as e:
            if attempt == max_retries - 1:
                raise
    
    # Extract the text the model returned
    raw_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
    
    # Parse the JSON output with graceful fallback
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        print(f"Failed to parse Gemini output: {raw_text}")
        parsed = {
            "lead_score": "Cold",
            "qualification_reason": f"Failed to parse AI response. Raw text: {raw_text[:200]}",
            "suggested_next_action": "Manual review required — AI output was malformed."
        }
    
    # Return everything combined for downstream steps
    return {**lead, **parsed}
