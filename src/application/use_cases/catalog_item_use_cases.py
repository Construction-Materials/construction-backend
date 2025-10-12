"""
Catalog Item Use Cases Implementation.
"""

from typing import List
from uuid import UUID

from src.application.dtos.catalog_item_dto import (
    CatalogItemCreateDTO, CatalogItemUpdateDTO, CatalogItemResponseDTO,
    CatalogItemListResponseDTO, CatalogItemSearchDTO, CatalogItemSimpleDTO,
    CatalogItemSimpleListResponseDTO
)
from src.domain.repositories.catalog_item_repository import CatalogItemRepository
from src.domain.entities.catalog_item import CatalogItem
from src.shared.exceptions import EntityNotFoundError, ValidationError


class CatalogItemUseCases:
    """Catalog item use cases implementation."""
    
    def __init__(self, catalog_item_repository: CatalogItemRepository):
        self._catalog_item_repository = catalog_item_repository
    
    async def create_catalog_item(self, item_dto: CatalogItemCreateDTO) -> CatalogItemResponseDTO:
        """Create a new catalog item."""
        # Normalize name for consistent checking and storage
        normalized_name = item_dto.name.strip().lower()
        
        # Check if item with same normalized name already exists
        existing_item = await self._catalog_item_repository.get_by_name(normalized_name)
        if existing_item:
            raise ValidationError(f"Catalog item with name '{item_dto.name}' already exists")
        
        # Create new catalog item with normalized name
        catalog_item = CatalogItem(name=normalized_name)
        created_item = await self._catalog_item_repository.create(catalog_item)
        
        return CatalogItemResponseDTO(
            item_id=created_item.id,
            name=created_item.name,
            last_used=created_item.last_used
        )
    
    async def get_catalog_item(self, item_id: UUID) -> CatalogItemResponseDTO:
        """Get catalog item by ID."""
        catalog_item = await self._catalog_item_repository.get_by_id(item_id)
        if not catalog_item:
            raise EntityNotFoundError("Catalog item", str(item_id))
        
        return CatalogItemResponseDTO(
            item_id=catalog_item.id,
            name=catalog_item.name,
            last_used=catalog_item.last_used
        )
    
    async def update_catalog_item(self, item_id: UUID, item_dto: CatalogItemUpdateDTO) -> CatalogItemResponseDTO:
        """Update catalog item."""
        catalog_item = await self._catalog_item_repository.get_by_id(item_id)
        if not catalog_item:
            raise EntityNotFoundError("Catalog item", str(item_id))
        
        # Check if new name conflicts with existing item
        if item_dto.name and item_dto.name != catalog_item.name:
            normalized_name = item_dto.name.strip().lower()
            existing_item = await self._catalog_item_repository.get_by_name(normalized_name)
            if existing_item:
                raise ValidationError(f"Catalog item with name '{item_dto.name}' already exists")
        
        # Update item with normalized name
        if item_dto.name:
            catalog_item.set_name(item_dto.name)
        
        updated_item = await self._catalog_item_repository.update(catalog_item)
        
        return CatalogItemResponseDTO(
            item_id=updated_item.id,
            name=updated_item.name,
            last_used=updated_item.last_used
        )
    
    async def delete_catalog_item(self, item_id: UUID) -> bool:
        """Delete catalog item."""
        catalog_item = await self._catalog_item_repository.get_by_id(item_id)
        if not catalog_item:
            raise EntityNotFoundError("Catalog item", str(item_id))
        
        return await self._catalog_item_repository.delete(item_id)
    
    async def list_catalog_items(self, limit: int = 100, offset: int = 0) -> CatalogItemListResponseDTO:
        """List all catalog items."""
        items = await self._catalog_item_repository.list_all(limit=limit, offset=offset)
        
        return CatalogItemListResponseDTO(
            items=[
                CatalogItemResponseDTO(
                    item_id=item.id,
                    name=item.name,
                    last_used=item.last_used
                )
                for item in items
            ],
            total=len(items),
            page=(offset // limit) + 1,
            size=limit
        )
    
    async def list_catalog_items_simple(self, limit: int = 100, offset: int = 0) -> CatalogItemSimpleListResponseDTO:
        """List all catalog items without last_used field (for sorted lists)."""
        items = await self._catalog_item_repository.list_all(limit=limit, offset=offset)
        total_count = await self._catalog_item_repository.count_all()
        
        # Calculate pagination info
        current_page = (offset // limit) + 1
        has_next = (offset + limit) < total_count
        has_prev = offset > 0
        
        # Generate navigation links
        next_offset = offset + limit if has_next else None
        prev_offset = max(0, offset - limit) if has_prev else None
        
        links = {}
        if next_offset is not None:
            links["next"] = f"/api/v1/catalog-items?limit={limit}&offset={next_offset}"
        if prev_offset is not None:
            links["prev"] = f"/api/v1/catalog-items?limit={limit}&offset={prev_offset}"
        
        return CatalogItemSimpleListResponseDTO(
            items=[
                CatalogItemSimpleDTO(
                    item_id=item.id,
                    name=item.name
                )
                for item in items
            ],
            total=total_count,
            page=current_page,
            size=limit,
            has_next=has_next,
            has_prev=has_prev,
            links=links
        )
    
    async def search_catalog_items(self, search_dto: CatalogItemSearchDTO) -> CatalogItemListResponseDTO:
        """Search catalog items by name."""
        items = await self._catalog_item_repository.search_by_name(
            search_dto.query, 
            limit=search_dto.size, 
            offset=(search_dto.page - 1) * search_dto.size
        )
        
        return CatalogItemListResponseDTO(
            items=[
                CatalogItemResponseDTO(
                    item_id=item.id,
                    name=item.name,
                    last_used=item.last_used
                )
                for item in items
            ],
            total=len(items),
            page=search_dto.page,
            size=search_dto.size
        )
