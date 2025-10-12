"""
Pytest configuration and fixtures for Recipe AI Extractor tests.
"""

import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager

from main import app
from src.infrastructure.database.connection import Base, init_database
from src.infrastructure.database.models import UserModel, RecipeModel, CatalogItemModel, RecipeItemModel
from mock_data.data_loader import MockDataLoader


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_recipe_extractor.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    # Create test engine
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup: drop all tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Create database session for tests."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def mock_data_loaded(db_session):
    """Load mock data into test database."""
    loader = MockDataLoader(db_session)
    loader.load_all_data()
    return loader


@pytest.fixture(scope="function")
def test_client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_client_with_mock_data(test_client, mock_data_loaded):
    """Test client with mock data loaded."""
    return test_client


# Sample data fixtures for individual tests
@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        "email": "test@example.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9Kz8K2K",
        "is_admin": False
    }


@pytest.fixture
def sample_recipe():
    """Sample recipe data."""
    return {
        "title": "Test Recipe",
        "external_url": "https://example.com/recipe",
        "preparation_steps": "1. Do this\n2. Do that",
        "prep_time_minutes": 30
    }


@pytest.fixture
def sample_catalog_item():
    """Sample catalog item data."""
    return {
        "name": "Test Ingredient",
        "last_used": "2024-03-15T10:30:00Z"
    }


# Database query helpers
@pytest.fixture
def get_user_by_email(db_session):
    """Helper to get user by email."""
    def _get_user(email: str):
        return db_session.query(UserModel).filter(UserModel.email == email).first()
    return _get_user


@pytest.fixture
def get_recipe_by_title(db_session):
    """Helper to get recipe by title."""
    def _get_recipe(title: str):
        return db_session.query(RecipeModel).filter(RecipeModel.title == title).first()
    return _get_recipe


@pytest.fixture
def get_catalog_item_by_name(db_session):
    """Helper to get catalog item by name."""
    def _get_item(name: str):
        return db_session.query(CatalogItemModel).filter(CatalogItemModel.name == name).first()
    return _get_item


# Mock data verification helpers
@pytest.fixture
def verify_mock_data_loaded(db_session):
    """Verify that mock data is properly loaded."""
    def _verify():
        user_count = db_session.query(UserModel).count()
        recipe_count = db_session.query(RecipeModel).count()
        catalog_count = db_session.query(CatalogItemModel).count()
        recipe_item_count = db_session.query(RecipeItemModel).count()
        
        return {
            "users": user_count,
            "recipes": recipe_count,
            "catalog_items": catalog_count,
            "recipe_items": recipe_item_count
        }
    return _verify
