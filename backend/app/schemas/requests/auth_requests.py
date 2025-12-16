"""
Authentication request models.
"""
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
import re 


class LoginRequest(BaseModel):
    """POST /auth/login request schema."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password", min_length=1)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@company.com",
                "password": "securePassword123"
            }
        }
    )


class PasswordResetRequest(BaseModel):
    """POST /auth/password-reset request schema."""
    
    email: EmailStr = Field(..., description="User email address")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@company.com"
            }
        }
    )


class PasswordResetConfirm(BaseModel):
    """POST /auth/password-reset/confirm request schema."""
    
    token: str = Field(..., description="Password reset token")
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
                "token": "reset_token_123456",
                "new_password": "newSecurePassword123"
            }
        }
    )