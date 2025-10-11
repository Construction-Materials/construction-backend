"""
Shared exceptions for the Recipe AI Extractor application.
"""

from typing import Optional


class RecipeExtractorException(Exception):
    """Base exception for Recipe AI Extractor."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class DomainException(RecipeExtractorException):
    """Domain layer exceptions."""
    pass


class ApplicationException(RecipeExtractorException):
    """Application layer exceptions."""
    pass


class InfrastructureException(RecipeExtractorException):
    """Infrastructure layer exceptions."""
    pass


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found."""
    
    def __init__(self, entity_type: str, entity_id: str):
        super().__init__(f"{entity_type} with ID {entity_id} not found")


class ValidationError(DomainException):
    """Raised when domain validation fails."""
    pass


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
    pass


class ExternalServiceError(InfrastructureException):
    """Raised when external service calls fail."""
    pass


class DatabaseError(InfrastructureException):
    """Raised when database operations fail."""
    pass
