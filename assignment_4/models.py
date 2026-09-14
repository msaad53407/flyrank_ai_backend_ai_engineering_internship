from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

class SignUpRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password (min 6 characters)")

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class UserData(BaseModel):
    id: str
    email: Optional[str] = None
    role: Optional[str] = "authenticated"
    created_at: Optional[str] = None
    app_metadata: Optional[Dict[str, Any]] = None
    user_metadata: Optional[Dict[str, Any]] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserData] = None

class PublicInfoResponse(BaseModel):
    message: str
    version: str
    identity_provider: str

class ProfileResponse(BaseModel):
    id: str
    email: Optional[str]
    role: Optional[str]
    app_metadata: Dict[str, Any] = Field(default_factory=dict)
    user_metadata: Dict[str, Any] = Field(default_factory=dict)

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
