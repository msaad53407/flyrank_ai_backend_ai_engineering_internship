import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_health():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_public_info():
    response = client.get("/public/info")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome stranger!" in data["message"]
    assert "identity_provider" in data

def test_signup_validation_errors():
    # Missing email
    r1 = client.post("/auth/signup", json={"email": "", "password": "password123"})
    assert r1.status_code == 400
    assert "error" in r1.json()

    # Short password
    r2 = client.post("/auth/signup", json={"email": "short@example.com", "password": "123"})
    assert r2.status_code == 400
    assert "error" in r2.json()

def test_signup_and_login_flow():
    test_email = "intern.test@flyrank.ai"
    test_password = "secure_password_456"

    # 1. Sign up
    signup_res = client.post("/auth/signup", json={"email": test_email, "password": test_password})
    assert signup_res.status_code == 201
    signup_data = signup_res.json()
    assert "user" in signup_data
    assert signup_data["user"]["email"] == test_email

    # 2. Login with wrong password
    bad_login = client.post("/auth/login", json={"email": test_email, "password": "wrongpassword"})
    assert bad_login.status_code == 401
    assert "Invalid login credentials" in bad_login.json()["error"]

    # 3. Login with correct password
    login_res = client.post("/auth/login", json={"email": test_email, "password": test_password})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    token = login_data["access_token"]
    assert len(token) > 20

    # 4. Access protected profile with token
    headers = {"Authorization": f"Bearer {token}"}
    profile_res = client.get("/protected/profile", headers=headers)
    assert profile_res.status_code == 200
    profile_data = profile_res.json()
    assert profile_data["email"] == test_email
    assert "verified" in profile_data["message"]

    # 5. Access second protected route (dashboard) with same token (reusable guard)
    dash_res = client.get("/protected/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["user_email"] == test_email

    # 6. Logout with token
    logout_res = client.post("/auth/logout", headers=headers)
    assert logout_res.status_code == 204

def test_protected_routes_without_or_bad_token():
    # No token
    r_no_token = client.get("/protected/profile")
    assert r_no_token.status_code == 401
    assert "Access token required" in r_no_token.json()["error"]

    # Malformed token
    r_bad_header = client.get("/protected/profile", headers={"Authorization": "Basic 12345"})
    assert r_bad_header.status_code == 401
    assert "Invalid token format" in r_bad_header.json()["error"]

    # Fake/tampered JWT
    r_fake_jwt = client.get("/protected/profile", headers={"Authorization": "Bearer fake.jwt.token"})
    assert r_fake_jwt.status_code == 401
    assert "Invalid" in r_fake_jwt.json()["error"] or "malformed" in r_fake_jwt.json()["error"]

def test_authorization_401_vs_403():
    # Standard user
    user_email = "regular.user@flyrank.ai"
    client.post("/auth/signup", json={"email": user_email, "password": "password123"})
    login_user = client.post("/auth/login", json={"email": user_email, "password": "password123"}).json()
    user_token = login_user["access_token"]

    # Standard user can access profile (200)
    assert client.get("/protected/profile", headers={"Authorization": f"Bearer {user_token}"}).status_code == 200

    # Standard user CANNOT access admin endpoint (403 Forbidden)
    res_403 = client.get("/protected/admin", headers={"Authorization": f"Bearer {user_token}"})
    assert res_403.status_code == 403
    assert "Admin role required" in res_403.json()["error"]

    # Admin user
    admin_email = "admin@flyrank.ai"
    client.post("/auth/signup", json={"email": admin_email, "password": "password123"})
    login_admin = client.post("/auth/login", json={"email": admin_email, "password": "password123"}).json()
    admin_token = login_admin["access_token"]

    # Admin CAN access admin endpoint (200 OK)
    res_admin = client.get("/protected/admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    assert res_admin.json()["admin"] == admin_email
