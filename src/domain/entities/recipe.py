"""
Recipe Domain Entity.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from src.shared.exceptions import ValidationError


class Recipe:
    """Recipe domain entity."""
    
    def __init__(
        self,
        recipe_id: Optional[UUID] = None,
        user_id: UUID = None,
        title: str = "",
        external_url: Optional[str] = None,
        preparation_steps: str = "",
        prep_time_minutes: int = 0,
        created_at: Optional[datetime] = None
    ):
        """Initialize Recipe entity."""
        if user_id is None:
            raise ValidationError("User ID is required for recipe")
        
        self._id = recipe_id or uuid4()
        self._user_id = user_id
        self._title = title
        self._external_url = external_url
        self._preparation_steps = preparation_steps
        self._prep_time_minutes = prep_time_minutes
        self._created_at = created_at or datetime.utcnow()
    
    @property
    def id(self) -> UUID:
        """Get recipe ID."""
        return self._id
    
    @property
    def user_id(self) -> UUID:
        """Get user ID (owner)."""
        return self._user_id
    
    @property
    def title(self) -> str:
        """Get recipe title."""
        return self._title
    
    @property
    def external_url(self) -> Optional[str]:
        """Get external URL."""
        return self._external_url
    
    @property
    def preparation_steps(self) -> str:
        """Get preparation steps."""
        return self._preparation_steps
    
    @property
    def prep_time_minutes(self) -> int:
        """Get preparation time in minutes."""
        return self._prep_time_minutes
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    def set_title(self, title: str) -> None:
        """Set recipe title with validation."""
        if not title or not title.strip():
            raise ValidationError("Recipe title cannot be empty")
        
        self._title = title.strip()
    
    def set_external_url(self, url: Optional[str]) -> None:
        """Set external URL with validation."""
        if url is not None:
            url = url.strip()
            if not url:
                url = None
            elif not url.startswith(('http://', 'https://')):
                raise ValidationError("External URL must start with http:// or https://")
        
        self._external_url = url
    
    def set_preparation_steps(self, steps: str) -> None:
        """Set preparation steps."""
        self._preparation_steps = steps or ""
    
    def set_prep_time(self, minutes: int) -> None:
        """Set preparation time with validation."""
        if minutes < 0:
            raise ValidationError("Preparation time cannot be negative")
        
        self._prep_time_minutes = minutes
    
    def __eq__(self, other) -> bool:
        """Check equality with another recipe."""
        if not isinstance(other, Recipe):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash for recipe."""
        return hash(self._id)
