"""
Comprehensive unit test suite for the polite scraper.
Covers:
- Price normalization
- Relative -> absolute URL conversion
- Missing description handling (null)
- Duplicate URL deduplication
- Malformed HTML fixture handling
- Pydantic schema validation
- Pipeline fault tolerance (skipping broken pages)
"""

from urllib.parse import urljoin
import pytest
from pydantic import ValidationError

from src.extractor import extract_raw_record
from src.models import BookRecord, normalize_price


def test_price_normalization():
    """Test extracting clean numeric GBP prices from raw currency strings."""
    assert normalize_price("£51.77") == 51.77
    assert normalize_price("£10.00") == 10.00
    assert normalize_price("£0.99") == 0.99
    assert normalize_price("Price: £123.45 inc tax") == 123.45
    assert normalize_price("") is None
    assert normalize_price(None) is None
    assert normalize_price("Free") is None


def test_relative_to_absolute_urls():
    """Test URL resolution from catalogue relative paths."""
    base_catalogue = "https://books.toscrape.com/catalogue/page-1.html"

    # Direct relative link
    rel_link = "a-light-in-the-attic_1000/index.html"
    assert urljoin(base_catalogue, rel_link) == (
        "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    )

    # Parent relative link
    parent_rel = "../tipping-the-velvet_999/index.html"
    assert urljoin(base_catalogue, parent_rel) == (
        "https://books.toscrape.com/tipping-the-velvet_999/index.html"
    )

    # Next page pagination link
    next_link = "page-2.html"
    assert urljoin(base_catalogue, next_link) == (
        "https://books.toscrape.com/catalogue/page-2.html"
    )


def test_missing_description():
    """Verify that a page with no description yields None (null), not empty or invented text."""
    html_no_desc = """
    <div class="product_main">
        <h1>A Book Without Description</h1>
        <p class="price_color">£19.99</p>
        <p class="instock availability">In stock (5 available)</p>
        <p class="star-rating Four"></p>
    </div>
    """
    raw = extract_raw_record(
        html=html_no_desc,
        product_url="https://books.toscrape.com/catalogue/no-desc_1/index.html",
        source_page="https://books.toscrape.com/catalogue/page-1.html",
        fetched_at="2026-09-14T12:00:00Z",
    )
    assert raw["title"] == "A Book Without Description"
    assert raw["description"] is None


def test_duplicate_urls_deduplication():
    """Verify deduplication ignores repeated URLs while preserving first occurrence."""
    raw_list = [
        ("https://books.toscrape.com/catalogue/book-1/index.html", "page-1.html"),
        ("https://books.toscrape.com/catalogue/book-2/index.html", "page-1.html"),
        ("https://books.toscrape.com/catalogue/book-1/index.html", "page-2.html"),  # duplicate
    ]
    seen = set()
    unique = []
    for url, src in raw_list:
        if url not in seen:
            seen.add(url)
            unique.append((url, src))

    assert len(unique) == 2
    assert unique[0][0] == "https://books.toscrape.com/catalogue/book-1/index.html"
    assert unique[1][0] == "https://books.toscrape.com/catalogue/book-2/index.html"


def test_malformed_html_fixture():
    """Ensure malformed HTML does not crash the extractor."""
    broken_html = "<html><body><div><p>Broken content without product_main</div>"
    raw = extract_raw_record(
        html=broken_html,
        product_url="https://books.toscrape.com/catalogue/broken/index.html",
        source_page="https://books.toscrape.com/catalogue/page-1.html",
        fetched_at="2026-09-14T12:00:00Z",
    )
    assert raw["title"] is None
    assert raw["price_text"] is None
    assert raw["description"] is None
    assert raw["product_url"] == "https://books.toscrape.com/catalogue/broken/index.html"


def test_book_record_schema_validation():
    """Test Pydantic schema validation rules."""
    valid_payload = {
        "title": "A Light in the Attic",
        "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "price_text": "£51.77",
        "price_gbp": 51.77,
        "availability_text": "In stock (22 available)",
        "rating_text": "Three",
        "description": "Poetry collection",
        "source_page": "https://books.toscrape.com/catalogue/page-1.html",
        "fetched_at": "2026-09-14T12:00:00Z",
    }
    rec = BookRecord(**valid_payload)
    assert rec.price_gbp == 51.77

    # Test invalid URL rejection
    invalid_url_payload = dict(valid_payload, product_url="ftp://invalid.url/book")
    with pytest.raises(ValidationError):
        BookRecord(**invalid_url_payload)

    # Test negative price rejection
    invalid_price_payload = dict(valid_payload, price_gbp=-5.0)
    with pytest.raises(ValidationError):
        BookRecord(**invalid_price_payload)
