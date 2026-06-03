\# AI Lead Qualifier — Real Estate



A webhook-triggered workflow that qualifies inbound real estate leads in real time using Google Gemini (Hot / Warm / Cold), writes structured records to an Airtable CRM, and returns scoring + next action as JSON — mirroring the lead-qualification + CRM-update pipeline used by modern AI sales platforms.



Built on the Pipedream free tier in a day, as a hands-on exploration of agentic LLM workflows.



\---



\## 🚀 Try it yourself



Clone this workflow into your own Pipedream account with one click:



👉 \*\*\[Open in Pipedream](https://pipedream.com/new?h=tch\_jPfzZx)\*\*



After cloning, you'll need to:

1\. Add a `GEMINI\_API\_KEY` in Pipedream → Settings → Environment Variables

2\. Connect your Airtable account in the Airtable step

3\. Update the Base ID and Table name to point to your own Airtable Leads table

4\. Deploy, then POST a lead to your new webhook URL



\---



\## Architecture



```

┌─────────────┐    ┌──────────────────┐    ┌──────────────┐    ┌──────────────┐

│   Webhook   │──> │ qualify\_lead\_    │──> │ get\_record\_  │──> │ return\_http\_ │

│  (trigger)  │    │ with\_gemini      │    │ or\_create    │    │ response     │

│   POST      │    │ (Python +        │    │ (Airtable)   │    │ (HTTP 200    │

│   JSON      │    │  Gemini 2.5)     │    │              │    │  + JSON)     │

└─────────────┘    └──────────────────┘    └──────────────┘    └──────────────┘

```



\## Stack



\- \*\*Pipedream\*\* — workflow orchestration (free tier)

\- \*\*Google Gemini 2.5 Flash-Lite\*\* — LLM with structured JSON output

\- \*\*Airtable\*\* — CRM destination

\- \*\*Python\*\* — custom logic, retry-with-backoff for rate limits, graceful JSON-parse fallback



\## What it does



1\. Receives a lead payload from any source (Zillow, Realtor.com, website form, etc.) via webhook

2\. Prompts Gemini to classify the lead as \*\*Hot / Warm / Cold\*\*, with a reason and suggested next action

3\. Writes the structured record to Airtable in real time

4\. Returns the lead ID, score, and recommended next action to the caller as JSON



\## Demo



📹 \*Loom walkthrough coming soon\*



\### Screenshots



\*\*Pipedream workflow canvas\*\*

!\[Workflow](screenshots/01-pipedream-canvas.png)



\*\*Qualified leads in Airtable\*\*

!\[Airtable](screenshots/02-airtable-leads.png)



\*\*Example request and response\*\*

!\[Response](screenshots/03-powershell-response.png)



\## Example request



```bash

curl -X POST https://your-webhook.m.pipedream.net \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d @test-payloads/hot-lead.json

```



Or in PowerShell:



```powershell

$body = Get-Content test-payloads/hot-lead.json -Raw

Invoke-RestMethod -Uri "https://your-webhook.m.pipedream.net" -Method Post -Body $body -ContentType "application/json"

```



\## Example response



```json

{

&#x20; "success": true,

&#x20; "lead\_id": "recHNzStpKlE4v3LJ",

&#x20; "score": "Hot",

&#x20; "next\_action": "Call Sarah within 24 hours to discuss closing timeline and verify proof of funds."

}

```



\## Repo contents



| Path | Description |

|---|---|

| `code/qualify\_lead\_with\_gemini.py` | The Gemini step — input validation, prompt design, retry with exponential backoff, graceful JSON-parse fallback |

| `screenshots/` | Demo screenshots of the workflow, Airtable, and a sample request |

| `test-payloads/` | Three sample lead JSONs (hot / warm / cold) you can POST to test |



\## Engineering decisions worth noting



\- \*\*Model migration:\*\* Originally built on `gemini-2.0-flash`, which Google deprecated mid-build. Migrated to `gemini-2.5-flash-lite` — a reminder that model-agnostic code matters in production.

\- \*\*Rate limit handling:\*\* Wrapped the Gemini call in retry-with-exponential-backoff (2s → 4s → 8s) so the workflow degrades gracefully when free-tier quota hits.

\- \*\*Robust JSON parsing:\*\* LLMs occasionally return malformed JSON. The code falls back to a flagged "Cold + manual review" record rather than crashing the pipeline.

\- \*\*Secrets handling:\*\* API keys live in Pipedream environment variables, not in code.

\- \*\*Input validation:\*\* Bad webhooks fail with a clear error message instead of an opaque undefined-property error.



\## What it taught me



The hardest part wasn't the LLM call — it was thinking through what happens when \*anything\* in the pipeline misbehaves: rate limits, deprecated models, malformed JSON, empty webhooks, edge-case leads. Production AI is mostly about handling the unhappy paths cleanly.



\---



Built by \*\*\[Anveshika Kamble](mailto:ark411@pitt.edu)\*\* — MS Computer Science, University of Pittsburgh

