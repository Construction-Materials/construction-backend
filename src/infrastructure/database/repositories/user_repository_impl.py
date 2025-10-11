"""
User Repository Implementation (Adapter).
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models import UserModel
from src.shared.exceptions import DatabaseError


class UserRepositoryImpl(UserRepository):
    """User repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        try:
            user_model = UserModel(
                user_id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                is_admin=user.is_admin,
                created_at=user.created_at
            )
            
            self._session.add(user_model)
            await self._session.commit()
            await self._session.refresh(user_model)
            
            return self._to_domain(user_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to create user: {str(e)}") from e
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        try:
            result = await self._session.execute(
                select(UserModel).where(UserModel.user_id == user_id)
            )
            user_model = result.scalar_one_or_none()
            
            return self._to_domain(user_model) if user_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get user by ID: {str(e)}") from e
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            result = await self._session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user_model = result.scalar_one_or_none()
            
            return self._to_domain(user_model) if user_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get user by email: {str(e)}") from e
    
    async def update(self, user: User) -> User:
        """Update existing user."""
        try:
            result = await self._session.execute(
                select(UserModel).where(UserModel.user_id == user.id)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                raise DatabaseError(f"User with ID {user.id} not found")
            
            user_model.email = user.email
            user_model.password_hash = user.password_hash
            user_model.is_admin = user.is_admin
            
            await self._session.commit()
            await self._session.refresh(user_model)
            
            return self._to_domain(user_model)
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to update user: {str(e)}") from e
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID."""
        try:
            result = await self._session.execute(
                delete(UserModel).where(UserModel.user_id == user_id)
            )
            await self._session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self._session.rollback()
            raise DatabaseError(f"Failed to delete user: {str(e)}") from e
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List all users with pagination."""
        try:
            result = await self._session.execute(
                select(UserModel)
                .offset(offset)
                .limit(limit)
                .order_by(UserModel.created_at.desc())
            )
            user_models = result.scalars().all()
            
            return [self._to_domain(user_model) for user_model in user_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list users: {str(e)}") from e
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        try:
            result = await self._session.execute(
                select(UserModel.user_id).where(UserModel.email == email)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            raise DatabaseError(f"Failed to check user existence: {str(e)}") from e
    
    def _to_domain(self, user_model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            user_id=user_model.user_id,
            email=user_model.email,
            password_hash=user_model.password_hash,
            is_admin=user_model.is_admin,
            created_at=user_model.created_at
        )
