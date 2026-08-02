# Week 4 · Assignment FL-04 — Ship an Automation Workflow v2

This assignment builds, executes, and audits a 4-step no-code/code automation pipeline for backend microservice development.

---

## 🏗️ 4-Step Pipeline Flow

```
[Raw Spec Input] 
       │
       ▼
Step 1: Gather & Ground (NotebookLM Context Parser)
       │
       ▼
Step 2: Synthesize & Schema Design (Pydantic v2 & DDL Generation)
       │
       ▼
Step 3: Code & Repository Generation (FastAPI & Storage Repositories)
       │
       ▼
Step 4: Audit & Pytest Suite Generation (Automated Unit Tests & Security Check)
       │
       ▼
[Production-Ready FastAPI Microservice]
```

*See [`pipeline_schema.json`](file:///f:/Programming/flyrank_ai_internship/assignment_fl04/pipeline_schema.json) for full machine-readable step definitions.*

---

## ⏱️ Time Accounting & ROI

| Execution Metric | Manual Coding | Automated Workflow Pipeline | Time Saved |
|---|---|---|---|
| **Average Build Time per Microservice** | 3.5 hours (210 mins) | 0.25 hours (15 mins pipeline + 15 mins human review) | **85.7% Reduction** |
| **5 Run Total Time** | 17.5 hours | 2.5 hours total | **15 Hours Saved** |

---

## 📑 5 Real Input Run Logs

1. [`run1_auth.md`](file:///f:/Programming/flyrank_ai_internship/assignment_fl04/runs/run1_auth.md): OAuth2 & JWT Password Bearer Authentication.
2. [`run2_billing.md`](file:///f:/Programming/flyrank_ai_internship/assignment_fl04/runs/run2_billing.md): Stripe Webhook Subscription Processing Engine.
3. [`run3_redis.md`](file:///f:/Programming/flyrank_ai_internship/assignment_fl04/runs/run3_redis.md): Async Redis Notification Worker Queue.
4. [`run4_vector.md`](file:///f:/Programming/flyrank_ai_internship/assignment_fl04/runs/run4_vector.md): PostgreSQL `pgvector` Embeddings Search Engine.
5. [`run5_tenant.md`](file:///f:/Programming/flyrank_ai_internship/assignment_fl04/runs/run5_tenant.md): Multi-tenant Organization RBAC Middleware.

---

## ⚠️ Failure Analysis & Required Human Checks

Key failure modes and mandatory human review requirements are documented in [`failure_analysis.md`](file:///f:/Programming/flyrank_ai_internship/assignment_fl04/failure_analysis.md):
1. Database Connection Pool Exhaustion under High Concurrency.
2. Secret Key Injection & Token Expiration Signatures.
3. Third-party API Rate Limits & Backoff Middleware.
