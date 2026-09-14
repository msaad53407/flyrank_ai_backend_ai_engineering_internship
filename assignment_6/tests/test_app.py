"""
Automated unit tests for Assignment 6 / BE-06 Background Job Service.
"""

import time
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.storage import create_report, get_counts, update_report


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """Health check must respond with 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_report_fast_door(client):
    """POST /reports must return 202 Accepted in milliseconds with pending status."""
    start = time.perf_counter()
    response = client.post("/reports", json={"topic": "artificial-intelligence"})
    elapsed = time.perf_counter() - start

    assert response.status_code == 202
    assert elapsed < 0.2  # Fast door well under 200ms
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"


def test_create_report_missing_topic_rejected(client):
    """Missing or empty topic must return 400 Bad Request before any job is created."""
    res_empty = client.post("/reports", json={})
    assert res_empty.status_code == 400
    assert "Missing required field 'topic'" in res_empty.json()["detail"]

    res_blank = client.post("/reports", json={"topic": "   "})
    assert res_blank.status_code == 400


def test_get_report_status_lifecycle(client):
    """GET /reports/{id} must reflect eventual consistency from pending to done."""
    # Create report
    post_res = client.post("/reports", json={"topic": "quantum-computing"})
    rep_id = post_res.json()["id"]

    # Initial poll
    poll_1 = client.get(f"/reports/{rep_id}")
    assert poll_1.status_code == 200
    assert poll_1.json()["status"] == "pending"
    assert poll_1.json()["result"] is None

    # Simulate background worker completion
    update_report(rep_id, status="done", result="Detailed quantum computing report")

    # Second poll
    poll_2 = client.get(f"/reports/{rep_id}")
    assert poll_2.status_code == 200
    assert poll_2.json()["status"] == "done"
    assert poll_2.json()["result"] == "Detailed quantum computing report"


def test_get_report_not_found(client):
    """Non-existent report ID must return 404 Not Found."""
    response = client.get("/reports/unknown_non_existent_id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_reports_control_panel(client):
    """GET /reports must list all reports."""
    response = client.get("/reports")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_inngest_registration_endpoint(client):
    """GET /api/inngest must serve Inngest introspection schema."""
    response = client.get("/api/inngest")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "dev"
    assert data["function_count"] >= 3


def test_storage_heartbeat_counts():
    """Verify heartbeat count aggregation."""
    rec = create_report("test-topic")
    counts = get_counts()
    assert counts["total"] >= 1
    assert counts["pending"] >= 1
