# The Polite Scraper (FlyRank Internship · Week 5 · Assignment A9 / BE-05)

A robust, polite scraping pipeline built with Python, Requests, BeautifulSoup, and Pydantic. It crawls the first three catalogue pages of **Books to Scrape**, visits all 60 book detail pages, turns raw HTML into validated, clean JSON records, survives page failures gracefully, and outputs a comprehensive execution run report.

---

## 🎯 Target Classification (Stage 0 Checkpoint)

- **Target Site**: [Books to Scrape](https://books.toscrape.com/)
- **Target Nature & Purpose**: Books to Scrape is an official, public scraping sandbox created specifically for developers to learn and practice web scraping techniques without causing harm or violating terms of service.
- **Scope**: Exactly the first **3 catalogue pages** (`catalogue/page-1.html` through `catalogue/page-3.html`), covering **60 unique book detail pages**.
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
