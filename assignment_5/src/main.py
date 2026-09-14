"""
FlyRank Internship · Backend Track · Week 5 · Assignment A9
The Polite Scraper
"""

import sys
from src.client import PoliteClient
from src.config import START_URL


def run_stage_1():
    print("--- Stage 1: Fetch and cache first catalogue page ---")
    client = PoliteClient()
    html, status = client.get(START_URL)
    if html:
        print(f"Successfully retrieved page 1! Status: {status}")
    else:
        print(f"Failed to retrieve page 1: {status}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--stage1":
        run_stage_1()
    else:
        run_stage_1()


if __name__ == "__main__":
    main()
