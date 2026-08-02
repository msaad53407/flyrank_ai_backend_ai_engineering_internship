import os
import pytest
from fastapi.testclient import TestClient
import database
from main import app

TEST_DB = "test_tasks.db"


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", TEST_DB)
    database.reset_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except OSError:
            pass


def test_root_and_health():
    with TestClient(app) as client:
        res_root = client.get("/")
        assert res_root.status_code == 200
        assert res_root.json()["name"] == "Task API (SQLite)"

        res_health = client.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "ok"


def test_get_initial_tasks():
    with TestClient(app) as client:
        res = client.get("/tasks")
        assert res.status_code == 200
        tasks = res.json()["tasks"]
        assert len(tasks) == 3
        assert tasks[0]["title"] == "Complete Assignment"


def test_get_task_by_id():
    with TestClient(app) as client:
        res = client.get("/tasks/1")
        assert res.status_code == 200
        assert res.json()["task"]["id"] == 1

        res_404 = client.get("/tasks/999")
        assert res_404.status_code == 404
        assert "error" in res_404.json()


def test_create_task_validation_and_success():
    with TestClient(app) as client:
        res_bad = client.post("/tasks", json={"title": "hi"})
        assert res_bad.status_code == 400

        res_ok = client.post("/tasks", json={"title": "Buy groceries", "done": False})
        assert res_ok.status_code == 201
        new_id = res_ok.json()["task_id"]

        res_get = client.get(f"/tasks/{new_id}")
        assert res_get.status_code == 200
        assert res_get.json()["task"]["title"] == "Buy groceries"


def test_update_and_delete_task():
    with TestClient(app) as client:
        res_up = client.put("/tasks/1", json={"title": "Updated Assignment Title", "done": False})
        assert res_up.status_code == 200
        assert res_up.json()["task"]["done"] is False

        res_del = client.delete("/tasks/1")
        assert res_del.status_code == 204

        res_404 = client.get("/tasks/1")
        assert res_404.status_code == 404


def test_stats_and_filtering():
    with TestClient(app) as client:
        res_stats = client.get("/stats")
        assert res_stats.status_code == 200
        data = res_stats.json()
        assert data["total_tasks"] == 3
        assert data["completed_tasks"] == 2
        assert data["pending_tasks"] == 1

        res_search = client.get("/tasks?search=gym")
        assert len(res_search.json()["tasks"]) == 1
