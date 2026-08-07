"""
Auth router: /api/auth/*
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo, RoleInfo
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post("/login")
async def login(body: LoginRequest, db=Depends(get_db)):
    """
    User login. Returns JWT access token and user info.

    POST /api/auth/login
    """
    svc = AuthService(db)
    user = await svc.authenticate(body.username, body.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    from app.core.security import create_access_token
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
    )

    permissions = await svc.get_user_permissions(user)

    return {
        "code": 0,
        "message": "success",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "email": user.email,
                "phone": user.phone,
                "avatar_url": user.avatar_url,
                "roles": [
                    {"id": r.id, "name": r.name, "description": r.description}
                    for r in user.roles
                ],
                "permissions": permissions,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            },
        },
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    User logout.

    POST /api/auth/logout
    """
    return {
        "code": 0,
        "message": "已登出",
        "data": None,
    }


@router.get("/me")
async def me(current_user: User = Depends(get_current_user), db=Depends(get_db)):
    """
    Get current user info.

    GET /api/auth/me
    """
    svc = AuthService(db)
    permissions = await svc.get_user_permissions(current_user)

    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "real_name": current_user.real_name,
            "email": current_user.email,
            "phone": current_user.phone,
            "avatar_url": current_user.avatar_url,
            "roles": [
                {"id": r.id, "name": r.name, "description": r.description}
                for r in current_user.roles
            ],
            "permissions": permissions,
            "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        },
    }
