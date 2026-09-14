"""
Complete scraping pipeline orchestrating crawling, extraction, normalization,
validation, persistence, and run reporting.
"""

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from src.client import PoliteClient
from src.config import OUTPUT_DIR, START_URL
from src.crawler import discover_book_urls
from src.extractor import extract_raw_record
from src.models import BookRecord, RunReport, normalize_price


class ScraperPipeline:
    """End-to-end scraper pipeline with error resilience and run reporting."""

    def __init__(
        self,
        client: Optional[PoliteClient] = None,
        output_dir: Path = OUTPUT_DIR,
    ):
        self.client = client or PoliteClient()
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        max_catalogue_pages: int = 3,
        inject_failure: bool = False,
        export_csv: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes the scraping pipeline:
        1. Discover catalogue pages and book URLs.
        2. Optionally inject a deliberately failing URL for Stage 5 resilience verification.
        3. Fetch detail pages and extract raw fields.
        4. Normalize and validate records via Pydantic.
        5. Persist books.json, errors.json, run-report.json (and books.csv).
        """
        start_dt = datetime.now(timezone.utc)
        start_time_iso = start_dt.isoformat()
        start_perf = time.perf_counter()

        print(f"\n[PIPELINE START] {start_time_iso}")
        print(f"Target: Catalogue pages 1 to {max_catalogue_pages}")

        # 1. Discover Catalogue
        unique_entries, total_discovered, catalogue_pages = discover_book_urls(
            self.client, start_url=START_URL, max_pages=max_catalogue_pages
        )
        print(
            f"[DISCOVERY] catalogue_pages={catalogue_pages}, discovered={total_discovered}, unique_urls={len(unique_entries)}"
        )

        # 2. Inject failure if requested (Stage 5 checkpoint)
        book_list = list(unique_entries)
        if inject_failure:
            fake_url = "https://books.toscrape.com/catalogue/fake-broken-book-404_9999/index.html"
            print(f"[TEST INJECTION] Adding deliberate 404 test page: {fake_url}")
            book_list.append((fake_url, START_URL))

        # 3. Process each book detail page
        raw_records: List[Dict[str, Any]] = []
        valid_records: List[BookRecord] = []
        error_records: List[Dict[str, Any]] = []
        seen_canonical_urls = set()

        for idx, (book_url, source_page) in enumerate(book_list, start=1):
            fetch_time = datetime.now(timezone.utc).isoformat()
            html, status = self.client.get(book_url)

            if not html:
                # Log and skip broken page — 59+ good records must survive
                print(f"[PAGE SKIPPED] Failed book {idx}/{len(book_list)}: {book_url} ({status})")
                continue

            # Extract raw fields
            try:
                raw_data = extract_raw_record(
                    html=html,
                    product_url=book_url,
                    source_page=source_page,
                    fetched_at=fetch_time,
                )
                raw_records.append(raw_data)
            except Exception as e:
                print(f"[EXTRACTION ERROR] {book_url}: {e}")
                error_records.append({"url": book_url, "stage": "extraction", "error": str(e)})
                continue

            # 4. Normalize & Validate Schema
            price_gbp = normalize_price(raw_data.get("price_text"))
            if price_gbp is None:
                error_records.append({
                    "url": book_url,
                    "stage": "normalization",
                    "error": f"Invalid price string: {raw_data.get('price_text')}",
                    "raw_data": raw_data,
                })
                continue

            # Check idempotency / canonical URL deduplication
            if book_url in seen_canonical_urls:
                continue
            seen_canonical_urls.add(book_url)

            record_payload = dict(raw_data)
            record_payload["price_gbp"] = price_gbp

            try:
                validated_record = BookRecord(**record_payload)
                valid_records.append(validated_record)
            except ValidationError as ve:
                print(f"[VALIDATION FAILED] {book_url}: {ve}")
                error_records.append({
                    "url": book_url,
                    "stage": "validation",
                    "error": ve.errors(),
                    "raw_data": record_payload,
                })

        # 5. Persist Output
        books_file = self.output_dir / "books.json"
        books_data = [r.model_dump() for r in valid_records]
        books_file.write_text(json.dumps(books_data, indent=2, ensure_ascii=False), encoding="utf-8")

        errors_file = self.output_dir / "errors.json"
        errors_file.write_text(json.dumps(error_records, indent=2), encoding="utf-8")

        # Optional CSV Export
        if export_csv and valid_records:
            csv_file = self.output_dir / "books.csv"
            with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "title",
                        "price_gbp",
                        "price_text",
                        "availability_text",
                        "rating_text",
                        "product_url",
                        "source_page",
                        "fetched_at",
                        "description",
                    ],
                )
                writer.writeheader()
                for rec in valid_records:
                    writer.writerow(rec.model_dump())

        # Duration and Run Report
        duration_seconds = round(time.perf_counter() - start_perf, 2)
        report = RunReport(
            start_time=start_time_iso,
            duration_seconds=duration_seconds,
            catalogue_pages=catalogue_pages,
            books_discovered=len(unique_entries),
            pages_fetched=self.client.fetch_count,
            cache_hits=self.client.cache_hit_count,
            valid_records=len(valid_records),
            invalid_records=len(error_records),
            failed_pages=self.client.failed_pages_count,
        )

        report_file = self.output_dir / "run-report.json"
        report_file.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")

        print(f"\n[PIPELINE FINISHED] Duration: {duration_seconds}s")
        print(f"Valid records stored: {len(valid_records)} -> {books_file}")
        print(f"Invalid records: {len(error_records)} -> {errors_file}")
        print(f"Failed pages: {self.client.failed_pages_count}")
        print(f"Report written: {report_file}")

        return {
            "raw_records": raw_records,
            "valid_records": valid_records,
            "report": report.model_dump(),
        }
