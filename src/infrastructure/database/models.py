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

class CategoryModel(Base):
    """Category SQLAlchemy model."""
    
    __tablename__ = "categories"
    
    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    materials = relationship("MaterialModel", back_populates="category", cascade="all, delete-orphan")

class ConstructionModel(Base):
    """Construction SQLAlchemy model."""
    
    __tablename__ = "constructions"
    
    construction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False, default="")
    status = Column(String(20), nullable=False, default="INACTIVE")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    storages = relationship("StorageModel", back_populates="construction", cascade="all, delete-orphan")

class MaterialModel(Base):
    """Material SQLAlchemy model."""
    
    __tablename__ = "materials"
    
    material_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.category_id"), nullable=False, index=True)

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False, default="")
    unit = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    category = relationship("CategoryModel", back_populates="materials")
    storage_items = relationship("StorageItemModel", back_populates="material")

class StorageModel(Base):
    """Storage SQLAlchemy model."""
    
    __tablename__ = "storages"
    
    storage_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    construction_id = Column(UUID(as_uuid=True), ForeignKey("constructions.construction_id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    construction = relationship("ConstructionModel", back_populates="storages")
    storage_items = relationship("StorageItemModel", back_populates="storage", cascade="all, delete-orphan")

class StorageItemModel(Base):
    """Storage item SQLAlchemy model."""
    
    __tablename__ = "storage_items"
    
    storage_id = Column(UUID(as_uuid=True), ForeignKey("storages.storage_id"), primary_key=True, nullable=False)
    material_id = Column(UUID(as_uuid=True), ForeignKey("materials.material_id"), primary_key=True, nullable=False)
    quantity_value = Column(DECIMAL(8, 2), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    storage = relationship("StorageModel", back_populates="storage_items")
    material = relationship("MaterialModel", back_populates="storage_items")
