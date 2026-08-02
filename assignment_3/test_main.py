import pytest
from fastapi.testclient import TestClient
from main import app, get_repo
from repository import InMemoryTaskRepository


@pytest.fixture(autouse=True)
def setup_repo():
    test_repo = InMemoryTaskRepository()
    app.dependency_overrides[get_repo] = lambda: test_repo
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def test_root_and_health():
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["name"] == "Task API (PostgreSQL Stack)"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["repository"] == "InMemoryTaskRepository"


def test_get_initial_tasks():
    res = client.get("/tasks")
    assert res.status_code == 200
    tasks = res.json()["tasks"]
    assert len(tasks) == 3


def test_create_and_get_task():
    res_create = client.post("/tasks", json={"title": "Dockerize application", "done": False})
    assert res_create.status_code == 201
    task_id = res_create.json()["task_id"]

    res_get = client.get(f"/tasks/{task_id}")
    assert res_get.status_code == 200
    assert res_get.json()["task"]["title"] == "Dockerize application"


def test_update_and_delete():
    res_update = client.put("/tasks/1", json={"title": "Updated Complete Assignment", "done": True})
    assert res_update.status_code == 200

    res_delete = client.delete("/tasks/1")
    assert res_delete.status_code == 204

    res_missing = client.get("/tasks/1")
    assert res_missing.status_code == 404
