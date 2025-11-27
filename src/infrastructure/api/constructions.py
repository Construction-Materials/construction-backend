"""
Construction API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from uuid import UUID
from rapidfuzz import fuzz

from src.application.dtos.construction_dto import (
    ConstructionCreateDTO,
    ConstructionUpdateDTO,
    ConstructionResponseDTO,
    ConstructionListResponseDTO,
    ConstructionSearchDTO
)
from src.application.dtos.material_dto import MaterialSearchDTO
from src.application.use_cases.construction_use_cases import ConstructionUseCases
from src.application.use_cases.document_analysis_use_cases import DocumentAnalysisUseCases
from src.application.use_cases.material_use_cases import MaterialUseCases
from src.infrastructure.api.dependencies import get_construction_use_cases, get_document_analysis_use_cases, get_material_use_cases

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
    construction_use_cases: ConstructionUseCases = Depends(get_construction_use_cases),
    material_use_cases: MaterialUseCases = Depends(get_material_use_cases)
):
    """
    Analizuj dokument (zdjęcie lub PDF) używając OpenAI API.
    
    Przyjmuje plik oraz construction_id i zwraca wyciągnięte dane w formacie JSON.
    Dla każdego materiału sprawdza czy istnieje w bazie i czy jednostka się zgadza.
    Jeśli jednostka się nie zgadza, użytkownik będzie musiał ręcznie wpisać ilość.
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
    
    # Sprawdź materiały w bazie i zgodność jednostek
    if "extracted_data" in result and "materials" in result["extracted_data"]:
        materials = result["extracted_data"]["materials"]
        enriched_materials = []
        
        for material in materials:
            material_name = material.get("name", "")
            document_unit = material.get("unit", "")
            quantity = material.get("quantity", 0)
            
            # Szukaj materiału w bazie po nazwie
            try:
                # Najpierw sprawdź czy jest idealny match (dokładna nazwa)
                all_materials = await material_use_cases.list_all_materials(limit=1000, offset=0)
                matching_material = None
                
                for db_material in all_materials.materials:
                    if db_material.name.lower() == material_name.lower():
                        matching_material = db_material
                        break
                
                if matching_material:
                    # Materiał istnieje w bazie - idealny match
                    # Unit może być UnitEnum lub string
                    material_unit = matching_material.unit.value if hasattr(matching_material.unit, 'value') else str(matching_material.unit)
                    unit_matches = (material_unit == document_unit)
                    
                    enriched_material = {
                        **material,
                        "material_id": str(matching_material.material_id),
                        "material_exists": True,
                        "material_unit": material_unit,
                        "unit_matches": unit_matches,
                        "can_use_quantity": unit_matches,  # Jeśli unit się zgadza, można użyć quantity
                        "suggested_materials": []  # Brak sugestii, bo jest idealny match
                    }
                else:
                    # Materiał nie istnieje w bazie - szukaj podobnych
                    search_dto = MaterialSearchDTO(query=material_name, page=1, size=5)
                    similar_materials_result = await material_use_cases.search_materials(search_dto)
                    
                    # Przygotuj listę sugerowanych materiałów z filtrowaniem po score
                    suggested_materials = []
                    material_name_lower = material_name.lower()
                    
                    for suggested in similar_materials_result.materials[:5]:  # Top 5
                        suggested_name_lower = suggested.name.lower()
                        
                        # Oblicz score podobieństwa używając różnych metod fuzzy matching
                        ratio_score = fuzz.ratio(material_name_lower, suggested_name_lower)
                        partial_score = fuzz.partial_ratio(material_name_lower, suggested_name_lower)
                        token_sort_score = fuzz.token_sort_ratio(material_name_lower, suggested_name_lower)
                        token_set_score = fuzz.token_set_ratio(material_name_lower, suggested_name_lower)
                        
                        # Użyj najwyższego wyniku
                        max_score = max(ratio_score, partial_score, token_sort_score, token_set_score)
                        
                        # Filtruj tylko materiały z score >= 50 (0.5 = 50%)
                        if max_score >= 50:
                            suggested_unit = suggested.unit.value if hasattr(suggested.unit, 'value') else str(suggested.unit)
                            suggested_materials.append({
                                "material_id": str(suggested.material_id),
                                "name": suggested.name,
                                "unit": suggested_unit,
                                "description": suggested.description,
                                "similarity_score": max_score  # Dodaj score dla informacji
                            })
                    
                    enriched_material = {
                        **material,
                        "material_id": None,
                        "material_exists": False,
                        "material_unit": None,
                        "unit_matches": False,
                        "can_use_quantity": False,  # Nie można użyć, bo materiał nie istnieje
                        "suggested_materials": suggested_materials  # Tylko materiały z score >= 50%
                    }
                
                enriched_materials.append(enriched_material)
                
            except Exception as e:
                # W przypadku błędu, zwróć materiał bez dodatkowych informacji
                enriched_materials.append({
                    **material,
                    "material_id": None,
                    "material_exists": False,
                    "material_unit": None,
                    "unit_matches": False,
                    "can_use_quantity": False,
                    "error": f"Błąd podczas sprawdzania materiału: {str(e)}"
                })
        
        result["extracted_data"]["materials"] = enriched_materials
    
    return result

