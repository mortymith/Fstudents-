"""
Query and path parameters for Inventory Management System API.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    
    limit: int = Field(20, ge=1, le=100, description="Number of items per page")
    offset: int = Field(0, ge=0, description="Number of items to skip")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {"limit": 20, "offset": 0}
        }
    )


class SortParams(BaseModel):
    """Sorting query parameters."""
    
    sort: Optional[str] = Field(
        None,
        description="Comma-separated list of fields to sort by. Prefix with '-' for descending."
    )
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {"sort": "name,-created_at"}
        }
    )


class IncludeParams(BaseModel):
    """Include related resources query parameters."""
    
    include: Optional[str] = Field(
        None,
        description="Comma-separated list of related resources to include"
    )
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {"include": "supplier,category,inventory"}
        }
    )


class IdPathParam(BaseModel):
    """ID path parameter."""
    
    id: int = Field(..., ge=1, description="Unique resource identifier")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {"id": 123}
        }
    )


class UserFilterParams(BaseModel):
    """User filtering parameters."""
    
    role: Optional[str] = Field(None, description="Filter by user role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    search: Optional[str] = Field(None, description="Search in email and full_name")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "role": "admin",
                "is_active": True,
                "search": "john"
            }
        }
    )


class CategoryFilterParams(BaseModel):
    """Category filtering parameters."""
    
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    parent_id: Optional[int] = Field(None, description="Filter by parent category ID")
    search: Optional[str] = Field(None, description="Search in category name and description")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "is_active": True,
                "parent_id": 1,
                "search": "electronics"
            }
        }
    )


class SupplierFilterParams(BaseModel):
    """Supplier filtering parameters."""
    
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    country: Optional[str] = Field(None, description="Filter by country")
    search: Optional[str] = Field(None, description="Search in supplier name and contact")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "is_active": True,
                "country": "United States",
                "search": "electronics"
            }
        }
    )


class ProductFilterParams(BaseModel):
    """Product filtering parameters."""
    
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    category_id: Optional[int] = Field(None, description="Filter by category ID")
    supplier_id: Optional[int] = Field(None, description="Filter by supplier ID")
    low_stock: Optional[bool] = Field(None, description="Filter for low stock items only")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    search: Optional[str] = Field(None, description="Search in name, description, and SKU")
    barcode: Optional[str] = Field(None, description="Filter by barcode data")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "is_active": True,
                "category_id": 1,
                "supplier_id": 1,
                "low_stock": True,
                "min_price": 10.0,
                "max_price": 1000.0,
                "search": "headphones",
                "barcode": "123456789012"
            }
        }
    )


class PurchaseOrderFilterParams(BaseModel):
    """Purchase order filtering parameters."""
    
    status: Optional[str] = Field(None, description="Filter by purchase order status")
    supplier_id: Optional[int] = Field(None, description="Filter by supplier ID")
    start_date: Optional[str] = Field(None, description="Filter POs created after this date")
    end_date: Optional[str] = Field(None, description="Filter POs created before this date")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "status": "ordered",
                "supplier_id": 1,
                "start_date": "2023-01-01T00:00:00Z",
                "end_date": "2023-01-31T23:59:59Z"
            }
        }
    )


class StockMovementFilterParams(BaseModel):
    """Stock movement filtering parameters."""
    
    product_id: Optional[int] = Field(None, description="Filter by product ID")
    movement_type: Optional[str] = Field(None, description="Filter by movement type")
    reference_type: Optional[str] = Field(None, description="Filter by reference type")
    start_date: Optional[str] = Field(None, description="Filter movements after this date")
    end_date: Optional[str] = Field(None, description="Filter movements before this date")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "product_id": 1,
                "movement_type": "in",
                "reference_type": "purchase_order",
                "start_date": "2023-01-01T00:00:00Z",
                "end_date": "2023-01-31T23:59:59Z"
            }
        }
    )


class StockAdjustmentFilterParams(BaseModel):
    """Stock adjustment filtering parameters."""
    
    adjustment_type: Optional[str] = Field(None, description="Filter by adjustment type")
    start_date: Optional[str] = Field(None, description="Filter adjustments after this date")
    end_date: Optional[str] = Field(None, description="Filter adjustments before this date")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "adjustment_type": "damaged",
                "start_date": "2023-01-01T00:00:00Z",
                "end_date": "2023-01-31T23:59:59Z"
            }
        }
    )


class ReportParams(BaseModel):
    """Report generation parameters."""
    
    threshold: Optional[int] = Field(10, description="Low stock threshold")
    start_date: Optional[str] = Field(None, description="Start date for report period")
    end_date: Optional[str] = Field(None, description="End date for report period")
    product_id: Optional[int] = Field(None, description="Filter by specific product")
    category_id: Optional[int] = Field(None, description="Filter by category")
    limit: Optional[int] = Field(10, le=100, description="Number of top products to return")
    include_inactive: Optional[bool] = Field(False, description="Include inactive products")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "threshold": 10,
                "start_date": "2023-01-01T00:00:00Z",
                "end_date": "2023-01-31T23:59:59Z",
                "category_id": 1,
                "limit": 10
            }
        }
    )