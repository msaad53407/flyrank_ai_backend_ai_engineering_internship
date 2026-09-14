"""
FlyRank Internship · Backend Track · Week 5 · Assignment A9
The Polite Scraper
"""

import sys
from src.client import PoliteClient
from src.config import START_URL
from src.crawler import discover_book_urls


def run_stage_1():
    print("--- Stage 1: Fetch and cache first catalogue page ---")
    client = PoliteClient()
    html, status = client.get(START_URL)
    if html:
        print(f"Successfully retrieved page 1! Status: {status}")
    else:
        print(f"Failed to retrieve page 1: {status}")


def run_stage_2():
    print("--- Stage 2: Discover three catalogue pages ---")
    client = PoliteClient()
    unique_books, discovered_count, catalogue_pages = discover_book_urls(
        client, start_url=START_URL, max_pages=3
    )
    print(
        f"catalogue_pages={catalogue_pages}, discovered={discovered_count}, unique_urls={len(unique_books)}"
    )


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--stage1":
            run_stage_1()
            return
        elif arg == "--stage2":
            run_stage_2()
            return

    # Default runs up to stage 2
    run_stage_2()


if __name__ == "__main__":
    main()
