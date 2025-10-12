"""
User DTOs for Application Layer.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserCreateDTO(BaseModel):
    """DTO for creating a new user."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    is_admin: bool = Field(default=False, description="Admin privileges")


class UserUpdateDTO(BaseModel):
    """DTO for updating user information."""
    email: Optional[EmailStr] = Field(None, description="User email address")
    is_admin: Optional[bool] = Field(None, description="Admin privileges")


class UserResponseDTO(BaseModel):
    """DTO for user response."""
    user_id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    is_admin: bool = Field(..., description="Admin status")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class UserLoginDTO(BaseModel):
    """DTO for user login."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserPasswordChangeDTO(BaseModel):
    """DTO for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")
