# Week 2 · Assignment — The Prompt Ladder

This assignment demonstrates progressive prompt engineering by taking a weak baseline prompt and iterating it across 5 distinct versions. Exactly **one layer** is added per version, with output changes evaluated at every step.

---

## 🪜 The Prompt Ladder

### 🔴 Baseline (Weak Prompt)
- **Prompt:** `"Write a backend API for tasks."`
- **Output Excerpt:**
  ```python
  # Simple script returning hardcoded task list
  def get_tasks():
      return ["task1", "task2"]
  ```
- **Evaluation:** Extremely generic, no framework specified, no type hints, no error handling, no persistence.

---

### 🟡 Version 1: Adding Layer 1 — Role & Persona
- **Prompt:** `"You are a Senior Python Architect. Write a backend API for tasks."`
- **Output Excerpt:**
  ```python
  from fastapi import FastAPI
  app = FastAPI()
  tasks = []

  @app.get("/tasks")
  def read_tasks():
      return tasks
  ```
- **4-Point Notes:**
  1. *What Changed:* Assigned Senior Python Architect role.
  2. *What Improved:* Switched to FastAPI framework with `@app.get` decorators.
  3. *What Still Failed:* In-memory storage, no Pydantic models, no validation or HTTP status codes.
  4. *What to Try Next:* Add explicit target audience and usage context.

---

### 🟡 Version 2: Adding Layer 2 — Real Context & Purpose
- **Prompt:** `"You are a Senior Python Architect. Write a FastAPI backend API for a task management application where clients need to create, read, update, and delete tasks with persistence."`
- **Output Excerpt:**
  ```python
  # Added SQLite connection & CRUD functions
  import sqlite3
  conn = sqlite3.connect("tasks.db")
  ```
- **4-Point Notes:**
  1. *What Changed:* Specified FastAPI framework, task management domain, and CRUD persistence context.
  2. *What Improved:* Replaced hardcoded array with SQLite database queries.
  3. *What Still Failed:* Untyped request bodies, missing standard status codes (400, 404, 201).
  4. *What to Try Next:* Specify strict JSON output schema and status code requirements.

---

### 🟡 Version 3: Adding Layer 3 — Specified Output Schema & Status Codes
- **Prompt:** `"You are a Senior Python Architect. Write a FastAPI CRUD API with SQLite. Endpoints must return JSON objects in format {'tasks': [...]} or {'task': {...}} and use HTTP 201 for POST, 204 for DELETE, and 404 for missing items."`
- **Output Excerpt:**
  ```python
  @app.post("/tasks", status_code=201)
  def create(task: dict):
      ...
  ```
- **4-Point Notes:**
  1. *What Changed:* Enforced explicit JSON response keys and standard HTTP status codes.
  2. *What Improved:* Endpoints now return standard HTTP 201, 204, and 404 response objects.
  3. *What Still Failed:* Input payloads accept any dictionary (`task: dict`) without title validation.
  4. *What to Try Next:* Add strict input validation constraints (title min_length=3).

---

### 🟡 Version 4: Adding Layer 4 — Input Validation Constraints
- **Prompt:** `"You are a Senior Python Architect. Write a FastAPI CRUD API with SQLite. Validate that task titles are strings with at least 3 characters. Return 400 Bad Request if title is invalid."`
- **Output Excerpt:**
  ```python
  if "title" not in task or len(str(task["title"]).strip()) < 3:
      raise HTTPException(status_code=400, detail="Title must be >= 3 chars")
  ```
- **4-Point Notes:**
  1. *What Changed:* Added strict payload title length validation rules.
  2. *What Improved:* Bad requests with short or missing titles are rejected with HTTP 400.
  3. *What Still Failed:* Direct database calls inside route handlers (tight coupling).
  4. *What to Try Next:* Add Few-Shot Repository Pattern architectural example.

---

### 🟢 Version 5: Adding Layer 5 — Few-Shot Example & Repository Pattern (Final Prompt)
- **Prompt:**
  ```markdown
  You are a Senior Python Architect. Build a production FastAPI Task CRUD API using the Repository Pattern.

  Requirements:
  1. Storage: Abstract TaskRepository interface implemented by SQLiteTaskRepository.
  2. Endpoints: GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id}, GET /stats.
  3. Validation: Task title must be non-empty string >= 3 chars (return 400). Missing IDs return 404.
  4. Example Repository Structure:
     class TaskRepository(ABC):
         @abstractmethod
         def get_all(self): pass
  ```
- **Output Excerpt:**
  ```python
  # Clean, modular, fully typed FastAPI app with abstract TaskRepository and SQLite engine
  ```
- **4-Point Notes:**
  1. *What Changed:* Provided architectural template showing abstract Repository Pattern interface.
  2. *What Improved:* Perfect separation of concerns between API routes and database storage.
  3. *What Still Failed:* None — meets production backend standards.
  4. *What to Try Next:* Final prompt is complete and reusable by any developer.

---

## 🎯 Final Reusable Prompt Template

```markdown
You are a Senior Backend Python Architect. Create a modular FastAPI CRUD application.

Domain: Task Management System
Architecture: Repository Pattern (abstract TaskRepository interface with SQLite implementation)
Endpoints required:
- GET /tasks (supports optional search and done filter)
- GET /tasks/{id} (404 if missing)
- POST /tasks (validates title len >= 3, returns 201)
- PUT /tasks/{id} (updates task, returns 404/400)
- DELETE /tasks/{id} (deletes task, returns 204/404)
- GET /stats (SQL COUNT stats)

Include complete Pydantic models, type annotations, and automatic table initialization.
```
