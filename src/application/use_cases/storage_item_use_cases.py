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
        """Create a new storage item or update existing one by adding quantity.
        
        If storage item with given construction_id and material_id already exists,
        adds the new quantity_value to the existing one.
        """
        # Create domain entity
        storage_item = StorageItem(
            construction_id=storage_item_dto.construction_id,
            material_id=storage_item_dto.material_id,
            quantity_value=storage_item_dto.quantity_value
        )
        
        # Upsert to repository (create or update by adding quantity)
        upserted_storage_item = await self._storage_item_repository.upsert(storage_item)
        
        return StorageItemResponseDTO(
            construction_id=upserted_storage_item.construction_id,
            material_id=upserted_storage_item.material_id,
            quantity_value=upserted_storage_item.quantity_value,
            created_at=upserted_storage_item.created_at
        )
    
    async def get_storage_item_by_ids(
        self, 
        construction_id: UUID, 
        material_id: UUID
    ) -> StorageItemResponseDTO:
        """Get storage item by construction ID and material ID."""
        storage_item = await self._storage_item_repository.get_by_ids(construction_id, material_id)
        if not storage_item:
            raise EntityNotFoundError(
                "StorageItem", 
                f"construction_id={construction_id}, material_id={material_id}"
            )
        
        return StorageItemResponseDTO(
            construction_id=storage_item.construction_id,
            material_id=storage_item.material_id,
            quantity_value=storage_item.quantity_value,
            created_at=storage_item.created_at
        )
    
    async def update_storage_item(
        self, 
        construction_id: UUID, 
        material_id: UUID, 
        storage_item_dto: StorageItemUpdateDTO
    ) -> StorageItemResponseDTO:
        """Update storage item."""
        storage_item = await self._storage_item_repository.get_by_ids(construction_id, material_id)
        if not storage_item:
            raise EntityNotFoundError(
                "StorageItem", 
                f"construction_id={construction_id}, material_id={material_id}"
            )
        
        # Update fields if provided
        if storage_item_dto.quantity_value is not None:
            storage_item.set_quantity_value(storage_item_dto.quantity_value)
        
        # Save changes
        updated_storage_item = await self._storage_item_repository.update(storage_item)
        
        return StorageItemResponseDTO(
            construction_id=updated_storage_item.construction_id,
            material_id=updated_storage_item.material_id,
            quantity_value=updated_storage_item.quantity_value,
            created_at=updated_storage_item.created_at
        )
    
    async def delete_storage_item(self, construction_id: UUID, material_id: UUID) -> bool:
        """Delete storage item."""
        storage_item = await self._storage_item_repository.get_by_ids(construction_id, material_id)
        if not storage_item:
            raise EntityNotFoundError(
                "StorageItem", 
                f"construction_id={construction_id}, material_id={material_id}"
            )
        
        return await self._storage_item_repository.delete(construction_id, material_id)
    
    async def get_storage_items_by_construction_id(
        self, 
        construction_id: UUID, 
        limit: int = 100, 
        offset: int = 0
    ) -> StorageItemListResponseDTO:
        """Get storage items by construction ID."""
        storage_items = await self._storage_item_repository.get_by_construction_id(
            construction_id=construction_id,
            limit=limit,
            offset=offset
        )
        
        return StorageItemListResponseDTO(
            storage_items=[
                StorageItemResponseDTO(
                    construction_id=storage_item.construction_id,
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
                    construction_id=storage_item.construction_id,
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
    
    async def get_materials_by_construction_id(
        self, 
        construction_id: UUID
    ) -> StorageItemMaterialListResponseDTO:
        """Get materials with details by construction ID."""
        materials_data = await self._storage_item_repository.get_materials_by_construction_id(construction_id)
        
        return StorageItemMaterialListResponseDTO(
            materials=[
                StorageItemMaterialDTO(
                    construction_id=material['construction_id'],
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
    
    async def create_storage_items_bulk_for_construction(
        self, 
        construction_id: UUID, 
        storage_item_dtos: List[StorageItemCreateDTO]
    ) -> List[StorageItemResponseDTO]:
        """Create or update multiple storage items at once for a given construction.
        
        Validates that all construction_ids in the request match the given construction_id.
        If storage item with given construction_id and material_id already exists,
        adds the new quantity_value to the existing one.
        """
        if not storage_item_dtos:
            raise ValidationError("At least one storage item is required")
        
        # Validate that all construction_ids match
        for dto in storage_item_dtos:
            if dto.construction_id != construction_id:
                raise ValidationError(
                    f"Storage item construction_id {dto.construction_id} does not match {construction_id}"
                )
        
        # Create domain entities
        storage_items = [
            StorageItem(
                construction_id=storage_item_dto.construction_id,
                material_id=storage_item_dto.material_id,
                quantity_value=storage_item_dto.quantity_value
            )
            for storage_item_dto in storage_item_dtos
        ]
        
        # Upsert to repository (create or update by adding quantity)
        upserted_storage_items = await self._storage_item_repository.upsert_bulk(storage_items)
        
        return [
            StorageItemResponseDTO(
                construction_id=storage_item.construction_id,
                material_id=storage_item.material_id,
                quantity_value=storage_item.quantity_value,
                created_at=storage_item.created_at
            )
            for storage_item in upserted_storage_items
        ]

