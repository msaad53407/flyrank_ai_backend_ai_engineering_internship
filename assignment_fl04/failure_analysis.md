# Failure Analysis & Human-in-the-Loop Review Points

While the automated 4-step pipeline reduces development time by **85%**, mandatory human verification is required at three key failure points:

### 1. Database Connection Pool Exhaustion under High Concurrency
- **Failure Mode:** AI-generated SQL connection code opens new database connections per request without pooling constraints.
- **Human Check:** Senior engineer must verify that connection pooling (e.g. `SQLAlchemy` pool_size or `psycopg2` ThreadedConnectionPool) is explicitly configured.

### 2. JWT Token Revocation & Secret Management
- **Failure Mode:** AI might output hardcoded fallback secret keys (`SECRET_KEY="secret"`) or omit token expiration checks.
- **Human Check:** Mandatory security review to ensure secrets are injected solely via `.env` environment variables and JWT expiration signatures are enforced.

### 3. Third-Party Rate Limit & Exponential Backoff Handling
- **Failure Mode:** External API webhooks (e.g. Stripe, Redis queues) lack retries or exception handling for HTTP 429 rate limits.
- **Human Check:** Human developer must inspect async retry middleware (e.g., `tenacity` library) before deploying to production.
