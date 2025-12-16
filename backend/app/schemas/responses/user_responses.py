"""
User management response models.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from ..shared import PaginatedResponse
from ..enums import UserRole


class UserSessionResponse(BaseModel):
    """User session response model."""
    
    id: int = Field(..., description="Session ID")
    user_id: int = Field(..., description="User ID")
    login_at: datetime = Field(..., description="Login timestamp")
    logout_at: Optional[datetime] = Field(None, description="Logout timestamp")
    ip_address: str = Field(..., description="Login IP address")
    user_agent: str = Field(..., description="User agent string")
    is_active: bool = Field(..., description="Session active status")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "login_at": "2023-01-15T09:45:00Z",
                "logout_at": "2023-01-15T17:30:00Z",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "is_active": True
            }
        }
    )


class UserSessionsResponse(PaginatedResponse):
    """GET /users/{id}/sessions response schema."""
    
    data: list[UserSessionResponse] = Field(..., description="List of user sessions")


class UsersResponse(PaginatedResponse):
    """GET /users response schema."""
    
    data: list[UserResponse] = Field(..., description="List of users")


class PasswordChangeResponse(BaseModel):
    """PUT /users/{id}/password response schema."""
    
    message: str = Field(..., description="Password change message")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Password updated successfully",
                "updated_at": "2023-01-15T10:30:00Z"
            }
        }
    )