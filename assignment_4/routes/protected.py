from fastapi import APIRouter, Depends
from typing import Dict, Any
from dependencies import get_current_user, require_admin

router = APIRouter(prefix="/protected", tags=["Protected Gates"])

@router.get(
    "/profile",
    summary="Read private profile data",
    description="Guarded route that requires a valid JWT in Authorization: Bearer <token> header."
)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "role": current_user.get("role"),
        "app_metadata": current_user.get("app_metadata", {}),
        "user_metadata": current_user.get("user_metadata", {}),
        "message": f"Hello {current_user.get('email')}, your token signature is verified."
    }

@router.get(
    "/dashboard",
    summary="Read private dashboard metrics",
    description="Second protected route demonstrating reusable auth middleware across the API."
)
async def get_dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "user_id": current_user.get("id"),
        "user_email": current_user.get("email"),
        "status": "active",
        "recent_audits_count": 5,
        "subscription_tier": "pro_intern",
        "message": "Welcome to your protected analytics dashboard."
    }

@router.get(
    "/admin",
    summary="Admin-only action (403 test)",
    description="Demonstrates authorization (403 Forbidden) vs authentication (401 Unauthorized)."
)
async def get_admin_metrics(current_user: Dict[str, Any] = Depends(require_admin)):
    return {
        "admin": current_user.get("email"),
        "all_users_count": 42,
        "system_status": "nominal"
    }
