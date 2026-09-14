"""
Catalogue discovery crawler.
Finds catalogue pages and discovers book URLs up to the specified page limit.
"""

from typing import List, Tuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.client import PoliteClient
from src.config import START_URL


def discover_book_urls(
    client: PoliteClient,
    start_url: str = START_URL,
    max_pages: int = 3,
) -> Tuple[List[Tuple[str, str]], int]:
    """
    Crawls catalogue pages starting from start_url up to max_pages.
    Returns:
        (unique_book_entries, catalogue_pages_count)
        where each entry is (product_url, source_page_url).
    """
    current_page_url = start_url
    pages_crawled = 0
    discovered_entries: List[Tuple[str, str]] = []
    seen_urls = set()
    unique_entries: List[Tuple[str, str]] = []

    while current_page_url and pages_crawled < max_pages:
        html, status = client.get(current_page_url)
        if not html:
            print(f"[CRAWLER] Failed to retrieve catalogue page: {current_page_url}")
            break

        pages_crawled += 1
        soup = BeautifulSoup(html, "html.parser")

        # Find all book links on current catalogue page
        book_links = soup.select("article.product_pod h3 a")
        for link in book_links:
            href = link.get("href")
            if href:
                absolute_url = urljoin(current_page_url, href)
                discovered_entries.append((absolute_url, current_page_url))
                if absolute_url not in seen_urls:
                    seen_urls.add(absolute_url)
                    unique_entries.append((absolute_url, current_page_url))

        # Check for next page
        next_tag = soup.select_one("li.next a")
        if next_tag and next_tag.get("href"):
            current_page_url = urljoin(current_page_url, next_tag.get("href"))
        else:
            current_page_url = None

    return unique_entries, len(discovered_entries), pages_crawled
