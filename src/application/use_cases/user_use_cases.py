"""
User Use Cases for Application Layer.
"""

from typing import List, Optional
from uuid import UUID
from passlib.context import CryptContext

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.application.dtos.user_dto import (
    UserCreateDTO, UserUpdateDTO, UserResponseDTO, 
    UserLoginDTO, UserPasswordChangeDTO
)
from src.shared.exceptions import EntityNotFoundError, ValidationError, BusinessRuleViolationError


class UserUseCases:
    """User use cases implementation."""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async def create_user(self, user_dto: UserCreateDTO) -> UserResponseDTO:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self._user_repository.get_by_email(user_dto.email)
        if existing_user:
            raise BusinessRuleViolationError("User with this email already exists")
        
        # Create domain entity
        user = User(
            email=user_dto.email,
            is_admin=user_dto.is_admin
        )
        user.set_password_hash(self._pwd_context.hash(user_dto.password))
        
        # Save to repository
        created_user = await self._user_repository.create(user)
        
        return UserResponseDTO(
            user_id=created_user.id,
            email=created_user.email,
            is_admin=created_user.is_admin,
            created_at=created_user.created_at
        )
    
    async def get_user_by_id(self, user_id: UUID) -> UserResponseDTO:
        """Get user by ID."""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))
        
        return UserResponseDTO(
            user_id=user.id,
            email=user.email,
            is_admin=user.is_admin,
            created_at=user.created_at
        )
    
    async def get_user_by_email(self, email: str) -> UserResponseDTO:
        """Get user by email."""
        user = await self._user_repository.get_by_email(email)
        if not user:
            raise EntityNotFoundError("User", email)
        
        return UserResponseDTO(
            user_id=user.id,
            email=user.email,
            is_admin=user.is_admin,
            created_at=user.created_at
        )
    
    async def update_user(self, user_id: UUID, user_dto: UserUpdateDTO) -> UserResponseDTO:
        """Update user information."""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))
        
        # Update fields if provided
        if user_dto.email is not None:
            # Check if new email is already taken
            existing_user = await self._user_repository.get_by_email(user_dto.email)
            if existing_user and existing_user.id != user_id:
                raise BusinessRuleViolationError("User with this email already exists")
            user.set_email(user_dto.email)
        
        if user_dto.is_admin is not None:
            user.set_admin_status(user_dto.is_admin)
        
        # Save changes
        updated_user = await self._user_repository.update(user)
        
        return UserResponseDTO(
            user_id=updated_user.id,
            email=updated_user.email,
            is_admin=updated_user.is_admin,
            created_at=updated_user.created_at
        )
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user."""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))
        
        return await self._user_repository.delete(user_id)
    
    async def list_users(self, limit: int = 100, offset: int = 0) -> List[UserResponseDTO]:
        """List all users."""
        users = await self._user_repository.list_all(limit=limit, offset=offset)
        
        return [
            UserResponseDTO(
                user_id=user.id,
                email=user.email,
                is_admin=user.is_admin,
                created_at=user.created_at
            )
            for user in users
        ]
    
    async def authenticate_user(self, login_dto: UserLoginDTO) -> UserResponseDTO:
        """Authenticate user with email and password."""
        user = await self._user_repository.get_by_email(login_dto.email)
        if not user:
            raise EntityNotFoundError("User", login_dto.email)
        
        # Verify password
        if not self._pwd_context.verify(login_dto.password, user.password_hash):
            raise ValidationError("Invalid password")
        
        return UserResponseDTO(
            user_id=user.id,
            email=user.email,
            is_admin=user.is_admin,
            created_at=user.created_at
        )
    
    async def change_password(self, user_id: UUID, password_dto: UserPasswordChangeDTO) -> bool:
        """Change user password."""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))
        
        # Verify current password
        if not self._pwd_context.verify(password_dto.current_password, user.password_hash):
            raise ValidationError("Current password is incorrect")
        
        # Set new password
        user.set_password_hash(self._pwd_context.hash(password_dto.new_password))
        
        await self._user_repository.update(user)
        return True
