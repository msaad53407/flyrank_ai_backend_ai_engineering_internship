from typing import Optional
from fastapi import FastAPI, Response
from starlette import status
from contextlib import asynccontextmanager

from database import (
    init_db,
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
    get_task_stats,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_db()
    yield


app = FastAPI(
    title="Task API with SQLite",
    description="Week 3 Assignment 1: Connecting CRUD API to SQLite Database",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"name": "Task API (SQLite)", "version": "1.0", "endpoints": ["/tasks", "/stats"]}


@app.get("/health")
async def health():
    return {"status": "ok", "database": "sqlite"}


@app.get("/tasks")
async def get_tasks(
    search: Optional[str] = None,
    done: Optional[bool] = None,
    sort: Optional[str] = None,
):
    tasks = get_all_tasks(search=search, done=done, sort=sort)
    return {"tasks": tasks}


@app.get("/tasks/{id}")
async def get_task(id: int, response: Response):
    task = get_task_by_id(id)
    if task:
        return {"task": task}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": f"Task {id} not found"}


@app.post("/tasks")
async def create_new_task(task: dict, response: Response):
    if "title" not in task or not isinstance(task["title"], str) or len(task["title"].strip()) < 3:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "error": "Task must have a title and it must be at least 3 characters long"
        }

    is_done = bool(task.get("done", False))
    created = create_task(title=task["title"].strip(), done=is_done)

    response.status_code = status.HTTP_201_CREATED
    return {"task_id": created["id"], "task": created}


@app.put("/tasks/{id}")
async def update_existing_task(id: int, task: dict, response: Response):
    if "title" in task:
        if not isinstance(task["title"], str) or len(task["title"].strip()) < 3:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "error": "Task must have a title and it must be at least 3 characters long"
            }

    updated = update_task(
        task_id=id,
        title=task["title"].strip() if "title" in task else None,
        done=task.get("done"),
    )

    if updated:
        return {"task": updated}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": f"Task {id} not found"}


@app.delete("/tasks/{id}")
async def delete_existing_task(id: int, response: Response):
    success = delete_task(id)
    if success:
        response.status_code = status.HTTP_204_NO_CONTENT
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": f"Task {id} not found"}


@app.get("/stats")
async def get_stats():
    return get_task_stats()
