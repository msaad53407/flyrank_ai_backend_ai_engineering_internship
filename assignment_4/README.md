# Week 4 · Assignment (BE-03 / A4) — Auth · Login & Protect

A secure, production-ready RESTful API implementing **Supabase Auth** as an external Identity Provider, **JSON Web Token (JWT)** verification, reusable dependency-based route protection, role-based authorization (401 vs 403), and interactive **Swagger UI** Bearer authentication.

---

## 🏛️ Architecture & The Trust Triangle

Secure authentication establishes a three-party trust model:

```
                      +-----------------------------+
                      |                             |
                      |  Identity Provider (Supabase)|
                      |  (Stores, hashes, signs)    |
                      |                             |
                      +-------^-------------+-------+
                              |             |
           1. Credentials     |             | 2. Signed JWT
          (email + password)  |             |    (Access Token)
                              |             |
                      +-------+-------------v-------+
                      |                             |
                      |        Client / UI          |
                      |                             |
                      +-------------+---------------+
                                    |
                                    | 3. Request + Authorization:
                                    |    Bearer <token>
                                    v
                      +-----------------------------+
                      |                             |
                      |     FastAPI Backend         |
                      |     (Verifies JWT signature)|
                      |                             |
                      +-----------------------------+
```

### Core Security Principles Applied
1. **Never roll your own crypto**: Passwords are never stored, hashed, or handled by backend database tables directly; Supabase Auth acts as the authoritative Identity Provider.
2. **Stateless verification**: Protected routes verify signed JWT access tokens passed via standard `Authorization: Bearer <token>` HTTP headers.
3. **Reusable guard pattern**: A single FastAPI `HTTPBearer` security dependency (`get_current_user`) guards all private endpoints consistently.

---

## 📡 API Reference Table

| Method | Endpoint | Description | Auth Required | Status Codes |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/` | Service health status and metadata | None | `200 OK` |
| `GET` | `/public/info` | Public open data accessible to any client | None | `200 OK` |
| `POST` | `/auth/signup` | Register new account with email and password | None | `201 Created`, `400 Bad Request` |
| `POST` | `/auth/login` | Authenticate user credentials & return JWT | None | `200 OK`, `400 Bad Request`, `401 Unauthorized` |
| `POST` | `/auth/logout` | Terminate user session | `Bearer <token>` | `204 No Content`, `401 Unauthorized` |
| `GET` | `/protected/profile` | Access private authenticated user profile | `Bearer <token>` | `200 OK`, `401 Unauthorized` |
| `GET` | `/protected/dashboard`| Access protected dashboard metrics | `Bearer <token>` | `200 OK`, `401 Unauthorized` |
| `GET` | `/protected/admin` | Admin-only metrics (demonstrates 403) | `Bearer <token>` | `200 OK`, `403 Forbidden`, `401 Unauthorized` |

---

## 🔒 401 Unauthorized vs. 403 Forbidden

- **`401 Unauthorized` ("I don't know who you are")**: The client did not provide an `Authorization: Bearer <token>` header, provided a malformed header, or the provided JWT was expired, invalid, or forged.
- **`403 Forbidden` ("I know who you are, but you are not allowed")**: The client provided a valid, verified JWT, but their role/permissions (e.g. `role: authenticated` vs `role: admin`) do not grant access to the requested administrative resource (`/protected/admin`).

---

## 🚀 Quickstart & Installation

### Option A: Using `uv` (Recommended)

1. **Clone repository and navigate to `assignment_4`:**
   ```bash
   cd assignment_4
   ```

2. **Create virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e . "pytest>=8.0.0" "httpx>=0.27.0"
   ```

3. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase URL & public anon key
   ```

4. **Run Server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Option B: Using standard `pip`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r pyproject.toml
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 Testing with `curl`

### 1. Public Info
```bash
curl -i http://localhost:8000/public/info
# Status: 200 OK
```

### 2. Sign Up
```bash
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"intern@flyrank.ai","password":"securePassword123"}'
# Status: 201 Created
```

### 3. Log In
```bash
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"intern@flyrank.ai","password":"securePassword123"}'
# Status: 200 OK -> Returns {"access_token": "...", "token_type": "bearer", ...}
```

### 4. Access Protected Route (Without Token)
```bash
curl -i http://localhost:8000/protected/profile
# Status: 401 Unauthorized -> {"error": "Access token required"}
```

### 5. Access Protected Route (With Token)
```bash
export TOKEN="<paste_access_token_here>"
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer $TOKEN"
# Status: 200 OK
```

### 6. Log Out
```bash
curl -i -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer $TOKEN"
# Status: 204 No Content
```

---

## 📑 Interactive Documentation (Swagger UI)

FastAPI automatically generates interactive OpenAPI documentation at `http://localhost:8000/docs`:
1. Open `http://localhost:8000/docs` in your browser.
2. Click the green **Authorize** button (padlock icon) at the top right.
3. Paste the JWT obtained from `POST /auth/login` into the `Value` field and click **Authorize**.
4. All protected endpoints (`/protected/profile`, `/protected/dashboard`, `/auth/logout`) now automatically attach the Bearer token when executing **Try it out** requests!

---

## 🤖 Stage 7: The AI Rematch ("AI vs Me")

### 1. Specification Prompt Given to AI
> *"Build a FastAPI backend with Supabase Auth that implements sign-up, login, logout, and protected routes. Include a reusable auth middleware, Swagger UI Bearer authorization with HTTPBearer, 401 on unauthenticated requests, and 403 on forbidden admin actions. Return 201 for signup, 200 for login/reads, and 204 for logout."*

### 2. Code Review & Structural Diff Comparison
1. **Token Extraction & Parsing**:
   - *AI Version*: Used simple string split (`request.headers.get("Authorization").split(" ")[1]`) without guarding against missing headers, lowercase `bearer`, or multiple spaces, resulting in unhandled `IndexError` / `AttributeError` 500 server crashes on malformed headers.
   - *Our Implementation*: Performs strict header structure validation: guards against empty headers, enforces the exact two-part format `Bearer <token>`, and returns standard `401 Unauthorized` with structured JSON errors instead of unhandled exceptions.
2. **Security & Credential Handling**:
   - *AI Version*: Attempted to store the Supabase `service_role` key inside local route definitions to bypass RLS policies, creating a critical vulnerability where client requests could impersonate any user.
   - *Our Implementation*: Uses strictly public `anon` keys in client-facing environments. All token claims are cryptographically verified through standard identity provider mechanisms.
3. **HTTP Status Code Conformity**:
   - *AI Version*: Returned `200 OK` for signup and `200 OK` with an empty JSON body for logout.
   - *Our Implementation*: Correctly respects REST conventions required by the specification: `201 Created` on `/auth/signup` and `204 No Content` on `/auth/logout`.

---

## 🚦 Automated Test Suite

Run the full pytest suite across all status codes:
```bash
pytest -v
```
