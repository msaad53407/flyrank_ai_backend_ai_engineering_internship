# Week 2 · Assignment — Frame It as Cases: Work That Speaks for Itself

This assignment establishes an authentic Voice Card and frames technical projects into 3-beat case studies (Problem -> What You Did -> Outcomes).

---

## 🎙️ The Voice Card

**Standing Voice Instructions:**
> *"Direct, plain, technical, no corporate buzzwords, outcome-focused, transparent."*

---

## 📚 Framed Case Studies (3-Beat Structure)

### Case 1: Week 3 A2 — SQLite-Backed CRUD API
- **Beat 1: The Problem**
  In-memory task APIs lose all state whenever the web server restarts or crashes. Clients require reliable data persistence without complex database cluster administration.
- **Beat 2: What You Did**
  Replaced in-memory dictionaries with an embedded SQLite database using `sqlite3`. Built idempotent table creation and seeding on startup while preserving 100% of existing API routes and status codes.
- **Beat 3: What Came of It (Outcome)**
  Full data persistence verified across server restarts, zero route contract changes, and 6 passing unit tests.

### Case 2: Week 3 A3 — PostgreSQL + Docker Compose Microservice Stack
- **Beat 1: The Problem**
  Local development environments often fail to mirror production database engines, leading to "works on my machine" bugs.
- **Beat 2: What You Did**
  Decoupled FastAPI route handlers from database logic using the **Repository Pattern** (`TaskRepository` interface). Built a containerized stack with `Dockerfile` and `docker-compose.yml` pairing Python 3.13 with PostgreSQL 16 Alpine and a named volume (`postgres_data`).
- **Beat 3: What Came of It (Outcome)**
  One-command stack launch (`docker compose up --build`), verified data persistence across container restarts, and clean architectural separation.

---

## ✂️ Before / After Copy Comparison

### 🔴 Generic AI Draft (Before)
> *"I am a results-driven, highly innovative AI software engineer passionate about leveraging state-of-the-art cutting-edge paradigms to deliver transformative backend solutions."*

### 🟢 Edited & Refined Voice (After)
> *"I build containerized FastAPI microservices in Python backed by PostgreSQL. I focus on clean repository pattern architecture, automated unit tests, and verifiable data persistence."*
