import os
import pytest
from fastapi.testclient import TestClient
import sqlite3

from src.main import app
from src.config import DB_PATH, REPORTS_DIR
from src.seed import seed_database
from src.queries import get_report_data

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Ensure database is seeded before running tests."""
    seed_database()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_seed_and_queries():
    # Verify 60 books seeded
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 60

    # Verify query aggregations
    data = get_report_data(DB_PATH)
    assert data["summary"]["total_books"] == 60
    assert data["summary"]["avg_price"] > 0
    assert len(data["top_5_expensive"]) == 5
    assert len(data["ratings_breakdown"]) > 0
    assert len(data["all_books"]) == 60


def test_generate_and_serve_report():
    # Generate new report with force=True to ensure fresh execution
    response = client.post("/reports", json={"force": True})
    assert response.status_code == 201
    res_data = response.json()
    assert "id" in res_data
    report_id = res_data["id"]
    assert res_data["file"] == f"/reports/{report_id}/file"

    # Get metadata
    meta_res = client.get(f"/reports/{report_id}")
    assert meta_res.status_code == 200
    meta_data = meta_res.json()
    assert meta_data["id"] == report_id
    assert meta_data["file"] == f"/reports/{report_id}/file"

    # 404 on unknown ID
    unknown_res = client.get("/reports/unknown-999")
    assert unknown_res.status_code == 404

    # Download file by link
    file_res = client.get(f"/reports/{report_id}/file")
    assert file_res.status_code == 200
    assert file_res.headers["content-type"] == "application/pdf"
    assert file_res.content.startswith(b"%PDF")
    assert len(file_res.content) > 10000  # Multi-page PDF


def test_idempotency():
    # Calling POST without force should return the existing report (HTTP 200)
    res1 = client.post("/reports", json={"force": False})
    assert res1.status_code == 200
    id1 = res1.json()["id"]

    res2 = client.post("/reports", json={"force": False})
    assert res2.status_code == 200
    id2 = res2.json()["id"]

    assert id1 == id2

    # Calling with force=True generates a new report (HTTP 201)
    res_force = client.post("/reports", json={"force": True})
    assert res_force.status_code == 201
    assert res_force.json()["id"] != id1


def test_list_reports():
    response = client.get("/reports")
    assert response.status_code == 200
    reports = response.json()
    assert isinstance(reports, list)
    assert len(reports) >= 1
    assert "id" in reports[0]
    assert "file" in reports[0]
