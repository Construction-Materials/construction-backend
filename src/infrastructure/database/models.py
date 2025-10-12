"""
SQLAlchemy models for Recipe AI Extractor.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.infrastructure.database.connection import Base


class UserModel(Base):
    """User SQLAlchemy model."""
    
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    recipes = relationship("RecipeModel", back_populates="user", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJobModel", back_populates="user", cascade="all, delete-orphan")


class RecipeModel(Base):
    """Recipe SQLAlchemy model."""
    
    __tablename__ = "recipes"
    
    recipe_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    external_url = Column(String(2048), nullable=True)
    image_url = Column(String(500), nullable=True)
    preparation_steps = Column(Text, nullable=False, default="")
    prep_time_minutes = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="recipes")
    recipe_items = relationship("RecipeItemModel", back_populates="recipe", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJobModel", back_populates="recipe")


class CatalogItemModel(Base):
    """Catalog item SQLAlchemy model."""
    
    __tablename__ = "catalog_items"
    
    item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    last_used = Column(DateTime, nullable=True)
    
    # Relationships
    recipe_items = relationship("RecipeItemModel", back_populates="catalog_item")


class RecipeItemModel(Base):
    """Recipe item SQLAlchemy model."""
    
    __tablename__ = "recipe_items"
    
    recipe_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.recipe_id"), nullable=False, index=True)
    item_id = Column(UUID(as_uuid=True), ForeignKey("catalog_items.item_id"), nullable=False)
    quantity_value = Column(DECIMAL(8, 2), nullable=False)
    quantity_unit = Column(String(50), nullable=False)
    
    # Relationships
    recipe = relationship("RecipeModel", back_populates="recipe_items")
    catalog_item = relationship("CatalogItemModel", back_populates="recipe_items")


class ProcessingJobModel(Base):
    """Processing job SQLAlchemy model."""
    
    __tablename__ = "processing_jobs"
    
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    submitted_url = Column(String(2048), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
    error_message = Column(Text, nullable=True)
    result_recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.recipe_id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="processing_jobs")
    recipe = relationship("RecipeModel", back_populates="processing_jobs")
