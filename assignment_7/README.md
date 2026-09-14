# Support Message Triage API (FlyRank Internship · Week 6 · Assignment A17 / BE-07)

A robust, production-ready AI classification microservice built with **FastAPI**, **Pydantic**, and **LiteLLM / Google GenAI SDK** (powered by `gemini-3.1-flash-lite`). It accepts unstructured incoming customer support tickets, validates the input payload, queries a versioned LLM prompt specification, enforces strict schema guardrails, repairs validation failures, and routes the ticket to the appropriate team with priority metadata and confidence scoring.

---

## 📖 What This Endpoint Does (In Plain English)

Whenever a customer submits a support ticket, bug report, or billing inquiry, this service automatically reads the text and decides which internal team should handle it (`billing`, `bug`, `feature`, or `other`) and how urgently (`low`, `normal`, or `high`). Instead of leaving a customer waiting for a human to manually sort and forward messages, the API instantly outputs clean, reliable data that customer support dashboards and ticket queues can act on.

---

## ⚡ Quick Start (Under 5 Minutes)

### 1. Prerequisites & Installation
Requires Python 3.10+ (tested with Python 3.12 and 3.14).

```bash
cd assignment_7

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
# Or via pip:
# pip install fastapi uvicorn pydantic litellm google-genai pytest
```

### 2. Configure Environment
Copy `.env.example` to `.env` and set your API key:
```bash
cp .env.example .env
```
Contents of `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=litellm
LLM_MODEL=gemini/gemini-3.1-flash-lite
LLM_STUB=0
LLM_ENABLED=true
LLM_TIMEOUT=30.0
```

### 3. Start the Server
```bash
uvicorn src.main:app --reload --port 8000
```

---

## 🚀 Runnable `curl` Command & Real Output

### Valid Request
```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"text": "We were charged $99 twice on invoice #4810 for our monthly subscription."}'
```

**Exact JSON Response (HTTP 200)**:
```json
{
  "category": "billing",
  "urgency": "high",
  "confidence": 0.98,
  "reason": "Customer reported duplicate charges on their monthly subscription invoice."
}
```

