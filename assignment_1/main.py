from fastapi import FastAPI
from fastapi.responses import Response
from starlette import status

app = FastAPI()

tasks = [
    {"id": 1, "title": "Complete Assingment", "done": True},
    {"id": 2, "title": "Go to the gym", "done": True},
    {"id": 3, "title": "Write about today in journal", "done": False},
]


@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/tasks")
async def get_tasks():
    return {"tasks": tasks}


@app.get("/tasks/{id}")
async def get_task(id: int, response: Response):
    task = tasks[id - 1] if 0 < id <= len(tasks) else None
    if task:
        return {"task": task}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": f"Task {id} not found"}


@app.post("/tasks")
async def create_task(task: dict, response: Response):
    if "title" not in task or len(task["title"]) < 3:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "error": "Task must have a title and it must be at least 3 characters long"
        }

    last_id = tasks[-1]["id"] if tasks else 0
    task["id"] = last_id + 1
    task["done"] = False
    tasks.append(task)

    response.status_code = status.HTTP_201_CREATED
    return {"task_id": task["id"]}


@app.put("/tasks/{id}")
async def update_task(id: int, task: dict, response: Response):
    if "title" in task and len(task["title"]) < 3:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "error": "Task must have a title and it must be at least 3 characters long"
        }

    task_id = id - 1
    if 0 <= task_id < len(tasks):
        tasks[task_id]["title"] = (
            task["title"] if "title" in task else tasks[task_id]["title"]
        )
        tasks[task_id]["done"] = task.get("done", tasks[task_id]["done"])
        return {"task": tasks[task_id]}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": f"Task {id} not found"}


@app.delete("/tasks/{id}")
async def delete_task(id: int, response: Response):
    task_id = id - 1
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        response.status_code = status.HTTP_204_NO_CONTENT
        return {}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": f"Task {id} not found"}
