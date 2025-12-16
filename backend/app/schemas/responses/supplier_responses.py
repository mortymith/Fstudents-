"""
Supplier management response models.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, TYPE_CHECKING
from ..shared import PaginatedResponse

if TYPE_CHECKING:
    from .product_responses import ProductResponse
    from .purchase_order_responses import PurchaseOrderResponse


class SupplierResponse(BaseModel):
    """Supplier response model."""
    
    id: int = Field(..., description="Supplier ID")
    name: str = Field(..., description="Supplier name")
    contact_person_name: Optional[str] = Field(None, description="Contact person name")
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    postal_code: Optional[str] = Field(None, description="Postal/ZIP code")
    country: Optional[str] = Field(None, description="Country")
    is_active: bool = Field(..., description="Supplier active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Global Electronics Inc.",
                "contact_person_name": "John Supplier",
                "contact_email": "john@globalelectronics.com",
                "contact_phone": "+1-555-0123",
                "address_line1": "123 Business Ave",
                "address_line2": "Suite 100",
                "city": "San Francisco",
                "state": "CA",
                "postal_code": "94105",
                "country": "United States",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }
    )


class SuppliersResponse(PaginatedResponse):
    """GET /suppliers response schema."""
    
    data: list[SupplierResponse] = Field(..., description="List of suppliers")


class SupplierProductsResponse(PaginatedResponse):
    """GET /suppliers/{id}/products response schema."""
    
    data: list["ProductResponse"] = Field(..., description="List of supplier products")


class SupplierPurchaseOrdersResponse(PaginatedResponse):
    """GET /suppliers/{id}/purchase-orders response schema."""
    
    data: list["PurchaseOrderResponse"] = Field(..., description="List of supplier purchase orders")