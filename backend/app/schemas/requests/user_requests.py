"""
User management request models.
"""
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
from typing import Optional
from ..enums import UserRole


class UserCreate(BaseModel):
    """POST /users request schema (Admin only)."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        description="User password",
        min_length=8,
        max_length=128
    )
    full_name: str = Field(
        ...,
        description="User's full name",
        min_length=1,
        max_length=255
    )
    role: UserRole = Field(..., description="User role")
    
    @validator("password")
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "new.user@company.com",
                "password": "securePassword123",
                "full_name": "Jane Smith",
                "role": "inventory_manager"
            }
        }
    )


class UserUpdate(BaseModel):
    """PUT /users/{id} request schema."""
    
    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(
        None,
        description="User's full name",
        min_length=1,
        max_length=255
    )
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="User active status")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "updated.email@company.com",
                "full_name": "Jane Updated",
                "role": "admin",
                "is_active": True
            }
        }
    )


class PasswordChange(BaseModel):
    """PUT /users/{id}/password request schema."""
    
    current_password: str = Field(
        ...,
        description="Current password",
        min_length=1
    )
    new_password: str = Field(
        ...,
        description="New password",
        min_length=8,
        max_length=128
    )
    
    @validator("new_password")
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "oldPassword123",
                "new_password": "newPassword456"
            }
        }
    )