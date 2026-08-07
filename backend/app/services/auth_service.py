"""
Authentication business logic.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, Role, Permission


class AuthService:
    """Authentication and user management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Verify credentials and return user, or None."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return None

        if user.status == "disabled":
            return None

        if not verify_password(password, user.password_hash):
            return None

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

        return user

    async def get_user_permissions(self, user: User) -> list[str]:
        """Collect all permission codes for a user from their roles."""
        codes: set[str] = set()
        for role in user.roles:
            # Permissions might be loaded or not
            if role.permissions:
                for perm in role.permissions:
                    codes.add(perm.code)
        return sorted(codes)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID with roles and permissions loaded."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        username: str,
        password: str,
        real_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        role_ids: Optional[list[str]] = None,
    ) -> User:
        """Create a new user."""
        user = User(
            username=username,
            password_hash=hash_password(password),
            real_name=real_name,
            email=email,
            phone=phone,
        )

        if role_ids:
            result = await self.db.execute(
                select(Role).where(Role.id.in_(role_ids))
            )
            user.roles = list(result.scalars().all())

        self.db.add(user)
        await self.db.flush()
        return user
