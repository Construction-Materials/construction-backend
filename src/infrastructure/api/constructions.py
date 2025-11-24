"""
Construction API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from uuid import UUID

from src.application.dtos.construction_dto import (
    ConstructionCreateDTO,
    ConstructionUpdateDTO,
    ConstructionResponseDTO,
    ConstructionListResponseDTO,
    ConstructionSearchDTO
)
from src.application.use_cases.construction_use_cases import ConstructionUseCases
from src.application.use_cases.document_analysis_use_cases import DocumentAnalysisUseCases
from src.infrastructure.api.dependencies import get_construction_use_cases, get_document_analysis_use_cases

router = APIRouter()


@router.get("/public", response_model=List[ConstructionResponseDTO])
async def list_constructions_public(
    limit: int = 100,
    offset: int = 0,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """List all constructions (public endpoint for testing)."""
    result = await construction_use_cases.list_all_constructions(limit=limit, offset=offset)
    return result.constructions


@router.post("/", response_model=ConstructionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_construction(
    construction_dto: ConstructionCreateDTO,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Create a new construction."""
    return await construction_use_cases.create_construction(construction_dto)


@router.get("/{construction_id}", response_model=ConstructionResponseDTO)
async def get_construction(
    construction_id: UUID,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Get construction by ID."""
    return await construction_use_cases.get_construction_by_id(construction_id)


@router.put("/{construction_id}", response_model=ConstructionResponseDTO)
async def update_construction(
    construction_id: UUID,
    construction_dto: ConstructionUpdateDTO,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Update construction."""
    return await construction_use_cases.update_construction(construction_id, construction_dto)


@router.delete("/{construction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_construction(
    construction_id: UUID,
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Delete construction."""
    await construction_use_cases.delete_construction(construction_id)


@router.get("/", response_model=ConstructionListResponseDTO)
async def list_constructions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """List all constructions."""
    return await construction_use_cases.list_all_constructions(limit=limit, offset=offset)


@router.get("/search", response_model=ConstructionListResponseDTO)
async def search_constructions(
    query: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: str = Query(None, description="Filter by status (active, in_progress, inactive, archived, deleted)"),
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """Search constructions by name and optionally filter by status."""
    from src.application.dtos.construction_dto import ConstructionStatus
    
    status_enum = None
    if status:
        try:
            status_enum = ConstructionStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}. Valid values: {[s.value for s in ConstructionStatus]}"
            )
    
    search_dto = ConstructionSearchDTO(query=query, page=page, size=size, status=status_enum)
    return await construction_use_cases.search_constructions(search_dto)


@router.post("/{construction_id}/analyze-document", status_code=status.HTTP_200_OK)
async def analyze_document(
    construction_id: UUID,
    file: UploadFile = File(..., description="Plik do analizy (zdjęcie lub PDF)"),
    document_analysis_use_cases: DocumentAnalysisUseCases = Depends(get_document_analysis_use_cases),
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases)
):
    """
    Analizuj dokument (zdjęcie lub PDF) używając OpenAI API.
    
    Przyjmuje plik oraz construction_id i zwraca wyciągnięte dane w formacie JSON.
    """
    # Sprawdź czy construction istnieje
    try:
        await construction_use_cases.get_construction_by_id(construction_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Construction o ID {construction_id} nie został znaleziony"
        )
    
    # Wczytaj zawartość pliku
    file_content = await file.read()
    
    # Analizuj dokument
    result = await document_analysis_use_cases.analyze_document(
        file_content=file_content,
        file_name=file.filename or "unknown",
        construction_id=construction_id
    )
    
    return result

