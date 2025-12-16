"""
Report response models.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from ..responses.product_responses import ProductResponse
from ..responses.stock_responses import StockMovementResponse


class LowStockReportResponse(BaseModel):
    """GET /reports/low-stock response schema."""
    
    generated_at: datetime = Field(..., description="Report generation timestamp")
    parameters: LowStockReportParameters = Field(..., description="Report parameters")
    products: List[ProductResponse] = Field(..., description="Low stock products")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generated_at": "2023-01-15T10:30:00Z",
                "parameters": {
                    "threshold": 10,
                    "category_id": 1
                },
                "products": []
            }
        }
    )


class LowStockReportParameters(BaseModel):
    """Low stock report parameters."""
    
    threshold: int = Field(..., description="Low stock threshold")
    category_id: Optional[int] = Field(None, description="Category ID filter")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "threshold": 10,
                "category_id": 1
            }
        }
    )


class StockMovementReportResponse(BaseModel):
    """GET /reports/stock-movement response schema."""
    
    generated_at: datetime = Field(..., description="Report generation timestamp")
    parameters: StockMovementReportParameters = Field(..., description="Report parameters")
    movements: List[StockMovementResponse] = Field(..., description="Stock movements")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generated_at": "2023-01-15T10:30:00Z",
                "parameters": {
                    "start_date": "2023-01-01T00:00:00Z",
                    "end_date": "2023-01-31T23:59:59Z",
                    "product_id": 1,
                    "category_id": 1
                },
                "movements": []
            }
        }
    )


class StockMovementReportParameters(BaseModel):
    """Stock movement report parameters."""
    
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    product_id: Optional[int] = Field(None, description="Product ID filter")
    category_id: Optional[int] = Field(None, description="Category ID filter")
    movement_type: Optional[str] = Field(None, description="Movement type filter")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2023-01-01T00:00:00Z",
                "end_date": "2023-01-31T23:59:59Z",
                "product_id": 1,
                "category_id": 1,
                "movement_type": "in"
            }
        }
    )


class MostSoldReportResponse(BaseModel):
    """GET /reports/most-sold response schema."""
    
    generated_at: datetime = Field(..., description="Report generation timestamp")
    parameters: MostSoldReportParameters = Field(..., description="Report parameters")
    products: List[MostSoldProduct] = Field(..., description="Most sold products")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generated_at": "2023-01-15T10:30:00Z",
                "parameters": {
                    "start_date": "2023-01-01T00:00:00Z",
                    "end_date": "2023-01-31T23:59:59Z",
                    "limit": 10
                },
                "products": [
                    {
                        "product": {
                            "id": 1,
                            "sku": "ELEC-001",
                            "name": "Wireless Headphones",
                            "price": 199.99
                        },
                        "total_sold": 150,
                        "revenue": 29998.50
                    }
                ]
            }
        }
    )


class MostSoldReportParameters(BaseModel):
    """Most sold report parameters."""
    
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    limit: int = Field(10, description="Number of products to return", le=100)
    category_id: Optional[int] = Field(None, description="Category ID filter")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2023-01-01T00:00:00Z",
                "end_date": "2023-01-31T23:59:59Z",
                "limit": 10,
                "category_id": 1
            }
        }
    )


class MostSoldProduct(BaseModel):
    """Most sold product information."""
    
    product: ProductResponse = Field(..., description="Product information")
    total_sold: int = Field(..., description="Total quantity sold", ge=0)
    revenue: float = Field(..., description="Total revenue", ge=0.0)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product": {
                    "id": 1,
                    "sku": "ELEC-001",
                    "name": "Wireless Headphones",
                    "price": 199.99
                },
                "total_sold": 150,
                "revenue": 29998.50
            }
        }
    )


class DashboardOverviewResponse(BaseModel):
    """GET /dashboard/overview response schema."""
    
    total_products: int = Field(..., description="Total number of products", ge=0)
    total_suppliers: int = Field(..., description="Total number of suppliers", ge=0)
    low_stock_count: int = Field(..., description="Number of low stock products", ge=0)
    pending_orders: int = Field(..., description="Number of pending purchase orders", ge=0)
    recent_movements: List[StockMovementResponse] = Field(
        ...,
        description="Recent stock movements"
    )
    top_selling_products: List[ProductResponse] = Field(
        ...,
        description="Top selling products"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_products": 150,
                "total_suppliers": 25,
                "low_stock_count": 12,
                "pending_orders": 5,
                "recent_movements": [],
                "top_selling_products": []
            }
        }
    )