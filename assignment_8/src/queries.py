"""
SQL aggregation queries for the bookstore report.
Extracts summary metrics, top expensive titles, rating distributions, and catalog rows.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict
from src.config import DB_PATH


def get_report_data(db_path: Path = DB_PATH) -> Dict[str, Any]:
    """
    Executes aggregation queries turning rows into high-level business numbers:
    1. Total number of books (COUNT)
    2. Average catalog price (AVG)
    3. Top 5 most expensive books (ORDER BY price DESC LIMIT 5)
    4. Breakdown by star rating (COUNT, AVG grouped by rating)
    5. Full book catalog list for complete document appendix
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Total count
    cursor.execute("SELECT COUNT(*) as total_books FROM books")
    total_books = cursor.fetchone()["total_books"]

    # 2. Average price
    cursor.execute("SELECT AVG(price) as avg_price FROM books")
    row_avg = cursor.fetchone()["avg_price"]
    avg_price = round(float(row_avg or 0.0), 2)

    # 3. Top 5 most expensive titles
    cursor.execute(
        """
        SELECT id, title, price, rating, url 
        FROM books 
        ORDER BY price DESC 
        LIMIT 5
        """
    )
    top_5_expensive = [dict(r) for r in cursor.fetchall()]

    # 4. Rating distribution breakdown
    cursor.execute(
        """
        SELECT 
            rating, 
            COUNT(*) as book_count, 
            ROUND(AVG(price), 2) as avg_price,
            ROUND(MIN(price), 2) as min_price,
            ROUND(MAX(price), 2) as max_price
        FROM books 
        GROUP BY rating 
        ORDER BY rating DESC
        """
    )
    ratings_breakdown = [dict(r) for r in cursor.fetchall()]

    # 5. All catalog books
    cursor.execute("SELECT id, title, price, rating, url FROM books ORDER BY id ASC")
    all_books = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "summary": {
            "total_books": total_books,
            "avg_price": avg_price,
        },
        "top_5_expensive": top_5_expensive,
        "ratings_breakdown": ratings_breakdown,
        "all_books": all_books,
    }


if __name__ == "__main__":
    data = get_report_data()
    print("=== Aggregated Report Data ===")
    print(json.dumps({k: v for k, v in data.items() if k != "all_books"}, indent=2))
    print(f"Total catalog records retrieved: {len(data['all_books'])}")
