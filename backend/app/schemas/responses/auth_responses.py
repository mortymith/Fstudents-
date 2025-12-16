"""
Authentication response models.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from ..enums import UserRole


class UserResponse(BaseModel):
    """User response model."""
    
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User's full name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="User active status")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "admin@company.com",
                "full_name": "John Doe",
                "role": "admin",
                "is_active": True,
                "last_login_at": "2023-01-15T09:45:00Z",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-15T09:45:00Z"
            }
        }
    )


class LoginResponse(BaseModel):
    """POST /auth/login response schema."""
    
    user: UserResponse = Field(..., description="User information")
    access_token: str = Field(..., description="JWT access token")
    expires_in: int = Field(..., description="Token expiry in seconds")
    token_type: str = Field("Bearer", description="Token type")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": {
                    "id": 1,
                    "email": "admin@company.com",
                    "full_name": "John Doe",
                    "role": "admin",
                    "is_active": True,
                    "last_login_at": "2023-01-15T09:45:00Z",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-15T09:45:00Z"
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
        }
    )


class LogoutResponse(BaseModel):
    """POST /auth/logout response schema."""
    
    message: str = Field(..., description="Logout message")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Successfully logged out"
            }
        }
    )


class PasswordResetResponse(BaseModel):
    """POST /auth/password-reset response schema."""
    
    message: str = Field(..., description="Reset instructions message")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Password reset instructions sent to your email"
            }
        }
    )


class PasswordResetConfirmResponse(BaseModel):
    """POST /auth/password-reset/confirm response schema."""
    
    message: str = Field(..., description="Password reset confirmation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Password successfully reset"
            }
        }
    )