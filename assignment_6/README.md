# Your First Background Job (FlyRank Internship · Week 7 · Assignment A7 / BE-06)

A high-performance, asynchronous background job processing architecture built with **FastAPI** and **Inngest**. It demonstrates the production standard for non-blocking web services: **accept fast, work in the background, and report status via polling**.

---

## 💡 The Core Architectural Pattern

In conventional synchronous web applications, slow tasks (such as AI generation, video rendering, or PDF report building) force the client to wait 10–40 seconds. Under traffic spikes or network instability, this causes HTTP gateway timeouts, browser freezes, and duplicate accidental retries.

This service solves that with a three-part lifecycle:
1. **The Fast Door (`POST /reports`)**: Validates the input, persists an initial pending record, dispatches a durable event to Inngest, and answers with **HTTP 202 Accepted** in **under 15 milliseconds**.
2. **The Worker (`make-report`)**: Inngest executes the heavy 8-second computation (`step.sleep` and `step.run`) asynchronously outside the client request-response lifecycle.
3. **Status Polling (`GET /reports/:id`)**: The client queries the status endpoint, seeing `pending` initially and `done` with the completed payload once finished (**eventual consistency**).

---

## ⚡ How to Run It (Under 5 Minutes)

### 1. Installation
Requires Python 3.10+ (tested with Python 3.12 and 3.14) and Node.js for the Inngest CLI.

```bash
cd assignment_6

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
# Or via pip:
# pip install fastapi uvicorn pydantic inngest httpx pytest
```

### 2. Start the Services (Two Terminals)

**Terminal 1 — Start the FastAPI Service**:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Start the Inngest Local Dev Server**:
```bash
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```
Open the interactive visual Inngest dashboard at **[http://localhost:8288](http://localhost:8288)** to monitor runs, view step timelines, inspect payloads, and test retries.

---

## 📋 API Endpoints & Inngest Functions

### REST API Endpoints
| Method | Path | Status | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | `200 OK` | Liveness health check. |
| `POST` | `/reports` | `202 Accepted` | Fast door: validates topic, creates pending record, emits event, returns in <15ms. |
| `GET` | `/reports/{id}` | `200 / 404` | Polling endpoint: returns `pending`, `done` with result, or `failed`. |
| `GET` | `/reports` | `200 OK` | Control panel extra: lists all active and completed reports. |
| `GET/PUT` | `/api/inngest` | `200 OK` | Inngest function registration and execution endpoint. |

### Inngest Background & Scheduled Functions
| Function ID | Trigger | Retries | Description |
| :--- | :--- | :---: | :--- |
| `say-hello` | `test/hello` | 0 | Introductory background function sleeping 5s and returning greeting. |
| `make-report` | `report/requested` | 2 (3 attempts) | Durable multi-step report generator (`step.sleep("8s")` + `step.run("build")`). Simulates retry failure when `topic == "fail"`. |
| `heartbeat` | `* * * * *` (Cron) | 0 | Autonomous scheduled job executing every minute, logging pending/done/failed report counts. |

---

## 🔬 Proof of Execution: 202 Accepted + Polling

### 1. Fast Door Request
```bash
$ time curl -i -X POST http://localhost:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"topic": "market-trends"}'
```
**Output (HTTP 202 in 0.010s)**:
```http
HTTP/1.1 202 Accepted
content-type: application/json

{"id": "204a98cf", "status": "pending"}

real    0m0.012s
```

### 2. Immediate Status Poll (Pending)
```bash
$ curl -s http://localhost:8000/reports/204a98cf
```
**Output**:
```json
{
  "id": "204a98cf",
  "topic": "market-trends",
  "status": "pending",
  "result": null
}
```

### 3. Status Poll after ~10 Seconds (Completed)
```bash
$ curl -s http://localhost:8000/reports/204a98cf
```
**Output**:
```json
{
  "id": "204a98cf",
  "topic": "market-trends",
  "status": "done",
  "result": "Comprehensive executive intelligence report compiled for topic: 'market-trends'."
}
```

---

## 🛡️ Stage 3 Reflection: Retries vs. Bad Input Validation

> **"A wrong input (such as a missing topic) must be rejected immediately at the door with HTTP 400 without creating a job; whereas a transient failure (like a database glitch or network timeout) represents the wrong moment rather than the wrong request, and thus rightfully deserves an automated retry with backoff."**

- **Bad Input Handling**: Sending `POST /reports` with `{}` or `{"topic": ""}` returns `400 Bad Request` in <1ms without emitting an event.
- **Transient Failure Handling**: Sending `POST /reports` with `{"topic": "fail"}` triggers the `make-report` worker, which fails during `step.run`, waits with exponential backoff across 3 attempts, and safely marks the report `failed` in the Inngest dashboard.

---

## ⏰ Stage 4 Reflection: Cron Schedules

The `heartbeat` function runs on schedule `* * * * *` (every minute) without any client request.

- **Every day at 08:00 UTC**:
  ```cron
  0 8 * * *
  ```
- **Every Sunday at 22:00 UTC**:
  ```cron
  0 22 * * 0
  ```
*(Verified using crontab.guru)*

---

## 🧪 Automated Unit Tests

Run the test suite with `pytest`:
```bash
pytest -v
```
Verifies healthcheck, fast 202 door timing (<100ms), 400 input validation, eventual consistency polling lifecycle, 404 handling, report listing, Inngest registration, and heartbeat count aggregation.
