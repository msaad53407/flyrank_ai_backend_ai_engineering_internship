# Week 3 · Assignment 1 (A2) — Connecting CRUD to SQLite Database

This project upgrades the Week 1 / Week 2 in-memory CRUD API to use a real **SQLite database**. All data now persists across server restarts while maintaining the exact same API contracts for clients.

---

## 💡 Architectural Shift

- **Before:** `Client -> FastAPI -> In-Memory Array (Lost on restart)`
- **After:** `Client -> FastAPI -> SQLite Database (Persisted in tasks.db)`

---

## 🗄️ Database Choice & Storage

- **Why SQLite?** SQLite is a zero-configuration, serverless, self-contained SQL database engine stored in a single file (`tasks.db`). It provides ACID transactions and SQL querying power without requiring external database server installation or management.
- **Database File:** Stored at `assignment_2/tasks.db` (automatically created on first application run).

---

## 🛠️ Data Model & Schema

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0
);
```

On initial startup, if the database table is empty, 3 example tasks are seeded automatically.

---

## 🚀 How to Run the Project

### Prerequisites
- Python >= 3.13
- [`uv`](https://docs.astral.sh/uv/) (recommended) or standard `pip`

### Step 1: Install Dependencies
```bash
uv sync
```

### Step 2: Start the FastAPI Server
```bash
uv run uvicorn main:app --reload --port 8000
```
Access interactive API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Step 3: Run Unit Tests
```bash
uv run pytest
```

---

## 🔍 SQL Exploration & Manual Queries

You can inspect and manipulate `tasks.db` using any SQLite viewer (e.g., **DB Browser for SQLite** or the `sqlite3` CLI).

```
+----+----------------------------------+------+
| id | title                            | done |
+----+----------------------------------+------+
| 1  | Complete Assignment              | 1    |
| 2  | Go to the gym                    | 1    |
| 3  | Write about today in journal     | 0    |
+----+----------------------------------+------+
```

### Key Queries Executed
1. **List all tasks:**
   ```sql
   SELECT * FROM tasks;
   ```
2. **Show completed tasks:**
   ```sql
   SELECT * FROM tasks WHERE done = 1;
   ```
3. **Count total tasks:**
   ```sql
   SELECT COUNT(*) FROM tasks;
   ```
4. **Mark all tasks completed:**
   ```sql
   UPDATE tasks SET done = 1;
   ```
5. **Delete completed tasks:**
   ```sql
   DELETE FROM tasks WHERE done = 1;
   ```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tasks` | List all tasks (supports `?search=...`, `?done=true`, `?sort=asc/desc`) |
| `GET` | `/tasks/{id}` | Get specific task by ID (404 if missing) |
| `POST` | `/tasks` | Create a new task (body: `{"title": "...", "done": false}`) |
| `PUT` | `/tasks/{id}` | Update task title/status |
| `DELETE` | `/tasks/{id}` | Delete task |
| `GET` | `/stats` | Return task counts using SQL `COUNT()` |
| `GET` | `/health` | Server & DB health check |
