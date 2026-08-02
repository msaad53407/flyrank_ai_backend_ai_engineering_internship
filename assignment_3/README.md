# Week 3 · Assignment 2 (A3) — Containerize your stack with Docker & PostgreSQL

This project containerizes the FastAPI Task CRUD application and pairs it with a **PostgreSQL** database using **Docker Compose**. It demonstrates clean architecture using the **Repository Pattern**, keeping service routes unchanged while swapping storage engines.

---

## 🏛️ Architecture (Repository Pattern)

```
                     +-----------------------+
                     |  FastAPI Routes/API   |  (Unchanged)
                     +-----------+-----------+
                                 |
                     +-----------v-----------+
                     | TaskRepository (ABC)  |  (Interface Contract)
                     +-----------+-----------+
                                 |
             +-------------------+-------------------+
             |                                       |
 +-----------v-----------+               +-----------v-----------+
 | PostgresTaskRepo      |               | InMemoryTaskRepo      |
 | (PostgreSQL Database) |               | (Unit Test Fallback)  |
 +-----------------------+               +-----------------------+
```

Because of this abstraction:
- **Routes (`main.py`) remain 100% untouched.**
- Switching between in-memory testing and production PostgreSQL requires zero route code changes.

---

## 📦 Container Setup & Docker Compose

The application and database run as two connected services defined in `docker-compose.yml`:
1. **`db`**: PostgreSQL 16 Alpine container with a named volume `postgres_data` ensuring data persistence.
2. **`web`**: Python 3.13 FastAPI application container built from `Dockerfile`.

Connection configuration is loaded from `.env` (gitignored; see `.env.example`).

---

## 🚀 How to Run the Stack

### Option A: Complete Stack via Docker Compose (Recommended)

1. **Start the stack:**
   ```bash
   docker compose up --build
   ```
2. **Access the API:**
   - Base URL: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`
3. **Stop the stack:**
   ```bash
   docker compose down
   ```

### Option B: Local Testing via Pytest

```bash
uv run pytest
```

---

## 🛡️ Proof of Data Persistence

Data persistence was verified through the following steps:
1. Started the stack with `docker compose up -d`.
2. Created new tasks via `POST http://localhost:8000/tasks`.
3. Restarted both web & database containers (`docker compose restart` or `docker compose down` followed by `docker compose up`).
4. Executed `GET http://localhost:8000/tasks` and confirmed all previously created tasks were still intact in PostgreSQL.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tasks` | List all tasks (supports `?search=...`, `?done=true`, `?sort=asc/desc`) |
| `GET` | `/tasks/{id}` | Get task by ID (404 if missing) |
| `POST` | `/tasks` | Create task (`{"title": "...", "done": false}`) |
| `PUT` | `/tasks/{id}` | Update task |
| `DELETE` | `/tasks/{id}` | Delete task |
| `GET` | `/stats` | Task statistics from SQL `COUNT(*)` |
| `GET` | `/health` | Health check & active repository engine |
