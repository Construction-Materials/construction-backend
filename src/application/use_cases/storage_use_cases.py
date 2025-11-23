"""
Storage Use Cases for Application Layer.
"""

from typing import List
from uuid import UUID

from src.domain.entities.storage import Storage
from src.domain.repositories.storage_repository import StorageRepository
from src.application.dtos.storage_dto import (
    StorageCreateDTO,
    StorageUpdateDTO,
    StorageResponseDTO,
    StorageListResponseDTO,
    StorageSearchDTO
)
from src.shared.exceptions import EntityNotFoundError, ValidationError


class StorageUseCases:
    """Storage use cases implementation."""
    
    def __init__(self, storage_repository: StorageRepository):
        self._storage_repository = storage_repository
    
    async def create_storage(self, storage_dto: StorageCreateDTO) -> StorageResponseDTO:
        """Create a new storage."""
        # Create domain entity
        storage = Storage(
            construction_id=storage_dto.construction_id,
            name=storage_dto.name
        )
        
        # Save to repository
        created_storage = await self._storage_repository.create(storage)
        
        return StorageResponseDTO(
            storage_id=created_storage.id,
            construction_id=created_storage.construction_id,
            name=created_storage.name,
            created_at=created_storage.created_at
        )
    
    async def get_storage_by_id(self, storage_id: UUID) -> StorageResponseDTO:
        """Get storage by ID."""
        storage = await self._storage_repository.get_by_id(storage_id)
        if not storage:
            raise EntityNotFoundError("Storage", str(storage_id))
        
        return StorageResponseDTO(
            storage_id=storage.id,
            construction_id=storage.construction_id,
            name=storage.name,
            created_at=storage.created_at
        )
    
    async def update_storage(self, storage_id: UUID, storage_dto: StorageUpdateDTO) -> StorageResponseDTO:
        """Update storage."""
        storage = await self._storage_repository.get_by_id(storage_id)
        if not storage:
            raise EntityNotFoundError("Storage", str(storage_id))
        
        # Update fields if provided
        if storage_dto.name is not None:
            storage.set_name(storage_dto.name)
        
        if storage_dto.construction_id is not None:
            storage.set_construction_id(storage_dto.construction_id)
        
        # Save changes
        updated_storage = await self._storage_repository.update(storage)
        
        return StorageResponseDTO(
            storage_id=updated_storage.id,
            construction_id=updated_storage.construction_id,
            name=updated_storage.name,
            created_at=updated_storage.created_at
        )
    
    async def delete_storage(self, storage_id: UUID) -> bool:
        """Delete storage."""
        storage = await self._storage_repository.get_by_id(storage_id)
        if not storage:
            raise EntityNotFoundError("Storage", str(storage_id))
        
        return await self._storage_repository.delete(storage_id)
    
    async def list_all_storages(self, limit: int = 100, offset: int = 0) -> StorageListResponseDTO:
        """List all storages."""
        storages = await self._storage_repository.list_all(limit=limit, offset=offset)
        total = await self._storage_repository.count_all()
        
        return StorageListResponseDTO(
            storages=[
                StorageResponseDTO(
                    storage_id=storage.id,
                    construction_id=storage.construction_id,
                    name=storage.name,
                    created_at=storage.created_at
                )
                for storage in storages
            ],
            total=total,
            page=(offset // limit) + 1 if limit > 0 else 1,
            size=limit
        )
    
    async def get_storages_by_construction_id(
        self, 
        construction_id: UUID, 
        limit: int = 100, 
        offset: int = 0
    ) -> StorageListResponseDTO:
        """Get storages by construction ID."""
        storages = await self._storage_repository.get_by_construction_id(
            construction_id=construction_id,
            limit=limit,
            offset=offset
        )
        
        return StorageListResponseDTO(
            storages=[
                StorageResponseDTO(
                    storage_id=storage.id,
                    construction_id=storage.construction_id,
                    name=storage.name,
                    created_at=storage.created_at
                )
                for storage in storages
            ],
            total=len(storages),
            page=(offset // limit) + 1 if limit > 0 else 1,
            size=limit
        )
    
    async def search_storages(self, search_dto: StorageSearchDTO) -> StorageListResponseDTO:
        """Search storages by name and optionally filter by construction ID."""
        # Search by name
        storages = await self._storage_repository.search_by_name(
            name=search_dto.query,
            limit=search_dto.size,
            offset=(search_dto.page - 1) * search_dto.size
        )
        
        # Filter by construction_id if provided
        if search_dto.construction_id:
            storages = [
                s for s in storages 
                if s.construction_id == search_dto.construction_id
            ]
        
        total = len(storages)
        
        return StorageListResponseDTO(
            storages=[
                StorageResponseDTO(
                    storage_id=storage.id,
                    construction_id=storage.construction_id,
                    name=storage.name,
                    created_at=storage.created_at
                )
                for storage in storages
            ],
            total=total,
            page=search_dto.page,
            size=search_dto.size
        )

