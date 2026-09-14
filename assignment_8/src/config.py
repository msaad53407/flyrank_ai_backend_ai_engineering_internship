"""
Configuration for the PDF Report Generator service.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DB_PATH = PROJECT_ROOT / "report.db"
REPORTS_DIR = PROJECT_ROOT / "reports"
TEMPLATES_DIR = PROJECT_ROOT / "src" / "templates"
BOOKS_JSON_PATH = PROJECT_ROOT.parent / "assignment_5" / "output" / "books.json"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
