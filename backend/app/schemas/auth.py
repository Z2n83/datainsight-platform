"""
Auth-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """POST /api/auth/login request body."""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class RoleInfo(BaseModel):
    """Brief role info embedded in user response."""
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    """User info returned after login or from /api/auth/me."""
    id: str
    username: str
    real_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    roles: List[RoleInfo] = []
    permissions: List[str] = []
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """POST /api/auth/login response data."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo


class LogoutResponse(BaseModel):
    """POST /api/auth/logout response."""
    message: str = "已登出"
