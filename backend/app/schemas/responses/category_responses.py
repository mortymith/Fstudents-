"""
Category management response models.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, TYPE_CHECKING
from ..shared import PaginatedResponse

if TYPE_CHECKING:
    from .product_responses import ProductResponse


class CategoryResponse(BaseModel):
    """Category response model."""
    
    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    parent_category: Optional["CategoryResponse"] = Field(
        None,
        description="Parent category details"
    )
    is_active: bool = Field(..., description="Category active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Electronics",
                "description": "Electronic devices and components",
                "parent_id": None,
                "parent_category": None,
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }
    )


class CategoriesResponse(PaginatedResponse):
    """GET /categories response schema."""
    
    data: list[CategoryResponse] = Field(..., description="List of categories")


class CategoryProductsResponse(PaginatedResponse):
    """GET /categories/{id}/products response schema."""
    
    data: list["ProductResponse"] = Field(..., description="List of products in category")