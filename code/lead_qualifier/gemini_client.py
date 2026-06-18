"""Thin client for the Gemini API with retry-on-rate-limit logic."""

import os
import time
from typing import Any

import requests


GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={api_key}"
)

DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE_SECONDS = 2


class GeminiClientError(RuntimeError):
    """Raised when the Gemini API call fails after retries."""
    pass


def call_gemini_with_retry(
    prompt: str,
    api_key: str | None = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    temperature: float = 0.2,
) -> str:
    """Call Gemini with the given prompt, retrying on rate limits.

    Args:
        prompt: The full prompt string to send.
        api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
        max_retries: Max retry attempts on rate-limited (429) responses.
        temperature: Sampling temperature (lower = more deterministic).

    Returns:
        The raw text returned by Gemini.

    Raises:
        GeminiClientError: If the key is missing or all retries fail.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise GeminiClientError("GEMINI_API_KEY is not set.")

    url = GEMINI_URL_TEMPLATE.format(model=GEMINI_MODEL, api_key=key)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json",
        },
    }

    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 429 and attempt < max_retries - 1:
                wait_seconds = DEFAULT_BACKOFF_BASE_SECONDS ** (attempt + 1)
                print(
                    f"Rate limited (attempt {attempt + 1}/{max_retries}). "
                    f"Waiting {wait_seconds}s before retry."
                )
                time.sleep(wait_seconds)
                continue

            response.raise_for_status()
            return _extract_text(response.json())

        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt == max_retries - 1:
                break
            time.sleep(DEFAULT_BACKOFF_BASE_SECONDS ** (attempt + 1))

    raise GeminiClientError(
        f"Gemini API failed after {max_retries} attempts: {last_error}"
    )


def _extract_text(response_data: dict[str, Any]) -> str:
    """Extract the model's text output from a Gemini response payload."""
    try:
        return response_data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise GeminiClientError(f"Unexpected Gemini response structure: {e}")