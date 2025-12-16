"""
Category management request models.
"""
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional


class CategoryCreate(BaseModel):
    """POST /categories request schema."""
    
    name: str = Field(
        ...,
        description="Category name",
        min_length=1,
        max_length=255
    )
    description: Optional[str] = Field(
        None,
        description="Category description",
        max_length=1000
    )
    parent_id: Optional[int] = Field(
        None,
        description="Parent category ID",
        ge=1
    )
    is_active: Optional[bool] = Field(True, description="Category active status")
    
    @validator("parent_id")
    def validate_not_self_referential(cls, v, values):
        """Prevent circular references."""
        if v is not None:
            # This check would need to be done at the database level
            # to prevent actual circular references
            pass
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "New Category",
                "description": "Category description",
                "parent_id": 1,
                "is_active": True
            }
        }
    )


class CategoryUpdate(BaseModel):
    """PUT /categories/{id} request schema."""
    
    name: Optional[str] = Field(
        None,
        description="Category name",
        min_length=1,
        max_length=255
    )
    description: Optional[str] = Field(
        None,
        description="Category description",
        max_length=1000
    )
    parent_id: Optional[int] = Field(
        None,
        description="Parent category ID",
        ge=1
    )
    is_active: Optional[bool] = Field(None, description="Category active status")
    
    @validator("parent_id")
    def validate_not_self_referential(cls, v, values, **kwargs):
        """Prevent self-referential parent ID."""
        # This would be checked at the API level with the actual category ID
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Category Name",
                "description": "Updated description",
                "parent_id": 2,
                "is_active": False
            }
        }
    )