"""
Product management request models.
"""
from __future__ import annotations
from datetime import date
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional
from decimal import Decimal


class ProductCreate(BaseModel):
    """POST /products request schema."""
    
    sku: str = Field(
        ...,
        description="Stock Keeping Unit",
        min_length=1,
        max_length=100
    )
    name: str = Field(
        ...,
        description="Product name",
        min_length=1,
        max_length=255
    )
    description: Optional[str] = Field(
        None,
        description="Product description",
        max_length=2000
    )
    category_id: int = Field(
        ...,
        description="Category ID",
        ge=1
    )
    supplier_id: int = Field(
        ...,
        description="Supplier ID",
        ge=1
    )
    price: Decimal = Field(
        ...,
        description="Selling price",
        ge=Decimal("0.00"),
        decimal_places=2
    )
    cost_price: Optional[Decimal] = Field(
        None,
        description="Cost price",
        ge=Decimal("0.00"),
        decimal_places=2
    )
    low_stock_threshold: Optional[int] = Field(
        None,
        description="Low stock threshold",
        ge=0
    )
    reorder_point: Optional[int] = Field(
        None,
        description="Reorder point",
        ge=0
    )
    reorder_quantity: Optional[int] = Field(
        None,
        description="Reorder quantity",
        ge=0
    )
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    barcode_data: Optional[str] = Field(
        None,
        description="Barcode data",
        max_length=100
    )
    is_active: Optional[bool] = Field(True, description="Product active status")
    
    @validator("price", "cost_price", pre=True)
    def convert_to_decimal(cls, v):
        """Convert to Decimal for precise monetary values."""
        if v is None:
            return None
        return Decimal(str(v)).quantize(Decimal("0.01"))
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sku": "NEW-SKU-001",
                "name": "New Product",
                "description": "Product description",
                "category_id": 1,
                "supplier_id": 1,
                "price": 99.99,
                "cost_price": 60.00,
                "low_stock_threshold": 5,
                "reorder_point": 10,
                "reorder_quantity": 25,
                "expiry_date": "2024-12-31",
                "barcode_data": "987654321098",
                "is_active": True
            }
        }
    )


class ProductUpdate(BaseModel):
    """PUT /products/{id} request schema."""
    
    sku: Optional[str] = Field(
        None,
        description="Stock Keeping Unit",
        min_length=1,
        max_length=100
    )
    name: Optional[str] = Field(
        None,
        description="Product name",
        min_length=1,
        max_length=255
    )
    description: Optional[str] = Field(
        None,
        description="Product description",
        max_length=2000
    )
    category_id: Optional[int] = Field(
        None,
        description="Category ID",
        ge=1
    )
    supplier_id: Optional[int] = Field(
        None,
        description="Supplier ID",
        ge=1
    )
    price: Optional[Decimal] = Field(
        None,
        description="Selling price",
        ge=Decimal("0.00"),
        decimal_places=2
    )
    cost_price: Optional[Decimal] = Field(
        None,
        description="Cost price",
        ge=Decimal("0.00"),
        decimal_places=2
    )
    low_stock_threshold: Optional[int] = Field(
        None,
        description="Low stock threshold",
        ge=0
    )
    reorder_point: Optional[int] = Field(
        None,
        description="Reorder point",
        ge=0
    )
    reorder_quantity: Optional[int] = Field(
        None,
        description="Reorder quantity",
        ge=0
    )
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    barcode_data: Optional[str] = Field(
        None,
        description="Barcode data",
        max_length=100
    )
    is_active: Optional[bool] = Field(None, description="Product active status")
    
    @validator("price", "cost_price", pre=True)
    def convert_to_decimal(cls, v):
        """Convert to Decimal for precise monetary values."""
        if v is None:
            return None
        return Decimal(str(v)).quantize(Decimal("0.01"))
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sku": "UPDATED-SKU-001",
                "name": "Updated Product Name",
                "description": "Updated description",
                "category_id": 2,
                "supplier_id": 2,
                "price": 129.99,
                "cost_price": 75.00,
                "low_stock_threshold": 8,
                "reorder_point": 12,
                "reorder_quantity": 30,
                "expiry_date": "2025-06-30",
                "barcode_data": "updated_barcode_123",
                "is_active": False
            }
        }
    )