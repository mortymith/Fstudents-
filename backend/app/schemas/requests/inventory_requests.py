"""
Inventory management request models.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class InventoryUpdate(BaseModel):
    """PATCH /products/{id}/inventory request schema."""
    
    quantity_on_hand: int = Field(
        ...,
        description="Current quantity on hand",
        ge=0
    )
    last_counted_at: Optional[datetime] = Field(None, description="Last inventory count timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity_on_hand": 150,
                "last_counted_at": "2023-01-20T11:00:00Z"
            }
        }
    )


class ProductInventoryCreate(BaseModel):
    """POST /inventory request schema (Admin only)."""
    
    product_id: int = Field(..., description="Product ID", ge=1)
    quantity_on_hand: int = Field(
        ...,
        description="Initial quantity on hand",
        ge=0
    )
    quantity_committed: Optional[int] = Field(
        0,
        description="Initial committed quantity",
        ge=0
    )
    quantity_available: Optional[int] = Field(
        None,
        description="Initial available quantity (calculated if not provided)"
    )
    last_restocked_at: Optional[datetime] = Field(
        None,
        description="Last restock timestamp"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 999,
                "quantity_on_hand": 100,
                "quantity_committed": 0,
                "quantity_available": 100,
                "last_restocked_at": "2023-01-15T10:30:00Z"
            }
        }
    )