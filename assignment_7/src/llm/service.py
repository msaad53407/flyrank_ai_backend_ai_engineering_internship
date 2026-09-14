"""
LLM Service Layer for support message triage powered by LiteLLM / Gemini.
Implements:
- Versioned prompt loading (Stage 2)
- Explicit timeouts (Stage 4)
- Safe retry policy on transient errors only (timeouts, 429, 5xx) with backoff (Stage 4)
- Fast failure on auth/client errors (400, 401, 403) without retry (Stage 4)
- Code fence stripping & JSON extraction (Stage 3)
- Pydantic schema validation (Stage 3)
- One repair retry on malformed/invalid output (Stage 3)
- Quarantine logging & HTTP 422 on unrecoverable model failure (Stage 3)
- Structured cost and token logging (Stage 4)
- Kill switch support (Stage 4)
"""

import json
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException
import litellm
from litellm.exceptions import (
    APIConnectionError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
    ServiceUnavailableError,
    Timeout,
)
from pydantic import ValidationError

from src.config import (
    GEMINI_API_KEY,
    LLM_ENABLED,
    LLM_MODEL,
    LLM_STUB,
    LLM_TIMEOUT,
    LOGS_DIR,
    PROMPT_DIR,
)
from src.llm.schema import (
    FALLBACK_TRIAGE_OUTPUT,
    STUB_TRIAGE_OUTPUT,
    TriageOutput,
)

PROMPT_VERSION = "v1"
QUARANTINE_FILE = LOGS_DIR / "quarantine.jsonl"
COST_LOG_FILE = LOGS_DIR / "cost.log"

# Silence verbose litellm logging in tests
litellm.suppress_debug_info = True


def load_system_prompt(version: str = PROMPT_VERSION) -> str:
    """Load the versioned prompt markdown file."""
    prompt_path = PROMPT_DIR / f"triage-{version}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt specification not found at {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def clean_json_text(text: str) -> str:
    """Strip markdown code fences and extraneous leading/trailing conversational text."""
    trimmed = text.strip()
    # Remove markdown ```json ... ``` code fences
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", trimmed)
    if fence_match:
        return fence_match.group(1).strip()

    # Find first { and last }
    first_brace = trimmed.find("{")
    last_brace = trimmed.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return trimmed[first_brace : last_brace + 1].strip()

    return trimmed


def log_cost_event(
    prompt_version: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_ms: float,
    repair_count: int,
    status: str,
):
    """Write one structured JSON log line per call for token and cost observability."""
    total_tokens = prompt_tokens + completion_tokens
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": prompt_version,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "duration_ms": round(duration_ms, 2),
        "repair_count": repair_count,
        "status": status,
    }
    with open(COST_LOG_FILE, mode="a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


def log_quarantine_event(
    user_input: str,
    raw_model_output: str,
    error: str,
    prompt_version: str = PROMPT_VERSION,
):
    """Quarantine unrecoverable model outputs to logs/quarantine.jsonl for auditing."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": prompt_version,
        "user_input": user_input,
        "raw_model_output": raw_model_output,
        "error": error,
    }
    with open(QUARANTINE_FILE, mode="a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def call_model_with_policy(
    messages: list,
    model: str = LLM_MODEL,
    timeout: float = LLM_TIMEOUT,
    max_retries: int = 2,
) -> Tuple[str, Dict[str, int]]:
    """
    Call LLM provider via LiteLLM obeying strict retry and timeout policies:
    - Retries ONLY on transient errors: RateLimit (429), ServiceUnavailable (5xx), Connection/Timeout.
    - Uses exponential backoff with jitter.
    - NEVER retries on client/auth errors: BadRequest (400), Authentication (401).
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                temperature=0.0,
                timeout=timeout,
            )
            content = response.choices[0].message.content or ""
            usage = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", 0) if response.usage else 0,
                "completion_tokens": getattr(response.usage, "completion_tokens", 0) if response.usage else 0,
            }
            return content, usage

        except (AuthenticationError, BadRequestError) as e:
            # Client / Auth error: fail fast immediately without burning quota
            print(f"[LLM FAST FAIL] Auth/Client error {type(e).__name__}: {e}. No retry permitted.")
            raise HTTPException(
                status_code=401 if isinstance(e, AuthenticationError) else 400,
                detail=f"Provider authentication/client error: {str(e)}",
            )

        except (RateLimitError, ServiceUnavailableError, Timeout, APIConnectionError, Exception) as e:
            # Check if retry limit reached
            if attempt > max_retries:
                print(f"[LLM EXHAUSTED] Max retries ({max_retries}) reached. Failing: {e}")
                if isinstance(e, Timeout):
                    raise HTTPException(status_code=504, detail="Gateway Timeout contacting LLM provider")
                raise HTTPException(status_code=502, detail=f"LLM Provider unavailable: {str(e)}")

            # Obey Retry-After header if present on 429
            retry_after = getattr(e, "retry_after", None)
            if retry_after is not None:
                sleep_sec = float(retry_after)
            else:
                # Exponential backoff with random jitter: 1.0s, 2.0s, 4.0s + jitter
                sleep_sec = (1.0 * (2 ** (attempt - 1))) + random.uniform(0.1, 0.5)

            print(f"[LLM RETRY] Attempt {attempt} failed ({type(e).__name__}). Retrying in {sleep_sec:.2f}s...")
            time.sleep(sleep_sec)


