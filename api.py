"""FastAPI backend for the AI Lead Qualifier web app.
Reuses the same lead_qualifier package that powers the Pipedream workflow.
"""
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "code"))

from lead_qualifier.gemini_client import call_gemini_with_retry
from lead_qualifier.parsing import parse_or_fallback
from lead_qualifier.prompts import build_qualification_prompt

app = FastAPI(title="AI Lead Qualifier API")

# Allow the React dev server to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)


class Lead(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    property_interest: str = ""
    message: str = ""
    source: str = ""


@app.post("/qualify")
def qualify(lead: Lead):
    lead_dict = lead.model_dump()
    prompt = build_qualification_prompt(lead_dict)
    raw = call_gemini_with_retry(prompt)
    parsed = parse_or_fallback(raw)
    return parsed