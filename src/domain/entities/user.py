"""
User Domain Entity.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.shared.exceptions import ValidationError


class User:
    """User domain entity."""
    
    def __init__(
        self,
        user_id: Optional[UUID] = None,
        email: str = "",
        password_hash: str = "",
        is_admin: bool = False,
        created_at: Optional[datetime] = None
    ):
        """Initialize User entity."""
        self._id = user_id or uuid4()
        self._email = email
        self._password_hash = password_hash
        self._is_admin = is_admin
        self._created_at = created_at or datetime.utcnow()
    
    @property
    def id(self) -> UUID:
        """Get user ID."""
        return self._id
    
    @property
    def email(self) -> str:
        """Get user email."""
        return self._email
    
    @property
    def password_hash(self) -> str:
        """Get password hash."""
        return self._password_hash
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self._is_admin
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    def set_email(self, email: str) -> None:
        """Set user email with validation."""
        if not email or not email.strip():
            raise ValidationError("Email cannot be empty")
        
        if "@" not in email:
            raise ValidationError("Invalid email format")
        
        self._email = email.strip().lower()
    
    def set_password_hash(self, password_hash: str) -> None:
        """Set password hash."""
        if not password_hash:
            raise ValidationError("Password hash cannot be empty")
        
        self._password_hash = password_hash
    
    def set_admin_status(self, is_admin: bool) -> None:
        """Set admin status."""
        self._is_admin = is_admin
    
    def __eq__(self, other) -> bool:
        """Check equality with another user."""
        if not isinstance(other, User):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash for user."""
        return hash(self._id)
