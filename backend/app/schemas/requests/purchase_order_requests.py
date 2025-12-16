"""
Purchase order management request models.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List
from decimal import Decimal


class PurchaseOrderItemCreate(BaseModel):
    """Purchase order item creation schema."""
    
    product_id: int = Field(..., description="Product ID", ge=1)
    quantity_ordered: int = Field(
        ...,
        description="Quantity ordered",
        ge=1
    )
    unit_cost: Decimal = Field(
        ...,
        description="Unit cost",
        ge=Decimal("0.00"),
        decimal_places=2
    )
    
    @validator("unit_cost", pre=True)
    def convert_to_decimal(cls, v):
        """Convert to Decimal for precise monetary values."""
        return Decimal(str(v)).quantize(Decimal("0.01"))
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "quantity_ordered": 100,
                "unit_cost": 25.50
            }
        }
    )


class PurchaseOrderCreate(BaseModel):
    """POST /purchase-orders request schema."""
    
    supplier_id: int = Field(..., description="Supplier ID", ge=1)
    status: Optional[str] = Field("draft", description="Purchase order status")
    ordered_date: Optional[datetime] = Field(None, description="Order date")
    expected_delivery_date: Optional[datetime] = Field(
        None,
        description="Expected delivery date"
    )
    items: List[PurchaseOrderItemCreate] = Field(
        ...,
        description="Purchase order items",
        min_items=1
    )
    
    @validator("status")
    def validate_status(cls, v):
        """Validate initial status."""
        if v not in ["draft", "ordered"]:
            raise ValueError("Initial status must be 'draft' or 'ordered'")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "supplier_id": 1,
                "status": "draft",
                "ordered_date": "2023-01-15T10:30:00Z",
                "expected_delivery_date": "2023-01-30T00:00:00Z",
                "items": [
                    {
                        "product_id": 1,
                        "quantity_ordered": 100,
                        "unit_cost": 25.50
                    }
                ]
            }
        }
    )


class PurchaseOrderUpdate(BaseModel):
    """PUT /purchase-orders/{id} request schema."""
    
    status: Optional[str] = Field(None, description="Purchase order status")
    ordered_date: Optional[datetime] = Field(None, description="Order date")
    expected_delivery_date: Optional[datetime] = Field(
        None,
        description="Expected delivery date"
    )
    received_date: Optional[datetime] = Field(None, description="Received date")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "received",
                "ordered_date": "2023-01-16T10:30:00Z",
                "expected_delivery_date": "2023-01-31T00:00:00Z",
                "received_date": "2023-01-30T14:30:00Z"
            }
        }
    )


class PurchaseOrderItemUpdate(BaseModel):
    """Purchase order item update schema."""
    
    quantity_received: Optional[int] = Field(
        None,
        description="Quantity received",
        ge=0
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity_received": 95
            }
        }
    )


class PurchaseOrderItemAdd(BaseModel):
    """POST /purchase-orders/{id}/items request schema."""
    
    items: List[PurchaseOrderItemCreate] = Field(
        ...,
        description="Items to add",
        min_items=1
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "product_id": 2,
                        "quantity_ordered": 50,
                        "unit_cost": 15.75
                    }
                ]
            }
        }
    )


class PurchaseOrderReceiveRequest(BaseModel):
    """POST /purchase-orders/{id}/receive request schema."""
    
    received_items: List[PurchaseOrderReceiveItem] = Field(
        ...,
        description="Received items",
        min_items=1
    )
    received_date: Optional[datetime] = Field(None, description="Received date")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "received_items": [
                    {
                        "purchase_order_item_id": 1,
                        "quantity_received": 95
                    }
                ],
                "received_date": "2023-01-20T14:30:00Z"
            }
        }
    )


class PurchaseOrderReceiveItem(BaseModel):
    """Individual item receipt schema."""
    
    purchase_order_item_id: int = Field(..., description="Purchase order item ID", ge=1)
    quantity_received: int = Field(
        ...,
        description="Quantity received",
        ge=0
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "purchase_order_item_id": 1,
                "quantity_received": 95
            }
        }
    )