"""
Stock movement and adjustment request models.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from ..enums import StockMovementType, StockReferenceType, StockAdjustmentType


class StockAdjustmentCreate(BaseModel):
    """POST /inventory/stock-adjustments request schema."""
    
    product_id: int = Field(..., description="Product ID", ge=1)
    adjustment_type: StockAdjustmentType = Field(..., description="Adjustment type")
    quantity_adjusted: int = Field(
        ...,
        description="Quantity adjusted (negative for reductions)",
        ge=-1000000,
        le=1000000
    )
    reason: str = Field(
        ...,
        description="Adjustment reason",
        min_length=1,
        max_length=1000
    )
    adjustment_date: datetime = Field(
        ...,
        description="Adjustment date and time"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "adjustment_type": "damaged",
                "quantity_adjusted": -5,
                "reason": "Items damaged during handling",
                "adjustment_date": "2023-01-15T10:30:00Z"
            }
        }
    )


class StockMovementCreate(BaseModel):
    """POST /stock-movements request schema (Admin only)."""
    
    product_id: int = Field(..., description="Product ID", ge=1)
    movement_type: StockMovementType = Field(..., description="Movement type")
    quantity_change: int = Field(
        ...,
        description="Quantity change (positive for incoming, negative for outgoing)",
        ge=-1000000,
        le=1000000
    )
    quantity_before: Optional[int] = Field(
        None,
        description="Quantity before movement (calculated if not provided)",
        ge=0
    )
    quantity_after: Optional[int] = Field(
        None,
        description="Quantity after movement (calculated if not provided)",
        ge=0
    )
    reference_type: StockReferenceType = Field(..., description="Reference type")
    reference_id: Optional[int] = Field(
        None,
        description="Reference ID (e.g., purchase order ID)",
        ge=1
    )
    movement_date: datetime = Field(..., description="Movement date and time")
    notes: Optional[str] = Field(
        None,
        description="Additional notes",
        max_length=2000
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "movement_type": "in",
                "quantity_change": 50,
                "quantity_before": 100,
                "quantity_after": 150,
                "reference_type": "purchase_order",
                "reference_id": 1,
                "movement_date": "2023-01-15T10:30:00Z",
                "notes": "Manual adjustment by admin"
            }
        }
    )


class StockMovementUpdate(BaseModel):
    """PUT /stock-movements/{id} request schema (Admin only)."""
    
    quantity_change: Optional[int] = Field(
        None,
        description="Quantity change",
        ge=-1000000,
        le=1000000
    )
    movement_date: Optional[datetime] = Field(
        None,
        description="Movement date and time"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes",
        max_length=2000
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity_change": 40,
                "movement_date": "2023-01-16T10:30:00Z",
                "notes": "Updated quantity"
            }
        }
    )


class StockAdjustmentUpdate(BaseModel):
    """PUT /stock-adjustments/{id} request schema."""
    
    quantity_adjusted: Optional[int] = Field(
        None,
        description="Quantity adjusted",
        ge=-1000000,
        le=1000000
    )
    adjustment_date: Optional[datetime] = Field(
        None,
        description="Adjustment date and time"
    )
    reason: Optional[str] = Field(
        None,
        description="Adjustment reason",
        min_length=1,
        max_length=1000
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity_adjusted": -3,
                "adjustment_date": "2023-01-16T10:30:00Z",
                "reason": "Updated damage count"
            }
        }
    )


class OutgoingStockCreate(BaseModel):
    """POST /inventory/outgoing-stock request schema."""
    
    product_id: int = Field(..., description="Product ID", ge=1)
    quantity: int = Field(
        ...,
        description="Quantity to deduct",
        ge=1
    )
    reason: str = Field(
        ...,
        description="Reason for outgoing stock",
        min_length=1,
        max_length=255
    )
    reference_id: Optional[int] = Field(
        None,
        description="Reference ID (e.g., sale ID)",
        ge=1
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes",
        max_length=2000
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "quantity": 5,
                "reason": "Sale",
                "reference_id": 1001,
                "notes": "Customer order #1001"
            }
        }
    )


class BarcodeScanRequest(BaseModel):
    """POST /barcode/scan request schema."""
    
    barcode_data: str = Field(
        ...,
        description="Barcode or QR code data",
        min_length=1,
        max_length=100
    )
    action: str = Field("view", description="Action to perform")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "barcode_data": "123456789012",
                "action": "view"
            }
        }
    )