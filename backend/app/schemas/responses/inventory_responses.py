"""
Inventory management response models.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from ..shared import PaginatedResponse
from ..responses.product_responses import ProductResponse


class ProductInventoryResponse(BaseModel):
    """Product inventory response model."""
    
    id: int = Field(..., description="Inventory ID")
    product_id: int = Field(..., description="Product ID")
    quantity_on_hand: int = Field(..., description="Quantity on hand", ge=0)
    quantity_committed: int = Field(..., description="Committed quantity", ge=0)
    quantity_available: int = Field(..., description="Available quantity", ge=0)
    last_restocked_at: Optional[datetime] = Field(None, description="Last restock timestamp")
    last_counted_at: Optional[datetime] = Field(None, description="Last count timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "product_id": 1,
                "quantity_on_hand": 100,
                "quantity_committed": 25,
                "quantity_available": 75,
                "last_restocked_at": "2023-01-10T14:30:00Z",
                "last_counted_at": "2023-01-05T09:15:00Z",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }
    )


class LowStockProductsResponse(PaginatedResponse):
    """GET /inventory/low-stock response schema."""
    
    data: list[ProductResponse] = Field(..., description="List of low stock products")