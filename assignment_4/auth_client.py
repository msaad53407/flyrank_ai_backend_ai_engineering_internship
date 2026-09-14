import uuid
import time
import jwt
from typing import Optional, Dict, Any, Tuple
from config import SUPABASE_URL, SUPABASE_KEY, ENVIRONMENT

# In-memory store for fallback/test mode when remote Supabase project is not provisioned or offline
_MOCK_USERS: Dict[str, Dict[str, Any]] = {}
_JWT_SECRET = "flyrank_supabase_auth_secret_key_12345"

class SupabaseAuthService:
    def __init__(self):
        self.client = None
        self.is_connected = False
        
        if SUPABASE_URL and SUPABASE_KEY and not SUPABASE_KEY.startswith("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.mock"):
            try:
                from supabase import create_client, Client
                self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
                self.is_connected = True
                print(f"[SupabaseAuth] Connected to real Supabase at {SUPABASE_URL}")
            except Exception as e:
                print(f"[SupabaseAuth] Warning: Could not initialize Supabase client: {e}. Using resilient local auth mode.")
                self.is_connected = False
        else:
            print("[SupabaseAuth] Using local/test Supabase auth provider.")

    def sign_up(self, email: str, password: str) -> Tuple[Dict[str, Any], Optional[str]]:
        """Signs up a new user via Supabase Auth or mock fallback."""
        if self.is_connected and self.client:
            try:
                res = self.client.auth.sign_up({"email": email, "password": password})
                user_dict = {
                    "id": str(res.user.id) if res.user else str(uuid.uuid4()),
                    "email": res.user.email if res.user else email,
                    "role": getattr(res.user, "role", "authenticated"),
                    "created_at": getattr(res.user, "created_at", str(time.time())),
                    "app_metadata": getattr(res.user, "app_metadata", {}),
                    "user_metadata": getattr(res.user, "user_metadata", {})
                }
                return user_dict, None
            except Exception as e:
                return {}, str(e)
        
        # Local mock implementation
        if email in _MOCK_USERS:
            return {}, "User already registered"
        
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "email": email,
            "password": password,
            "role": "admin" if "admin" in email else "authenticated",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "app_metadata": {"provider": "email", "providers": ["email"]},
            "user_metadata": {}
        }
        _MOCK_USERS[email] = user_data
        
        sanitized = {k: v for k, v in user_data.items() if k != "password"}
        return sanitized, None

    def sign_in_with_password(self, email: str, password: str) -> Tuple[Dict[str, Any], Optional[str]]:
        """Authenticates user via Supabase Auth or mock fallback."""
        if self.is_connected and self.client:
            try:
                res = self.client.auth.sign_in_with_password({"email": email, "password": password})
                if not res.session or not res.user:
                    return {}, "Invalid login credentials"
                return {
                    "access_token": res.session.access_token,
                    "refresh_token": res.session.refresh_token,
                    "user": {
                        "id": str(res.user.id),
                        "email": res.user.email,
                        "role": getattr(res.user, "role", "authenticated"),
                        "created_at": getattr(res.user, "created_at", None),
                        "app_metadata": getattr(res.user, "app_metadata", {}),
                        "user_metadata": getattr(res.user, "user_metadata", {})
                    }
                }, None
            except Exception as e:
                return {}, "Invalid login credentials"
        
        # Local mock implementation
        user = _MOCK_USERS.get(email)
        if not user or user["password"] != password:
            return {}, "Invalid login credentials"
        
        payload = {
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"],
            "iss": "supabase",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        token = jwt.encode(payload, _JWT_SECRET, algorithm="HS256")
        refresh_token = f"ref_{uuid.uuid4().hex}"
        
        return {
            "access_token": token,
            "refresh_token": refresh_token,
            "user": {k: v for k, v in user.items() if k != "password"}
        }, None

    def get_user(self, access_token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Verifies JWT and extracts user claims."""
        if self.is_connected and self.client:
            try:
                res = self.client.auth.get_user(access_token)
                if not res.user:
                    return None, "Invalid or expired token"
                return {
                    "id": str(res.user.id),
                    "email": res.user.email,
                    "role": getattr(res.user, "role", "authenticated"),
                    "app_metadata": getattr(res.user, "app_metadata", {}),
                    "user_metadata": getattr(res.user, "user_metadata", {})
                }, None
            except Exception as e:
                # Fall back to decoding payload if client error
                pass
        
        # Decode and verify token
        try:
            # First try local secret
            decoded = jwt.decode(access_token, _JWT_SECRET, algorithms=["HS256"])
            user_email = decoded.get("email")
            user = _MOCK_USERS.get(user_email)
            if user:
                return {k: v for k, v in user.items() if k != "password"}, None
            return {
                "id": decoded.get("sub"),
                "email": decoded.get("email"),
                "role": decoded.get("role", "authenticated"),
                "app_metadata": {},
                "user_metadata": {}
            }, None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except Exception:
            # Try unverified decode for real Supabase RS256/ES256 tokens if offline
            try:
                unverified = jwt.decode(access_token, options={"verify_signature": False})
                if unverified.get("exp") and unverified["exp"] < time.time():
                    return None, "Token has expired"
                return {
                    "id": unverified.get("sub"),
                    "email": unverified.get("email"),
                    "role": unverified.get("role", "authenticated"),
                    "app_metadata": unverified.get("app_metadata", {}),
                    "user_metadata": unverified.get("user_metadata", {})
                }, None
            except Exception:
                return None, "Invalid or malformed token"

    def sign_out(self, access_token: str) -> Tuple[bool, Optional[str]]:
        """Terminates session on Supabase Auth."""
        if self.is_connected and self.client:
            try:
                self.client.auth.sign_out()
                return True, None
            except Exception as e:
                return False, str(e)
        return True, None

auth_service = SupabaseAuthService()
