"""
Stock movement and adjustment response models.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, TYPE_CHECKING
from ..shared import PaginatedResponse
from ..enums import StockMovementType, StockReferenceType, StockAdjustmentType

if TYPE_CHECKING:
    from .product_responses import ProductResponse
    from .user_responses import UserResponse


class StockMovementResponse(BaseModel):
    """Stock movement response model."""
    
    id: int = Field(..., description="Movement ID")
    product_id: int = Field(..., description="Product ID")
    product: Optional["ProductResponse"] = Field(None, description="Product details")
    movement_type: StockMovementType = Field(..., description="Movement type")
    quantity_change: int = Field(..., description="Quantity change")
    quantity_before: int = Field(..., description="Quantity before movement")
    quantity_after: int = Field(..., description="Quantity after movement")
    reference_type: StockReferenceType = Field(..., description="Reference type")
    reference_id: Optional[int] = Field(None, description="Reference ID")
    movement_date: datetime = Field(..., description="Movement timestamp")
    created_by: int = Field(..., description="User ID who created the movement")
    user: Optional["UserResponse"] = Field(None, description="User details")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "product_id": 1,
                "product": None,
                "movement_type": "in",
                "quantity_change": 50,
                "quantity_before": 100,
                "quantity_after": 150,
                "reference_type": "purchase_order",
                "reference_id": 1,
                "movement_date": "2023-01-15T10:30:00Z",
                "created_by": 1,
                "user": None,
                "created_at": "2023-01-15T10:30:00Z"
            }
        }
    )


class StockAdjustmentResponse(BaseModel):
    """Stock adjustment response model."""
    
    id: int = Field(..., description="Adjustment ID")
    product_id: int = Field(..., description="Product ID")
    product: Optional["ProductResponse"] = Field(None, description="Product details")
    adjustment_type: StockAdjustmentType = Field(..., description="Adjustment type")
    quantity_adjusted: int = Field(..., description="Quantity adjusted")
    reason: str = Field(..., description="Adjustment reason")
    adjustment_date: datetime = Field(..., description="Adjustment timestamp")
    created_by: int = Field(..., description="User ID who created the adjustment")
    user: Optional["UserResponse"] = Field(None, description="User details")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "product_id": 1,
                "product": None,
                "adjustment_type": "damaged",
                "quantity_adjusted": -5,
                "reason": "Items damaged during handling",
                "adjustment_date": "2023-01-15T10:30:00Z",
                "created_by": 1,
                "user": None,
                "created_at": "2023-01-15T10:30:00Z"
            }
        }
    )


class StockMovementsResponse(PaginatedResponse):
    """GET /stock-movements response schema."""
    
    data: list[StockMovementResponse] = Field(..., description="List of stock movements")


class ProductStockMovementsResponse(PaginatedResponse):
    """GET /products/{id}/stock-movements response schema."""
    
    data: list[StockMovementResponse] = Field(..., description="List of product stock movements")


class ProductStockAdjustmentsResponse(PaginatedResponse):
    """GET /products/{id}/stock-adjustments response schema."""
    
    data: list[StockAdjustmentResponse] = Field(..., description="List of product stock adjustments")