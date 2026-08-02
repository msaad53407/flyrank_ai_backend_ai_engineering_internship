import os
import logging
from typing import Optional
from fastapi import FastAPI, Response, Depends
from starlette import status
from contextlib import asynccontextmanager

from repository import TaskRepository, PostgresTaskRepository, InMemoryTaskRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("assignment_3")

repo: TaskRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    global repo
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        logger.info("Initializing PostgreSQL Task Repository...")
        postgres_repo = PostgresTaskRepository(db_url=db_url)
        try:
            postgres_repo.init_db()
            repo = postgres_repo
            logger.info("Successfully connected to PostgreSQL database.")
        except Exception as e:
            logger.warning(f"Could not connect to Postgres ({e}). Falling back to InMemory repo.")
            repo = InMemoryTaskRepository()
    else:
        logger.info("No DATABASE_URL found. Using InMemory Task Repository.")
        repo = InMemoryTaskRepository()
    yield


app = FastAPI(
    title="Task API with PostgreSQL & Docker",
    description="Week 3 Assignment 2: Containerized CRUD API with PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)


def get_repo() -> TaskRepository:
    return repo


@app.get("/")
async def root():
    return {"name": "Task API (PostgreSQL Stack)", "version": "1.0", "endpoints": ["/tasks", "/stats"]}


@app.get("/health")
async def health(repository: TaskRepository = Depends(get_repo)):
    repo_type = type(repository).__name__
    return {"status": "ok", "repository": repo_type}


@app.get("/tasks")
async def get_tasks(
    search: Optional[str] = None,
    done: Optional[bool] = None,
    sort: Optional[str] = None,
    repository: TaskRepository = Depends(get_repo),
):
    tasks = repository.get_all(search=search, done=done, sort=sort)
    return {"tasks": tasks}


@app.get("/tasks/{id}")
async def get_task(id: int, response: Response, repository: TaskRepository = Depends(get_repo)):
    task = repository.get_by_id(id)
    if task:
        return {"task": task}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": f"Task {id} not found"}


@app.post("/tasks")
async def create_new_task(
    task: dict, response: Response, repository: TaskRepository = Depends(get_repo)
):
    if "title" not in task or not isinstance(task["title"], str) or len(task["title"].strip()) < 3:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "error": "Task must have a title and it must be at least 3 characters long"
        }

    is_done = bool(task.get("done", False))
    created = repository.create(title=task["title"].strip(), done=is_done)

    response.status_code = status.HTTP_201_CREATED
    return {"task_id": created["id"], "task": created}


@app.put("/tasks/{id}")
async def update_existing_task(
    id: int, task: dict, response: Response, repository: TaskRepository = Depends(get_repo)
):
    if "title" in task:
        if not isinstance(task["title"], str) or len(task["title"].strip()) < 3:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "error": "Task must have a title and it must be at least 3 characters long"
            }

    updated = repository.update(
        task_id=id,
        title=task["title"].strip() if "title" in task else None,
        done=task.get("done"),
    )

    if updated:
        return {"task": updated}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": f"Task {id} not found"}


@app.delete("/tasks/{id}")
async def delete_existing_task(
    id: int, response: Response, repository: TaskRepository = Depends(get_repo)
):
    success = repository.delete(id)
    if success:
        response.status_code = status.HTTP_204_NO_CONTENT
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": f"Task {id} not found"}


@app.get("/stats")
async def get_stats(repository: TaskRepository = Depends(get_repo)):
    return repository.get_stats()