def get_triage_decision(user_text: str, prompt_version: str = PROMPT_VERSION) -> TriageOutput:
    """
    Main orchestration pipeline for classifying a support message:
    1. Check stub and kill switch.
    2. Build prompt from versioned markdown.
    3. Call model with explicit timeout and retry policy.
    4. Clean, parse, and validate against Pydantic schema.
    5. Repair once if validation fails.
    6. Quarantine and return 422 if repair fails.
    7. Log cost and tokens.
    """
    if LLM_STUB:
        return STUB_TRIAGE_OUTPUT

    if not LLM_ENABLED:
        return FALLBACK_TRIAGE_OUTPUT

    system_prompt = load_system_prompt(prompt_version)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
    ]

    start_perf = time.perf_counter()
    repair_count = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0

    # Attempt 1
    raw_output, usage_1 = call_model_with_policy(messages)
    total_prompt_tokens += usage_1["prompt_tokens"]
    total_completion_tokens += usage_1["completion_tokens"]

    # Parse and Validate Attempt 1
    try:
        cleaned_json = clean_json_text(raw_output)
        data = json.loads(cleaned_json)
        validated = TriageOutput(**data)

        duration_ms = (time.perf_counter() - start_perf) * 1000.0
        log_cost_event(
            prompt_version=prompt_version,
            model=LLM_MODEL,
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            duration_ms=duration_ms,
            repair_count=0,
            status="success",
        )
        return validated

    except (json.JSONDecodeError, ValidationError, Exception) as first_err:
        repair_count += 1
        print(f"[REPAIR REQUIRED] First attempt failed validation: {first_err}. Initiating repair retry...")

        # Repair Retry (Attempt 2)
        repair_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": raw_output},
            {
                "role": "user",
                "content": (
                    f"Your previous answer was rejected for this reason: {first_err}.\n"
                    "Please return ONLY a corrected, valid JSON object matching the schema."
                ),
            },
        ]

        raw_output_repair, usage_2 = call_model_with_policy(repair_messages)
        total_prompt_tokens += usage_2["prompt_tokens"]
        total_completion_tokens += usage_2["completion_tokens"]

        try:
            cleaned_repair = clean_json_text(raw_output_repair)
            repair_data = json.loads(cleaned_repair)
            validated_repair = TriageOutput(**repair_data)

            duration_ms = (time.perf_counter() - start_perf) * 1000.0
            log_cost_event(
                prompt_version=prompt_version,
                model=LLM_MODEL,
                prompt_tokens=total_prompt_tokens,
                completion_tokens=total_completion_tokens,
                duration_ms=duration_ms,
                repair_count=1,
                status="repaired",
            )
            return validated_repair

        except Exception as final_err:
            duration_ms = (time.perf_counter() - start_perf) * 1000.0
            log_cost_event(
                prompt_version=prompt_version,
                model=LLM_MODEL,
                prompt_tokens=total_prompt_tokens,
                completion_tokens=total_completion_tokens,
                duration_ms=duration_ms,
                repair_count=1,
                status="quarantined",
            )
            log_quarantine_event(
                user_input=user_text,
                raw_model_output=raw_output_repair,
                error=str(final_err),
                prompt_version=prompt_version,
            )
            print(f"[QUARANTINED] Repair retry failed: {final_err}. Logged to quarantine.jsonl.")
            raise HTTPException(
                status_code=422,
                detail=f"Model output failed schema validation after repair attempt: {str(final_err)}",
            )
