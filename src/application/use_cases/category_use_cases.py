"""
Category Use Cases for Application Layer.
"""

from typing import List
from uuid import UUID

from src.domain.entities.category import Category
from src.domain.repositories.category_repository import CategoryRepository
from src.application.dtos.category_dto import (
    CategoryCreateDTO,
    CategoryUpdateDTO,
    CategoryResponseDTO,
    CategoryListResponseDTO,
    CategorySearchDTO
)
from src.shared.exceptions import EntityNotFoundError, ValidationError


class CategoryUseCases:
    """Category use cases implementation."""
    
    def __init__(self, category_repository: CategoryRepository):
        self._category_repository = category_repository
    
    async def create_category(self, category_dto: CategoryCreateDTO) -> CategoryResponseDTO:
        """Create a new category."""
        # Create domain entity
        category = Category(
            name=category_dto.name
        )
        
        # Save to repository
        created_category = await self._category_repository.create(category)
        
        return CategoryResponseDTO(
            category_id=created_category.id,
            name=created_category.name,
            created_at=created_category.created_at
        )
    
    async def get_category_by_id(self, category_id: UUID) -> CategoryResponseDTO:
        """Get category by ID."""
        category = await self._category_repository.get_by_id(category_id)
        if not category:
            raise EntityNotFoundError("Category", str(category_id))
        
        return CategoryResponseDTO(
            category_id=category.id,
            name=category.name,
            created_at=category.created_at
        )
    
    async def update_category(self, category_id: UUID, category_dto: CategoryUpdateDTO) -> CategoryResponseDTO:
        """Update category."""
        category = await self._category_repository.get_by_id(category_id)
        if not category:
            raise EntityNotFoundError("Category", str(category_id))
        
        # Update fields if provided
        if category_dto.name is not None:
            category.set_name(category_dto.name)
        
        # Save changes
        updated_category = await self._category_repository.update(category)
        
        return CategoryResponseDTO(
            category_id=updated_category.id,
            name=updated_category.name,
            created_at=updated_category.created_at
        )
    
    async def delete_category(self, category_id: UUID) -> bool:
        """Delete category."""
        category = await self._category_repository.get_by_id(category_id)
        if not category:
            raise EntityNotFoundError("Category", str(category_id))
        
        return await self._category_repository.delete(category_id)
    
    async def list_all_categories(self, limit: int = 100, offset: int = 0) -> CategoryListResponseDTO:
        """List all categories."""
        categories = await self._category_repository.list_all(limit=limit, offset=offset)
        total = await self._category_repository.count_all()
        
        return CategoryListResponseDTO(
            categories=[
                CategoryResponseDTO(
                    category_id=category.id,
                    name=category.name,
                    created_at=category.created_at
                )
                for category in categories
            ],
            total=total,
            page=(offset // limit) + 1 if limit > 0 else 1,
            size=limit
        )
    
    async def search_categories(self, search_dto: CategorySearchDTO) -> CategoryListResponseDTO:
        """Search categories by name."""
        categories = await self._category_repository.search_by_name(
            name=search_dto.query,
            limit=search_dto.size,
            offset=(search_dto.page - 1) * search_dto.size
        )
        
        total = len(categories)
        
        return CategoryListResponseDTO(
            categories=[
                CategoryResponseDTO(
                    category_id=category.id,
                    name=category.name,
                    created_at=category.created_at
                )
                for category in categories
            ],
            total=total,
            page=search_dto.page,
            size=search_dto.size
        )

