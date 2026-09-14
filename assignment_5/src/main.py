"""
FlyRank Internship · Backend Track · Week 5 · Assignment A9
The Polite Scraper - Main CLI Interface
"""

import argparse
import json
import sys

from src.client import PoliteClient
from src.config import START_URL
from src.crawler import discover_book_urls
from src.extractor import extract_raw_record
from src.pipeline import ScraperPipeline


def run_stage_1():
    print("=== Stage 1 Checkpoint: Fetch & Cache Catalogue Page 1 ===")
    client = PoliteClient()
    html, status = client.get(START_URL)
    if html:
        print(f"Successfully retrieved page 1! Status: {status}")
    else:
        print(f"Failed to retrieve page 1: {status}")


def run_stage_2():
    print("=== Stage 2 Checkpoint: Discover Three Catalogue Pages ===")
    client = PoliteClient()
    unique_books, discovered_count, catalogue_pages = discover_book_urls(
        client, start_url=START_URL, max_pages=3
    )
    print(
        f"catalogue_pages={catalogue_pages}, discovered={discovered_count}, unique_urls={len(unique_books)}"
    )


def run_stage_3():
    print("=== Stage 3 Checkpoint: Extract Raw Book Details ===")
    client = PoliteClient()
    unique_books, _, _ = discover_book_urls(client, start_url=START_URL, max_pages=3)

    raw_records = []
    for idx, (url, source_page) in enumerate(unique_books, start=1):
        html, _ = client.get(url)
        if html:
            record = extract_raw_record(
                html=html,
                product_url=url,
                source_page=source_page,
                fetched_at="2026-09-14T12:00:00Z",
            )
            raw_records.append(record)

    if raw_records:
        print("\nSample Raw Record (All 8 keys):")
        print(json.dumps(raw_records[0], indent=2))
    print(f"\ndetail_pages={len(raw_records)}")


def run_stage_4():
    print("=== Stage 4 Checkpoint: Clean, Validate & Store Records ===")
    pipeline = ScraperPipeline()
    result = pipeline.run(max_catalogue_pages=3, inject_failure=False)
    records = result["valid_records"]
    print(f"\nCheckpoint check: Total valid records in books.json = {len(records)}")
    all_numeric = all(isinstance(r.price_gbp, (int, float)) for r in records)
    all_https = all(r.product_url.startswith("https://") for r in records)
    print(f"All price_gbp are numbers: {all_numeric}")
    print(f"All product_url start with https://: {all_https}")


def run_stage_5():
    print("=== Stage 5 Checkpoint: Survive Failures & Report Run ===")
    pipeline = ScraperPipeline()
    result = pipeline.run(max_catalogue_pages=3, inject_failure=True)
    report = result["report"]
    print(f"\nCheckpoint check with injected broken URL:")
    print(f"Good records surviving: {len(result['valid_records'])}")
    print(f"failed_pages: {report['failed_pages']}")
    print(f"Run Report Output:\n{json.dumps(report, indent=2)}")


def main():
    parser = argparse.ArgumentParser(description="FlyRank Polite Scraper")
    parser.add_argument("--stage1", action="store_true", help="Run Stage 1 checkpoint")
    parser.add_argument("--stage2", action="store_true", help="Run Stage 2 checkpoint")
    parser.add_argument("--stage3", action="store_true", help="Run Stage 3 checkpoint")
    parser.add_argument("--stage4", action="store_true", help="Run Stage 4 checkpoint")
    parser.add_argument("--stage5", action="store_true", help="Run Stage 5 checkpoint (injected failure)")
    parser.add_argument("--test-failure", action="store_true", help="Inject deliberate 404 test page")
    parser.add_argument("--pages", type=int, default=3, help="Max catalogue pages to scrape")

    args = parser.parse_args()

    if args.stage1:
        run_stage_1()
    elif args.stage2:
        run_stage_2()
    elif args.stage3:
        run_stage_3()
    elif args.stage4:
        run_stage_4()
    elif args.stage5:
        run_stage_5()
    else:
        # Full production run
        pipeline = ScraperPipeline()
        pipeline.run(max_catalogue_pages=args.pages, inject_failure=args.test_failure)


if __name__ == "__main__":
    main()
