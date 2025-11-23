"""
StorageItem Use Cases for Application Layer.
"""

from typing import List
from uuid import UUID
from decimal import Decimal

from src.domain.entities.storage_item import StorageItem
from src.domain.repositories.storage_item_repository import StorageItemRepository
from src.application.dtos.storage_item_dto import (
    StorageItemCreateDTO,
    StorageItemUpdateDTO,
    StorageItemResponseDTO,
    StorageItemListResponseDTO,
    StorageItemMaterialDTO,
    StorageItemMaterialListResponseDTO
)
from src.shared.exceptions import EntityNotFoundError, ValidationError


class StorageItemUseCases:
    """StorageItem use cases implementation."""
    
    def __init__(self, storage_item_repository: StorageItemRepository):
        self._storage_item_repository = storage_item_repository
    
    async def create_storage_item(self, storage_item_dto: StorageItemCreateDTO) -> StorageItemResponseDTO:
        """Create a new storage item."""
        # Create domain entity
        storage_item = StorageItem(
            storage_id=storage_item_dto.storage_id,
            material_id=storage_item_dto.material_id,
            quantity_value=storage_item_dto.quantity_value
        )
        
        # Save to repository
        created_storage_item = await self._storage_item_repository.create(storage_item)
        
        return StorageItemResponseDTO(
            storage_id=created_storage_item.storage_id,
            material_id=created_storage_item.material_id,
            quantity_value=created_storage_item.quantity_value,
            created_at=created_storage_item.created_at
        )
    
    async def get_storage_item_by_ids(
        self, 
        storage_id: UUID, 
        material_id: UUID
    ) -> StorageItemResponseDTO:
        """Get storage item by storage ID and material ID."""
        storage_item = await self._storage_item_repository.get_by_ids(storage_id, material_id)
        if not storage_item:
            raise EntityNotFoundError(
                "StorageItem", 
                f"storage_id={storage_id}, material_id={material_id}"
            )
        
        return StorageItemResponseDTO(
            storage_id=storage_item.storage_id,
            material_id=storage_item.material_id,
            quantity_value=storage_item.quantity_value,
            created_at=storage_item.created_at
        )
    
    async def update_storage_item(
        self, 
        storage_id: UUID, 
        material_id: UUID, 
        storage_item_dto: StorageItemUpdateDTO
    ) -> StorageItemResponseDTO:
        """Update storage item."""
        storage_item = await self._storage_item_repository.get_by_ids(storage_id, material_id)
        if not storage_item:
            raise EntityNotFoundError(
                "StorageItem", 
                f"storage_id={storage_id}, material_id={material_id}"
            )
        
        # Update fields if provided
        if storage_item_dto.quantity_value is not None:
            storage_item.set_quantity_value(storage_item_dto.quantity_value)
        
        # Save changes
        updated_storage_item = await self._storage_item_repository.update(storage_item)
        
        return StorageItemResponseDTO(
            storage_id=updated_storage_item.storage_id,
            material_id=updated_storage_item.material_id,
            quantity_value=updated_storage_item.quantity_value,
            created_at=updated_storage_item.created_at
        )
    
    async def delete_storage_item(self, storage_id: UUID, material_id: UUID) -> bool:
        """Delete storage item."""
        storage_item = await self._storage_item_repository.get_by_ids(storage_id, material_id)
        if not storage_item:
            raise EntityNotFoundError(
                "StorageItem", 
                f"storage_id={storage_id}, material_id={material_id}"
            )
        
        return await self._storage_item_repository.delete(storage_id, material_id)
    
    async def get_storage_items_by_storage_id(
        self, 
        storage_id: UUID, 
        limit: int = 100, 
        offset: int = 0
    ) -> StorageItemListResponseDTO:
        """Get storage items by storage ID."""
        storage_items = await self._storage_item_repository.get_by_storage_id(
            storage_id=storage_id,
            limit=limit,
            offset=offset
        )
        
        return StorageItemListResponseDTO(
            storage_items=[
                StorageItemResponseDTO(
                    storage_id=storage_item.storage_id,
                    material_id=storage_item.material_id,
                    quantity_value=storage_item.quantity_value,
                    created_at=storage_item.created_at
                )
                for storage_item in storage_items
            ],
            total=len(storage_items),
            page=(offset // limit) + 1 if limit > 0 else 1,
            size=limit
        )
    
    async def get_storage_items_by_material_id(
        self, 
        material_id: UUID, 
        limit: int = 100, 
        offset: int = 0
    ) -> StorageItemListResponseDTO:
        """Get storage items by material ID."""
        storage_items = await self._storage_item_repository.get_by_material_id(
            material_id=material_id,
            limit=limit,
            offset=offset
        )
        
        return StorageItemListResponseDTO(
            storage_items=[
                StorageItemResponseDTO(
                    storage_id=storage_item.storage_id,
                    material_id=storage_item.material_id,
                    quantity_value=storage_item.quantity_value,
                    created_at=storage_item.created_at
                )
                for storage_item in storage_items
            ],
            total=len(storage_items),
            page=(offset // limit) + 1 if limit > 0 else 1,
            size=limit
        )
    
    async def get_materials_by_storage_id(
        self, 
        storage_id: UUID
    ) -> StorageItemMaterialListResponseDTO:
        """Get materials with details by storage ID."""
        materials_data = await self._storage_item_repository.get_materials_by_storage_id(storage_id)
        
        return StorageItemMaterialListResponseDTO(
            materials=[
                StorageItemMaterialDTO(
                    storage_id=material['storage_id'],
                    material_id=material['material_id'],
                    name=material['name'],
                    category=material['category'],
                    description=material['description'],
                    unit=material['unit'],
                    quantity_value=material['quantity_value'],
                    created_at=material['created_at']
                )
                for material in materials_data
            ]
        )

