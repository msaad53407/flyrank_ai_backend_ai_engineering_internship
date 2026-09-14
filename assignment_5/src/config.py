"""
Configuration and settings for the polite scraper.
"""

from pathlib import Path

# Target URLs
BASE_URL = "https://books.toscrape.com/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"

# Politeness Settings
USER_AGENT = (
    "FlyRankInternshipA9/1.0 "
    "(+https://github.com/msaad53407/flyrank_ai_backend_ai_engineering_internship)"
)
REQUEST_TIMEOUT = 10.0  # seconds
REQUEST_DELAY = 1.0     # seconds between live network requests (minimum 0.5s required)

# Storage Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"
OUTPUT_DIR = PROJECT_ROOT / "output"
