"""
Database seeding script for the PDF report generator.
Reads scraped book records from assignment_5/output/books.json and seeds report.db.
Supports Option B (Bookstore dataset) with idempotent deletion on rerun.
"""

import json
import sqlite3
from pathlib import Path
from src.config import BOOKS_JSON_PATH, DB_PATH

RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def init_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table for book dataset (Stage 1)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            rating INTEGER NOT NULL,
            url TEXT NOT NULL
        )
        """
    )

    # Table for report artifact bookkeeping (Stage 4)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def seed_database(db_path: Path = DB_PATH, json_path: Path = BOOKS_JSON_PATH) -> int:
    """
    Seed report.db idempotently.
    Deletes existing rows in 'books' first to ensure running twice leaves exactly 60 records.
    """
    conn = init_db(db_path)
    cursor = conn.cursor()

    # Clean existing rows to guarantee idempotency
    cursor.execute("DELETE FROM books")

    if not json_path.exists():
        raise FileNotFoundError(f"Source books dataset not found at {json_path}")

    books_data = json.loads(json_path.read_text(encoding="utf-8"))

    rows_to_insert = []
    for item in books_data:
        title = item.get("title", "")
        price = float(item.get("price_gbp", 0.0))
        rating_str = str(item.get("rating_text", "")).lower()
        rating = RATING_MAP.get(rating_str, 3)
        url = item.get("product_url", "")
        rows_to_insert.append((title, price, rating, url))

    cursor.executemany(
        "INSERT INTO books (title, price, rating, url) VALUES (?, ?, ?, ?)",
        rows_to_insert,
    )
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM books")
    total_count = cursor.fetchone()[0]
    conn.close()

    print(f"Seeded report.db with {total_count} books (idempotent clean copy).")
    return total_count


if __name__ == "__main__":
    seed_database()
