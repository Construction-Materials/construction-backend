"""
User API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.application.dtos.user_dto import (
    UserCreateDTO, UserUpdateDTO, UserResponseDTO, 
    UserLoginDTO, UserPasswordChangeDTO
)
from src.application.use_cases.user_use_cases import UserUseCases
from src.infrastructure.api.dependencies import get_user_use_cases, get_current_user

router = APIRouter()


@router.get("/public", response_model=List[UserResponseDTO])
async def list_users_public(
    limit: int = 100,
    offset: int = 0,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """List all users (public endpoint for testing)."""
    return await user_use_cases.list_users(limit=limit, offset=offset)


@router.post("/", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_dto: UserCreateDTO,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Create a new user."""
    return await user_use_cases.create_user(user_dto)


@router.get("/me", response_model=UserResponseDTO)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Get current user information."""
    return await user_use_cases.get_user_by_id(current_user["user_id"])


@router.get("/{user_id}", response_model=UserResponseDTO)
async def get_user(
    user_id: UUID,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Get user by ID."""
    return await user_use_cases.get_user_by_id(user_id)


@router.put("/{user_id}", response_model=UserResponseDTO)
async def update_user(
    user_id: UUID,
    user_dto: UserUpdateDTO,
    current_user: dict = Depends(get_current_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Update user information."""
    # Check if user is updating themselves or is admin
    if current_user["user_id"] != user_id and not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    return await user_use_cases.update_user(user_id, user_dto)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Delete user."""
    # Check if user is deleting themselves or is admin
    if current_user["user_id"] != user_id and not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    await user_use_cases.delete_user(user_id)


@router.get("/", response_model=List[UserResponseDTO])
async def list_users(
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """List all users (admin only)."""
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return await user_use_cases.list_users(limit=limit, offset=offset)


@router.post("/login", response_model=UserResponseDTO)
async def login_user(
    login_dto: UserLoginDTO,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Authenticate user."""
    return await user_use_cases.authenticate_user(login_dto)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_dto: UserPasswordChangeDTO,
    current_user: dict = Depends(get_current_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """Change user password."""
    await user_use_cases.change_password(current_user["user_id"], password_dto)
