from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from auth_client import auth_service

# HTTPBearer defines the Bearer auth security scheme for Swagger UI (/docs)
security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Dict[str, Any]:
    """
    Reusable authentication dependency for protected routes.
    Extracts Bearer token from header and verifies it via Supabase Auth.
    """
    # 1. Check for Authorization header presence
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"}
        )
    
    # 2. Check header format
    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid token format. Format must be: Bearer <token>"}
        )
    
    token = parts[1].strip()
    
    # 3. Verify token with Supabase Auth
    user, error = auth_service.get_user(token)
    if error or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": error or "Invalid or expired access token"}
        )
    
    # Attach token to user object for downstream handlers like logout
    user["_token"] = token
    return user

def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Authorization dependency verifying admin permissions.
    Distinguishes 401 (Authentication failed) vs 403 (Forbidden).
    """
    role = current_user.get("role", "")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Forbidden: Admin role required for this action"}
        )
    return current_user
