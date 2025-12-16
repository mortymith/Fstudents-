"""
Product management response models.
"""
from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, TYPE_CHECKING
from ..shared import PaginatedResponse

if TYPE_CHECKING:
    from .category_responses import CategoryResponse
    from .supplier_responses import SupplierResponse
    from .inventory_responses import ProductInventoryResponse


class ProductResponse(BaseModel):
    """Product response model."""
    
    id: int = Field(..., description="Product ID")
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category_id: int = Field(..., description="Category ID")
    category: Optional["CategoryResponse"] = Field(None, description="Category details")
    supplier_id: int = Field(..., description="Supplier ID")
    supplier: Optional["SupplierResponse"] = Field(None, description="Supplier details")
    price: Decimal = Field(..., description="Selling price", ge=Decimal("0.00"))
    cost_price: Optional[Decimal] = Field(None, description="Cost price", ge=Decimal("0.00"))
    low_stock_threshold: Optional[int] = Field(None, description="Low stock threshold", ge=0)
    reorder_point: Optional[int] = Field(None, description="Reorder point", ge=0)
    reorder_quantity: Optional[int] = Field(None, description="Reorder quantity", ge=0)
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    barcode_data: Optional[str] = Field(None, description="Barcode data")
    qr_code_data: Optional[str] = Field(None, description="QR code data")
    is_active: bool = Field(..., description="Product active status")
    inventory: Optional["ProductInventoryResponse"] = Field(
        None,
        description="Inventory information"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "sku": "ELEC-001",
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "category_id": 1,
                "category": None,
                "supplier_id": 1,
                "supplier": None,
                "price": 199.99,
                "cost_price": 120.50,
                "low_stock_threshold": 10,
                "reorder_point": 15,
                "reorder_quantity": 50,
                "expiry_date": "2024-12-31",
                "barcode_data": "123456789012",
                "qr_code_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
                "is_active": True,
                "inventory": None,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }
    )


class ProductsResponse(PaginatedResponse):
    """GET /products response schema."""
    
    data: list[ProductResponse] = Field(..., description="List of products")


class BarcodeScanResponse(BaseModel):
    """POST /barcode/scan response schema."""
    
    product: ProductResponse = Field(..., description="Product information")
    action: str = Field(..., description="Action performed")
    requires_quantity: bool = Field(..., description="Whether quantity input is required")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product": {
                    "id": 1,
                    "sku": "ELEC-001",
                    "name": "Wireless Headphones",
                    "description": "High-quality wireless headphones with noise cancellation",
                    "category_id": 1,
                    "category": None,
                    "supplier_id": 1,
                    "supplier": None,
                    "price": 199.99,
                    "cost_price": 120.50,
                    "low_stock_threshold": 10,
                    "reorder_point": 15,
                    "reorder_quantity": 50,
                    "expiry_date": "2024-12-31",
                    "barcode_data": "123456789012",
                    "qr_code_data": None,
                    "is_active": True,
                    "inventory": None,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-15T10:30:00Z"
                },
                "action": "view",
                "requires_quantity": False
            }
        }
    )


class BarcodeGenerateResponse(BaseModel):
    """GET /products/{id}/barcode response schema."""
    
    code_data: str = Field(..., description="Barcode/QR code data")
    code_type: str = Field(..., description="Type of code generated")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
                "code_type": "barcode"
            }
        }
    )