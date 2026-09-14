"""
Strict Pydantic schemas and enums for the support message triage feature.
Enforces closed output categories and prevents unbounded free text.
"""

from enum import Enum
from pydantic import BaseModel, Field


class CategoryEnum(str, Enum):
    billing = "billing"
    bug = "bug"
    feature = "feature"
    other = "other"


class UrgencyEnum(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"


class TriageInput(BaseModel):
    """Input payload representing an inbound customer support message."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The customer support message (1-2000 characters).",
    )


class TriageOutput(BaseModel):
    """Strict schema-validated decision output."""
    category: CategoryEnum = Field(..., description="Target routing team category")
    urgency: UrgencyEnum = Field(..., description="Priority level for handling")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model certainty score 0.0-1.0")
    reason: str = Field(..., min_length=1, max_length=300, description="One concise sentence justification")


# Deterministic stub response (used when LLM_STUB=1)
STUB_TRIAGE_OUTPUT = TriageOutput(
    category=CategoryEnum.billing,
    urgency=UrgencyEnum.high,
    confidence=0.95,
    reason="[STUB MODE] Customer reported duplicate credit card charge requiring billing review.",
)

# Safe fallback response (used when LLM_ENABLED=false)
FALLBACK_TRIAGE_OUTPUT = TriageOutput(
    category=CategoryEnum.other,
    urgency=UrgencyEnum.normal,
    confidence=0.0,
    reason="[KILL SWITCH ACTIVE] Automated LLM triage is currently offline; routed to general queue.",
)
