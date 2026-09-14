"""
Polite HTTP client with file-based caching and rate limiting.
"""

import hashlib
import re
import time
from pathlib import Path
from typing import Optional, Tuple
import requests

from src.config import CACHE_DIR, REQUEST_DELAY, REQUEST_TIMEOUT, USER_AGENT


class PoliteClient:
    """Polite HTTP client with local caching and request rate limiting."""

    def __init__(
        self,
        cache_dir: Path = CACHE_DIR,
        user_agent: str = USER_AGENT,
        timeout: float = REQUEST_TIMEOUT,
        delay: float = REQUEST_DELAY,
    ):
        self.cache_dir = cache_dir
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay = delay
        self.last_request_time: float = 0.0

        # Run statistics
        self.fetch_count = 0
        self.cache_hit_count = 0
        self.failed_pages_count = 0

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, url: str) -> Path:
        """Derive a deterministic, readable filename for caching."""
        # Clean specific well-known paths
        match = re.search(r"catalogue/page-(\d+)\.html", url)
        if match:
            return self.cache_dir / f"catalogue-page-{match.group(1)}.html"

        # Book detail pages: extract slug
        match_book = re.search(r"catalogue/([^/]+)/index\.html", url)
        if match_book:
            slug = match_book.group(1)
            # sanitize slug
            safe_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", slug)
            return self.cache_dir / f"book-{safe_slug}.html"

        # Fallback hash
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        return self.cache_dir / f"page-{url_hash}.html"

    def get(self, url: str, retry_on_failure: bool = True) -> Tuple[Optional[str], str]:
        """
        Fetch a URL with caching and politeness rules.
        Returns tuple of (html_content, status_message).
        """
        cache_file = self._get_cache_path(url)

        # 1. Cache Check
        if cache_file.exists():
            content = cache_file.read_text(encoding="utf-8")
            self.cache_hit_count += 1
            size = len(content.encode("utf-8"))
            msg = f"[CACHE HIT] {url} ({size:,} bytes)"
            print(msg)
            return content, "CACHE_HIT"

        # 2. Rate Limiting: wait if needed before live network request
        elapsed = time.time() - self.last_request_time
        if self.last_request_time > 0 and elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml",
        }

        attempts = 2 if retry_on_failure else 1
        last_error = None

        for attempt in range(1, attempts + 1):
            try:
                self.last_request_time = time.time()
                response = requests.get(url, headers=headers, timeout=self.timeout)

                if response.status_code == 200:
                    html = response.text
                    cache_file.write_text(html, encoding="utf-8")
                    self.fetch_count += 1
                    size = len(response.content)
                    msg = f"[FETCH] {url} (status: 200, size: {size:,} bytes)"
                    print(msg)
                    return html, "FETCH"
                else:
                    # Do not retry 404 / 403
                    if response.status_code in (403, 404) or attempt == attempts:
                        self.failed_pages_count += 1
                        msg = f"[FAILED] {url} (status: {response.status_code})"
                        print(msg)
                        return None, f"HTTP_{response.status_code}"

                    print(f"[RETRY] {url} (status: {response.status_code}, attempt {attempt})")
                    time.sleep(1.0)
            except (requests.Timeout, requests.ConnectionError) as e:
                last_error = e
                if attempt == attempts:
                    self.failed_pages_count += 1
                    msg = f"[ERROR] {url} failed: {e}"
                    print(msg)
                    return None, "NETWORK_ERROR"
                print(f"[RETRY] {url} encountered {type(e).__name__}, retrying once...")
                time.sleep(1.0)

        self.failed_pages_count += 1
        return None, "FAILED"
