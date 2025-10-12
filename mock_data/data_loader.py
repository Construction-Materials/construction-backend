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
    UserModel, RecipeModel, CatalogItemModel, RecipeItemModel
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
        self._load_users()
        self._load_catalog_items()
        self._load_recipes()
        self._load_recipe_items()
        
        print("✅ Mock data załadowane pomyślnie!")
    
    def _load_users(self) -> None:
        """Load users from JSON."""
        users_data = self._load_json_file("users.json")
        
        for user_data in users_data:
            user = UserModel(
                user_id=UUID(user_data["id"]),
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                is_admin=user_data["is_admin"],
                created_at=datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00"))
            )
            self.db_session.add(user)
        
        self.db_session.commit()
        print(f"✅ Załadowano {len(users_data)} użytkowników")
    
    def _load_catalog_items(self) -> None:
        """Load catalog items from JSON."""
        items_data = self._load_json_file("catalog_items.json")
        
        for item_data in items_data:
            item = CatalogItemModel(
                item_id=UUID(item_data["id"]),
                name=item_data["name"],
                last_used=datetime.fromisoformat(item_data["last_used"].replace("Z", "+00:00")) if item_data["last_used"] else None
            )
            self.db_session.add(item)
        
        self.db_session.commit()
        print(f"✅ Załadowano {len(items_data)} składników")
    
    def _load_recipes(self) -> None:
        """Load recipes from JSON."""
        recipes_data = self._load_json_file("recipes.json")
        
        for recipe_data in recipes_data:
            recipe = RecipeModel(
                recipe_id=UUID(recipe_data["id"]),
                user_id=UUID(recipe_data["user_id"]),
                title=recipe_data["title"],
                external_url=recipe_data["external_url"],
                image_url=recipe_data.get("image_url"),
                preparation_steps=recipe_data["preparation_steps"],
                prep_time_minutes=recipe_data["prep_time_minutes"],
                created_at=datetime.fromisoformat(recipe_data["created_at"].replace("Z", "+00:00"))
            )
            self.db_session.add(recipe)
        
        self.db_session.commit()
        print(f"✅ Załadowano {len(recipes_data)} przepisów")
    
    def _load_recipe_items(self) -> None:
        """Load recipe items from JSON."""
        recipe_items_data = self._load_json_file("recipe_items.json")
        
        for item_data in recipe_items_data:
            quantity = item_data["quantity"]
            recipe_item = RecipeItemModel(
                recipe_item_id=UUID(item_data["id"]),
                recipe_id=UUID(item_data["recipe_id"]),
                item_id=UUID(item_data["item_id"]),
                quantity_value=Decimal(str(quantity["value"])),
                quantity_unit=quantity["unit"]
            )
            self.db_session.add(recipe_item)
        
        self.db_session.commit()
        print(f"✅ Załadowano {len(recipe_items_data)} połączeń przepis-składnik")
    
    def _load_json_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSON data from file."""
        file_path = os.path.join(self._mock_data_path, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clear_all_data(self) -> None:
        """Clear all mock data from database."""
        print("🗑️ Czyszczenie bazy danych...")
        
        # Delete in reverse order (respecting foreign keys)
        self.db_session.query(RecipeItemModel).delete()
        self.db_session.query(RecipeModel).delete()
        self.db_session.query(CatalogItemModel).delete()
        self.db_session.query(UserModel).delete()
        
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
