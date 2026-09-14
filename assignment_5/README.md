# The Polite Scraper (FlyRank Internship · Week 5 · Assignment A9 / BE-05)

A production-grade, polite scraping pipeline built with Python, Requests, BeautifulSoup4, and Pydantic. It autonomously navigates the first three catalogue pages of **Books to Scrape**, visits all 60 book detail pages, turns messy raw HTML into validated, clean JSON records, survives page failures gracefully, and outputs an honest execution run report.

---

## 🎯 Target Classification (Stage 0 Checkpoint)

- **Target Site**: [Books to Scrape](https://books.toscrape.com/)
- **Nature of Target**: An official, public practice sandbox explicitly created for developers to learn and practice web scraping techniques without causing harm or violating terms of service.
- **Scraping Scope**: Exactly the first **3 catalogue pages** (`catalogue/page-1.html` through `catalogue/page-3.html`), covering **60 unique book detail pages**.
- **Data Collected**:
  - `title`: Book title string
  - `product_url`: Canonical absolute URL
  - `price_text`: Raw price string (e.g. `£51.77`)
  - `price_gbp`: Normalized floating-point price in GBP (e.g. `51.77`)
  - `availability_text`: Raw stock availability string
  - `rating_text`: Star rating text (`One`, `Two`, `Three`, `Four`, `Five`)
  - `description`: Book description string (or `null` if omitted)
  - `source_page`: Provenance URL of catalogue page where the book link was discovered
  - `fetched_at`: ISO 8601 UTC timestamp of fetch
- **Justification**: Collecting this data is appropriate because Books to Scrape is explicitly designated as a practice sandbox for educational scraping.
- **`robots.txt` Investigation**:
  - Request: `GET https://books.toscrape.com/robots.txt`
  - Result: HTTP `404 Not Found` — **no robots file found**.
  - Note: A missing `robots.txt` does not imply carte blanche permission; on production websites, a missing file must never replace reading the site's Terms of Service and API availability. Because Books to Scrape is an explicit sandbox, polite automated scraping is permitted.

> **Mandatory Pledge**:
> "I will not reuse this code on another site without checking its rules and terms first."

---

## ⚡ Quick Start (Run in under 5 minutes)

### 1. Prerequisites & Installation
Requires Python 3.10 or newer (tested with Python 3.12 and 3.14).

```bash
# Navigate to assignment directory
cd assignment_5

# Set up virtual environment using uv or venv
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
# Alternatively with pip:
# pip install requests beautifulsoup4 pydantic pytest
```

### 2. One Copy-Pasteable Run Command
```bash
python -m src.main
```
This executes the full polite pipeline:
- Discovers 60 unique book URLs across the first 3 catalogue pages.
- Reads from local cache or fetches detail pages politely with rate limiting.
- Normalizes prices into `price_gbp` numbers and validates records against the Pydantic schema.
- Emits output artifacts:
  - `output/books.json` (60 validated records)
  - `output/books.csv` (tabular CSV export)
  - `output/errors.json` (quarantined invalid records)
  - `output/run-report.json` (execution metrics)

---

## 🔬 Stage Checkpoints Verification

You can run each stage checkpoint independently via CLI flags:

| Stage | Command | Description / Expected Checkpoint |
| :--- | :--- | :--- |
| **Stage 1** | `python -m src.main --stage1` | Fetches catalogue page 1 (`[FETCH]` on first run, `[CACHE HIT]` on second run with byte size). |
| **Stage 2** | `python -m src.main --stage2` | Discovers catalogue pages 1-3. Output: `catalogue_pages=3, discovered=60, unique_urls=60`. |
| **Stage 3** | `python -m src.main --stage3` | Visits all 60 books. Prints sample 8-field raw record and `detail_pages=60`. |
| **Stage 4** | `python -m src.main --stage4` | Cleans, schema-validates, and stores records in `output/books.json`. Idempotent on rerun (always 60 records). |
| **Stage 5** | `python -m src.main --stage5` | Injects a deliberate 404 URL. Verifies 60 good records survive and `failed_pages: 1`. |

---

## 🛡️ Politeness & Resilience Rules

1. **Honest User-Agent**: Every live request sends:
   ```http
   User-Agent: FlyRankInternshipA9/1.0 (+https://github.com/msaad53407/flyrank_ai_backend_ai_engineering_internship)
   ```
2. **Rate-Limiting Delay**: Implements a minimum delay of **1.0 second** (greater than the required 500ms) between consecutive live network requests to ensure zero server strain.
3. **Strict Timeouts**: All requests specify a 10.0-second timeout to prevent hanging.
4. **Local Disk Caching**: Raw HTML is saved locally in `cache/`. Subsequent runs read from local storage with zero redundant network requests (`[CACHE HIT]`).
5. **Fault Tolerance**: Pages are processed individually in isolated try-except blocks. HTTP 404/403 errors are logged and skipped without killing the run; transient errors (timeouts / 5xx) are retried once.

---

## 📐 Record Schema (Pydantic)

Validated via `src/models.py:BookRecord`:

```python
class BookRecord(BaseModel):
    title: str                      # Book title string
    product_url: str                # Canonical product URL (must start with https://)
    price_text: str                 # Raw string price, e.g. "£51.77"
    price_gbp: float                # Normalized numeric GBP price, e.g. 51.77
    availability_text: str          # Stock availability string, e.g. "In stock (22 available)"
    rating_text: Optional[str]      # Star rating, e.g. "Three"
    description: Optional[str]      # Book description, or None (null) if missing
    source_page: str                # Provenance URL of catalogue page
    fetched_at: str                 # ISO 8601 UTC timestamp of fetch
```

---

## 📊 Proof of Execution (`output/run-report.json`)

Here is an actual `run-report.json` generated from a clean cached production run:

```json
{
  "start_time": "2026-09-14T14:55:04.917368+00:00",
  "duration_seconds": 0.93,
  "catalogue_pages": 3,
  "books_discovered": 60,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}
```

And here is the report generated when testing failure survival via `--stage5`:

```json
{
  "start_time": "2026-09-14T14:54:53.165690+00:00",
  "duration_seconds": 7.17,
  "catalogue_pages": 3,
  "books_discovered": 60,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}
```

### Why No Browser Was Needed
This pipeline deliberately avoided using a headless browser (Puppeteer, Playwright, or Selenium) because **the target website delivers static, server-side rendered HTML containing all catalog items and detail elements directly in the HTTP GET response body**. Running a headless browser would consume 10x-50x more memory and CPU cycles while introducing substantial startup overhead without adding any value.

---

## ⚠️ Honest Limitations

- **DOM Fragility**: The extractor depends on CSS class selectors (`.product_main`, `.price_color`, `.instock.availability`, `#product_description`). If the site's layout changes, selectors must be adjusted.
- **Currency Assumption**: Price normalization currently parses standard decimal formats and assumes GBP (`£`) currency values.
- **Pagination Assumption**: The crawler navigates using `<li class="next"><a ...>`. If pagination structure shifts to infinite scroll or dynamic AJAX, API reverse engineering would be required.

---

## 🤝 Ethics Note

1. **API First**: Always search for and prioritize an official public API before scraping any website.
2. **Respect Boundaries**: Never bypass authentication gates, paywalls, CAPTCHAs, or bot-protection mechanisms.
3. **Politeness**: Always declare your identity in the `User-Agent` with contact information, respect rate limits, and use caching during development.
4. **Data Minimization**: Collect only the minimum subset of data required for your purpose; never scrape private personal identifying information (PII).

---

## 🧪 Automated Unit Tests

Run the test suite with `pytest`:

```bash
pytest -v
```

Tests cover:
- `test_price_normalization`: Validates regex price parsing into floats.
- `test_relative_to_absolute_urls`: Validates `urljoin` resolution of relative paths.
- `test_missing_description`: Confirms `null` is saved when description is absent.
- `test_duplicate_urls_deduplication`: Confirms repeated URLs are filtered.
- `test_malformed_html_fixture`: Verifies extractor does not crash on invalid HTML.
- `test_book_record_schema_validation`: Checks Pydantic validation rejects invalid records.
