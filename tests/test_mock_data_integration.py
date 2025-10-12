"""
Integration tests with mock data loaded.
Tests API endpoints with real mock data from JSON files.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from src.infrastructure.database.models import UserModel, RecipeModel, CatalogItemModel, RecipeItemModel


class TestMockDataIntegration:
    """Test API endpoints with mock data."""
    
    def test_users_endpoint_with_mock_data(self, test_client_with_mock_data: TestClient):
        """Test users endpoint with mock data."""
        response = test_client_with_mock_data.get("/api/v1/users")
        
        assert response.status_code == 200
        users = response.json()
        
        # Should have 7 users from mock data
        assert len(users) == 7
        
        # Check admin user exists
        admin_user = next((u for u in users if u["is_admin"]), None)
        assert admin_user is not None
        assert admin_user["email"] == "admin@example.com"
        
        # Check all users have required fields
        for user in users:
            assert "id" in user
            assert "email" in user
            assert "is_admin" in user
            assert "created_at" in user
    
    def test_recipes_endpoint_with_mock_data(self, test_client_with_mock_data: TestClient):
        """Test recipes endpoint with mock data."""
        response = test_client_with_mock_data.get("/api/v1/recipes")
        
        assert response.status_code == 200
        recipes = response.json()
        
        # Should have 8 recipes from mock data
        assert len(recipes) == 8
        
        # Check specific recipes exist
        recipe_titles = [r["title"] for r in recipes]
        assert "Klasyczne naleśniki" in recipe_titles
        assert "Spaghetti Carbonara" in recipe_titles
        assert "Zupa pomidorowa" in recipe_titles
        
        # Check all recipes have required fields
        for recipe in recipes:
            assert "id" in recipe
            assert "user_id" in recipe
            assert "title" in recipe
            assert "preparation_steps" in recipe
            assert "prep_time_minutes" in recipe
            assert "created_at" in recipe
    
    def test_catalog_items_endpoint_with_mock_data(self, test_client_with_mock_data: TestClient):
        """Test catalog items endpoint with mock data."""
        response = test_client_with_mock_data.get("/api/v1/catalog-items")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        
        items = data["items"]
        
        # Should have 10 catalog items from mock data
        assert len(items) == 10
        
        # Check specific ingredients exist
        item_names = [i["name"] for i in items]
        assert "Mąka pszenna" in item_names
        assert "Jajka" in item_names
        assert "Mleko" in item_names
        assert "Masło" in item_names
        
        # Check all items have required fields
        for item in items:
            assert "item_id" in item
            assert "name" in item
            assert "last_used" in item
    
    def test_recipe_items_relationships(self, db_session: Session, mock_data_loaded):
        """Test that recipe items relationships are properly loaded."""
        # Get a recipe with items
        recipe = db_session.query(RecipeModel).filter(
            RecipeModel.title == "Klasyczne naleśniki"
        ).first()
        
        assert recipe is not None
        
        # Check recipe has items
        recipe_items = db_session.query(RecipeItemModel).filter(
            RecipeItemModel.recipe_id == recipe.recipe_id
        ).all()
        
        assert len(recipe_items) > 0
        
        # Check each recipe item has valid relationships
        for item in recipe_items:
            assert item.recipe_id == recipe.recipe_id
            assert item.item_id is not None
            assert item.quantity_value is not None
            assert item.quantity_unit is not None
    
    def test_user_recipe_relationships(self, db_session: Session, mock_data_loaded):
        """Test that user-recipe relationships are properly loaded."""
        # Get a user with recipes
        user = db_session.query(UserModel).filter(
            UserModel.email == "anna.kowalski@example.com"
        ).first()
        
        assert user is not None
        
        # Check user has recipes
        user_recipes = db_session.query(RecipeModel).filter(
            RecipeModel.user_id == user.user_id
        ).all()
        
        assert len(user_recipes) > 0
        
        # Check all recipes belong to this user
        for recipe in user_recipes:
            assert recipe.user_id == user.user_id
    
    def test_catalog_item_usage(self, db_session: Session, mock_data_loaded):
        """Test that catalog items are used in recipes."""
        # Get a catalog item
        flour = db_session.query(CatalogItemModel).filter(
            CatalogItemModel.name == "Mąka pszenna"
        ).first()
        
        assert flour is not None
        
        # Check flour is used in recipes
        flour_usage = db_session.query(RecipeItemModel).filter(
            RecipeItemModel.item_id == flour.item_id
        ).all()
        
        assert len(flour_usage) > 0
        
        # Check usage has valid quantities
        for usage in flour_usage:
            assert usage.quantity_value > 0
            assert usage.quantity_unit in ["g", "kg", "szt", "łyżki", "łyżeczki"]
    
    def test_mock_data_statistics(self, verify_mock_data_loaded):
        """Test that mock data statistics are correct."""
        stats = verify_mock_data_loaded()
        
        # Expected counts from mock data
        assert stats["users"] == 7
        assert stats["recipes"] == 8
        assert stats["catalog_items"] == 10
        assert stats["recipe_items"] == 33
    
    def test_recipe_with_external_url(self, test_client_with_mock_data: TestClient):
        """Test recipe with external URL."""
        response = test_client_with_mock_data.get("/api/v1/recipes")
        recipes = response.json()
        
        # Find recipe with external URL
        recipe_with_url = next(
            (r for r in recipes if r["external_url"] is not None), 
            None
        )
        
        assert recipe_with_url is not None
        assert recipe_with_url["external_url"].startswith("https://")
    
    def test_recipe_without_external_url(self, test_client_with_mock_data: TestClient):
        """Test recipe without external URL."""
        response = test_client_with_mock_data.get("/api/v1/recipes")
        recipes = response.json()
        
        # Find recipe without external URL
        recipe_without_url = next(
            (r for r in recipes if r["external_url"] is None), 
            None
        )
        
        assert recipe_without_url is not None
        assert recipe_without_url["external_url"] is None
    
    def test_quantity_units_diversity(self, db_session: Session, mock_data_loaded):
        """Test that mock data has diverse quantity units."""
        units = db_session.query(RecipeItemModel.quantity_unit).distinct().all()
        unit_names = [unit[0] for unit in units]
        
        # Should have various units
        expected_units = ["g", "ml", "szt", "łyżki", "łyżeczki", "szczypta"]
        for unit in expected_units:
            assert unit in unit_names
    
    def test_preparation_time_range(self, test_client_with_mock_data: TestClient):
        """Test that recipes have realistic preparation times."""
        response = test_client_with_mock_data.get("/api/v1/recipes")
        recipes = response.json()
        
        prep_times = [r["prep_time_minutes"] for r in recipes]
        
        # All times should be positive
        assert all(time > 0 for time in prep_times)
        
        # Should have variety in preparation times
        assert min(prep_times) >= 15  # At least 15 minutes
        assert max(prep_times) <= 150  # At most 2.5 hours