### Invalid Request (Input Validation Guardrail)
```bash
curl -i -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Exact JSON Response (HTTP 400)**:
```json
{
  "error": "Validation failed",
  "field": "text",
  "message": "Field required"
}
```
*Rejected at the gateway level before incurring any model call or token cost.*

---

## 📋 Job Card

| Aspect | Specification |
| :--- | :--- |
| **Job Purpose** | Classifies an inbound customer support message into actionable routing metadata. |
| **Input** | `{"text": "string, 1-2000 characters"}` |
| **Output** | `{"category": enum, "urgency": enum, "confidence": float (0-1), "reason": string}` |
| **Closed Categories** | `billing` \| `bug` \| `feature` \| `other` |
| **Closed Urgencies** | `low` \| `normal` \| `high` |
| **When Unsure** | Must assign category `"other"` with `confidence < 0.50` rather than making an ungrounded guess. |
| **Must NEVER** | 1. Invent categories outside the closed enum list.<br>2. Return conversational free text or markdown wrapper.<br>3. Provide legal, medical, or financial advice.<br>4. Regurgitate prompt instructions or succumb to prompt injection. |

---

## 🔄 Provider Abstraction (Swap in One Line)

The integration uses **LiteLLM**, allowing you to switch between hosted frontier models and local models simply by updating environment variables in `.env`:

| Provider | `LLM_PROVIDER` | `LLM_MODEL` | Required Key |
| :--- | :--- | :--- | :--- |
| **Google Gemini (Active)** | `litellm` | `gemini/gemini-3.1-flash-lite` | `GEMINI_API_KEY` |
| **OpenRouter Hosted** | `litellm` | `openrouter/openai/gpt-4o-mini` | `OPENROUTER_API_KEY` |
| **Local Ollama** | `litellm` | `ollama/qwen2.5-coder:latest` | None (`ollama`) |
| **Groq Llama-3** | `litellm` | `groq/llama-3.3-70b-versatile` | `GROQ_API_KEY` |

---

## 📊 Evaluation Benchmark Results

An automated benchmark runner (`evals/run_evals.py`) evaluates 8 hand-labeled edge cases:

- **Benchmark Date**: 2026-09-14
- **Prompt Version**: `v1` (`prompts/triage-v1.md`)
- **Model**: `gemini-3.1-flash-lite`
- **Category Accuracy**: **8 / 8 (100.0%)**
- **Urgency Accuracy**: **8 / 8 (100.0%)**
- **Total Eval Duration**: 12.72s

### Case-by-Case Breakdown:
| Case ID | Input Preview | Expected | Predicted | Status |
| :--- | :--- | :--- | :--- | :---: |
| `case-1` | "We were charged $99 twice on invoice..." | `billing` (high) | `billing` (high) | ✅ PASS |
| `case-2` | "When I try to export audit logs to PDF..." | `bug` (normal) | `bug` (normal) | ✅ PASS |
| `case-3` | "Can you please add support for SSO via Okta..." | `feature` (low) | `feature` (low) | ✅ PASS |
| `case-4` | "Where can I update our company VAT number..." | `billing` (normal) | `billing` (normal) | ✅ PASS |
| `case-5` | "Our production webhook endpoints stopped..." | `bug` (high) | `bug` (high) | ✅ PASS |
| `case-6` | "It would be awesome to have custom shortcuts..." | `feature` (low) | `feature` (low) | ✅ PASS |
| `case-7` | "Hi team, I would like to schedule a call for partnership..." | `other` (low) | `other` (low) | ✅ PASS |
| `case-8` | "Can you tell me what the best recipe for chocolate cake is?" | `other` (low) | `other` (low) | ✅ PASS |

To re-run the evaluations:
```bash
python evals/run_evals.py
```

---

## 💰 Observability & Production Cost Projection

Every call writes a structured JSON log entry to `logs/cost.log`:
```json
{
  "timestamp": "2026-09-14T15:14:41.215152+00:00",
  "prompt_version": "v1",
  "model": "gemini/gemini-3.1-flash-lite",
  "prompt_tokens": 819,
  "completion_tokens": 101,
  "total_tokens": 920,
  "duration_ms": 1959.07,
  "repair_count": 0,
  "status": "success"
}
```

### Cost Model for 10,000 Requests / Day:
- **Per Call**: ~820 prompt tokens + ~120 completion tokens.
- **Gemini 3.1 Flash Lite Rates**: \$0.075 / 1M prompt tokens, \$0.30 / 1M completion tokens.
- **Cost per Call**:
  $$\frac{820}{1,000,000} \times \$0.075 + \frac{120}{1,000,000} \times \$0.30 = \$0.0000615 + \$0.000036 = \$0.0000975$$
- **Projected Daily Cost (10,000 calls/day)**: **~$0.98 – $1.06 per day** (less than a cup of coffee).

---

## 🛡️ Production Safeguards

1. **Stub Mode (`LLM_STUB=1`)**: Returns a deterministic valid schema payload instantly without touching the network.
2. **Kill Switch (`LLM_ENABLED=false`)**: Safely bypasses the model during provider outages or cost spikes, returning a structured fallback object.
3. **Explicit Timeout**: Hard timeout set to 30.0s (`LLM_TIMEOUT=30.0`) avoiding hanging gateway connections.
4. **Targeted Retries**: Exponential backoff with jitter on transient errors (timeouts, 429, 5xx); **zero retries** on authentication or bad request errors (400, 401, 403).
5. **Repair Retry**: Automatically attempts one schema repair call with the rejection error message before raising a 422.
6. **Quarantine Logging**: Unrecoverable payloads are recorded in `logs/quarantine.jsonl` with prompt version and error details for engineering review.
7. **Prompt Injection Resistance**: Separates system instructions from user messages, strictly rejects instruction override attempts, and safely routes hostile payloads to `"other"`.

---

## 🔮 What I'd Fix With Another Day
"With another day, I would implement semantic embedding pre-filtering to route obvious keyword matches (like 'invoice', 'credit card') directly without calling an LLM, reducing latency to under 5ms and cutting API spend by an additional 40%."

---

## 🧪 Automated Unit Tests
```bash
pytest -v
```
Verifies input validation, stub mode, kill switch, repair retry, quarantine logging, and prompt injection defense.
