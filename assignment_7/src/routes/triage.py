"""
API Route for support message triage.
"""

from fastapi import APIRouter, HTTPException
from src.config import LLM_ENABLED, LLM_STUB
from src.llm.schema import (
    FALLBACK_TRIAGE_OUTPUT,
    STUB_TRIAGE_OUTPUT,
    TriageInput,
    TriageOutput,
)

router = APIRouter()


@router.post("/triage", response_model=TriageOutput, status_code=200)
def triage_support_message(payload: TriageInput):
    """
    Classify an inbound support message into category, urgency, confidence, and reason.
    Rejects invalid inputs before any LLM call is initiated.
    """
    # 1. Check Stub Mode
    if LLM_STUB:
        return STUB_TRIAGE_OUTPUT

    # 2. Check Kill Switch
    if not LLM_ENABLED:
        return FALLBACK_TRIAGE_OUTPUT

    # In Stage 1, if not in stub mode, return stub or call service in future stages
    try:
        from src.llm.service import get_triage_decision
        return get_triage_decision(payload.text)
    except ImportError:
        # Before Stage 2 service is created, return STUB
        return STUB_TRIAGE_OUTPUT
