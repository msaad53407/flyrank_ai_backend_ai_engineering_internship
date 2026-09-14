from fastapi import APIRouter, HTTPException, status, Depends, Response
from typing import Dict, Any
from models import SignUpRequest, LoginRequest, TokenResponse, ErrorResponse
from auth_client import auth_service
from dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Registers a user with email and password via Supabase Auth without storing passwords locally.",
    responses={
        201: {"description": "User created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid or missing registration data"}
    }
)
async def sign_up(body: SignUpRequest):
    # Validation
    if not body.email or not body.email.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "Email is required"})
    if not body.password or len(body.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Password must be at least 6 characters long"}
        )
    
    user_data, error = auth_service.sign_up(body.email.strip(), body.password)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": error})
    
    return {
        "message": "User registered successfully",
        "user": user_data
    }

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Authenticate user & obtain JWT",
    description="Verifies user credentials and returns an access token (JWT) and refresh token.",
    responses={
        200: {"model": TokenResponse, "description": "Authentication successful"},
        400: {"model": ErrorResponse, "description": "Missing credentials"},
        401: {"model": ErrorResponse, "description": "Invalid login credentials"}
    }
)
async def login(body: LoginRequest):
    if not body.email or not body.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Both email and password are required"}
        )
    
    session_data, error = auth_service.sign_in_with_password(body.email.strip(), body.password)
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid login credentials"}
        )
    
    return session_data

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End user session",
    description="Terminates active user session and invalidates access token. Requires Bearer authorization.",
    responses={
        204: {"description": "Session ended successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    token = current_user.get("_token", "")
    auth_service.sign_out(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
