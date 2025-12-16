"""
Purchase order response models.
"""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from ..shared import PaginatedResponse

if TYPE_CHECKING:
    from .supplier_responses import SupplierResponse
    from .user_responses import UserResponse
    from .product_responses import ProductResponse


class PurchaseOrderItemResponse(BaseModel):
    """Purchase order item response model."""
    
    id: int = Field(..., description="Item ID")
    purchase_order_id: int = Field(..., description="Purchase order ID")
    product_id: int = Field(..., description="Product ID")
    product: Optional["ProductResponse"] = Field(None, description="Product details")
    quantity_ordered: int = Field(..., description="Quantity ordered", ge=0)
    quantity_received: int = Field(..., description="Quantity received", ge=0)
    unit_cost: Decimal = Field(..., description="Unit cost", ge=Decimal("0.00"))
    line_total: Decimal = Field(..., description="Line total", ge=Decimal("0.00"))
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "purchase_order_id": 1,
                "product_id": 1,
                "product": None,
                "quantity_ordered": 100,
                "quantity_received": 95,
                "unit_cost": 25.50,
                "line_total": 2550.00,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }
    )


class PurchaseOrderResponse(BaseModel):
    """Purchase order response model."""
    
    id: int = Field(..., description="Purchase order ID")
    po_number: str = Field(..., description="Purchase order number")
    supplier_id: int = Field(..., description="Supplier ID")
    supplier: Optional["SupplierResponse"] = Field(None, description="Supplier details")
    status: str = Field(..., description="Purchase order status")
    total_amount: Decimal = Field(..., description="Total amount", ge=Decimal("0.00"))
    ordered_date: Optional[datetime] = Field(None, description="Order date")
    expected_delivery_date: Optional[datetime] = Field(None, description="Expected delivery date")
    received_date: Optional[datetime] = Field(None, description="Received date")
    created_by: int = Field(..., description="User ID who created the PO")
    user: Optional["UserResponse"] = Field(None, description="User details")
    items: List[PurchaseOrderItemResponse] = Field(..., description="Purchase order items")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "po_number": "PO-2023-001",
                "supplier_id": 1,
                "supplier": None,
                "status": "ordered",
                "total_amount": 2500.75,
                "ordered_date": "2023-01-10T09:00:00Z",
                "expected_delivery_date": "2023-01-25T00:00:00Z",
                "received_date": "2023-01-24T14:30:00Z",
                "created_by": 1,
                "user": None,
                "items": [],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }
    )


class PurchaseOrdersResponse(PaginatedResponse):
    """GET /purchase-orders response schema."""
    
    data: list[PurchaseOrderResponse] = Field(..., description="List of purchase orders")