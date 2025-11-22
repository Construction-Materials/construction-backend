"""
Data loader for mock data JSON files.
Converts JSON data to SQLAlchemy models and loads into database.
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.models import (
    CategoryModel,
    ConstructionModel,
    MaterialModel,
    StorageModel,
    StorageItemModel,
    ConstructionStatus,
    UnitEnum
)
from src.infrastructure.database.connection import Base
from src.shared.config import settings


class MockDataLoader:
    """Loader for mock data from JSON files."""
    
    def __init__(self, db_session: Session = None):
        """Initialize data loader."""
        self.db_session = db_session
        self._mock_data_path = os.path.join(os.path.dirname(__file__))
    
    def load_all_data(self) -> None:
        """Load all mock data into database."""
        print("🔄 Ładowanie mock data...")
        
        # Load in correct order (respecting foreign keys)
        self._load_categories()
        self._load_constructions()
        self._load_materials()
        self._load_storages()
        self._load_storage_items()
        
        print("✅ Mock data załadowane pomyślnie!")
    
    def _load_categories(self) -> None:
        """Load categories from JSON."""
        categories_data = self._load_json_file("categories.json")
        
        for category_data in categories_data:
            category = CategoryModel(
                category_id=UUID(category_data["id"]),
                name=category_data["name"]
            )
            self.db_session.add(category)
        
        self.db_session.commit()
        print(f"✅ Załadowano {len(categories_data)} kategorii")
    
    def _load_constructions(self) -> None:
        """Load constructions from JSON."""
        constructions_data = self._load_json_file("constructions.json")
        
        for construction_data in constructions_data:
            construction = ConstructionModel(
                construction_id=UUID(construction_data["id"]),
                name=construction_data["name"],
                description=construction_data["description"],
                status=ConstructionStatus(construction_data["status"]),
                created_at=datetime.fromisoformat(construction_data["created_at"].replace("Z", "+00:00"))
            )
            self.db_session.add(construction)
        
        self.db_session.commit()
        print(f"✅ Załadowano {len(constructions_data)} konstrukcji")
    
    def _load_materials(self) -> None:
        """Load materials from JSON."""
        materials_data = self._load_json_file("materials.json")
        
        for material_data in materials_data:
            material = MaterialModel(
                material_id=UUID(material_data["id"]),
                category_id=UUID(material_data["category_id"]),
                name=material_data["name"],
                description=material_data["description"],
                unit=UnitEnum(material_data["unit"]),
                created_at=datetime.fromisoformat(material_data["created_at"].replace("Z", "+00:00"))
            )
            self.db_session.add(material)
        
        self.db_session.commit()
        print(f"✅ Załadowano {len(materials_data)} materiałów")
    
    def _load_storages(self) -> None:
        """Load storages from JSON."""
        storages_data = self._load_json_file("storages.json")
        
        for storage_data in storages_data:
            storage = StorageModel(
                storage_id=UUID(storage_data["id"]),
                construction_id=UUID(storage_data["construction_id"]),
                name=storage_data["name"],
                created_at=datetime.fromisoformat(storage_data["created_at"].replace("Z", "+00:00"))
            )
            self.db_session.add(storage)
        
        self.db_session.commit()
        print(f"✅ Załadowano {len(storages_data)} magazynów")
    
    def _load_storage_items(self) -> None:
        """Load storage items from JSON."""
        storage_items_data = self._load_json_file("storage_items.json")
        
        for item_data in storage_items_data:
            storage_item = StorageItemModel(
                storage_id=UUID(item_data["storage_id"]),
                material_id=UUID(item_data["material_id"]),
                quantity_value=Decimal(str(item_data["quantity_value"]))
            )
            self.db_session.add(storage_item)
        
        self.db_session.commit()
        print(f"✅ Załadowano {len(storage_items_data)} pozycji magazynowych")
    
    def _load_json_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSON data from file."""
        file_path = os.path.join(self._mock_data_path, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clear_all_data(self) -> None:
        """Clear all mock data from database."""
        print("🗑️ Czyszczenie bazy danych...")
        
        # Delete in reverse order (respecting foreign keys)
        self.db_session.query(StorageItemModel).delete()
        self.db_session.query(StorageModel).delete()
        self.db_session.query(MaterialModel).delete()
        self.db_session.query(ConstructionModel).delete()
        self.db_session.query(CategoryModel).delete()
        
        self.db_session.commit()
        print("✅ Baza danych wyczyszczona")
    
    def reset_database(self) -> None:
        """Clear and reload all mock data."""
        self.clear_all_data()
        self.load_all_data()


def create_database_session() -> Session:
    """Create database session for data loading."""
    engine = create_engine(settings.database_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def load_mock_data() -> None:
    """Main function to load mock data into database."""
    session = create_database_session()
    try:
        loader = MockDataLoader(session)
        loader.load_all_data()
    finally:
        session.close()


def reset_mock_data() -> None:
    """Reset database with mock data."""
    session = create_database_session()
    try:
        loader = MockDataLoader(session)
        loader.reset_database()
    finally:
        session.close()


if __name__ == "__main__":
    """Run data loading when script is executed directly."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        print("🔄 Resetowanie bazy danych z mock data...")
        reset_mock_data()
    else:
        print("🔄 Ładowanie mock data...")
        load_mock_data()
