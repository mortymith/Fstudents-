"""
Shared Pydantic models used across multiple schemas.
"""
from __future__ import annotations
from datetime import datetime, date
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class TimestampFields(BaseModel):
    """Common timestamp fields."""
    
    created_at: datetime = Field(
        ..., description="Creation timestamp"
    )
    updated_at: datetime = Field(
        ..., description="Last update timestamp"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }
    )


class Pagination(BaseModel):
    """Pagination metadata."""
    
    total: int = Field(..., description="Total number of items", ge=0)
    limit: int = Field(..., description="Items per page", ge=1, le=100)
    offset: int = Field(..., description="Items skipped", ge=0)
    has_more: bool = Field(..., description="Whether more items exist")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "total": 150,
                "limit": 20,
                "offset": 0,
                "has_more": True
            }
        }
    )


class PaginatedResponse(BaseModel):
    """Base paginated response."""
    
    data: list[Any] = Field(..., description="List of items")
    pagination: Pagination = Field(..., description="Pagination metadata")


class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    field: str = Field(..., description="Field causing error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "field": "email",
                "message": "Email is required",
                "code": "required"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[list[ErrorDetail]] = Field(None, description="Detailed errors")
    trace_id: Optional[str] = Field(None, description="Request trace ID")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "One or more validation errors occurred",
                "details": [
                    {
                        "field": "email",
                        "message": "Email is required",
                        "code": "required"
                    }
                ],
                "trace_id": "req_123456789"
            }
        }
    )