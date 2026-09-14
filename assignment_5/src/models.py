"""
Pydantic data models for normalized book records and run reports.
"""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


def normalize_price(price_text: Optional[str]) -> Optional[float]:
    """
    Normalizes a price string like '£51.77' into float 51.77.
    Returns None if no numeric price is found.
    """
    if not price_text:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", price_text)
    if match:
        return float(match.group(1))
    return None


class BookRecord(BaseModel):
    """
    Schema for a cleaned, validated book record.
    Raw fields and normalized fields live side by side.
    """
    title: str = Field(..., min_length=1, description="Book title")
    product_url: str = Field(..., description="Canonical product URL")
    price_text: str = Field(..., min_length=1, description="Original price string")
    price_gbp: float = Field(..., ge=0.0, description="Normalized numeric price in GBP")
    availability_text: str = Field(..., min_length=1, description="Stock availability string")
    rating_text: Optional[str] = Field(None, description="Star rating text (e.g. Three)")
    description: Optional[str] = Field(None, description="Book description, or null if missing")
    source_page: str = Field(..., description="Catalogue provenance page URL")
    fetched_at: str = Field(..., description="ISO 8601 UTC timestamp of fetch")

    @field_validator("product_url", "source_page")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError(f"URL must start with http:// or https://, got: {v}")
        return v


class RunReport(BaseModel):
    """Execution summary statistics for a scraper run."""
    start_time: str
    duration_seconds: float
    catalogue_pages: int
    books_discovered: int
    pages_fetched: int
    cache_hits: int
    valid_records: int
    invalid_records: int
    failed_pages: int
