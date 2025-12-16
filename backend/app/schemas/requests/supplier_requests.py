"""
Supplier management request models.
"""
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
from typing import Optional


class SupplierCreate(BaseModel):
    """POST /suppliers request schema."""
    
    name: str = Field(
        ...,
        description="Supplier name",
        min_length=1,
        max_length=255
    )
    contact_person_name: Optional[str] = Field(
        None,
        description="Contact person name",
        max_length=255
    )
    contact_email: Optional[EmailStr] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(
        None,
        description="Contact phone number",
        max_length=50
    )
    address_line1: Optional[str] = Field(
        None,
        description="Address line 1",
        max_length=255
    )
    address_line2: Optional[str] = Field(
        None,
        description="Address line 2",
        max_length=255
    )
    city: Optional[str] = Field(None, description="City", max_length=100)
    state: Optional[str] = Field(None, description="State/Province", max_length=100)
    postal_code: Optional[str] = Field(
        None,
        description="Postal/ZIP code",
        max_length=20
    )
    country: Optional[str] = Field(None, description="Country", max_length=100)
    is_active: Optional[bool] = Field(True, description="Supplier active status")
    
    @validator("contact_phone")
    def validate_phone_format(cls, v):
        """Basic phone number validation."""
        if v is None:
            return v
        # Remove all non-digit characters for validation
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 7:
            raise ValueError("Phone number appears to be invalid")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "New Supplier LLC",
                "contact_person_name": "Jane Contact",
                "contact_email": "jane@newsupplier.com",
                "contact_phone": "+1-555-0124",
                "address_line1": "456 Commerce St",
                "address_line2": "Building B",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "United States",
                "is_active": True
            }
        }
    )


class SupplierUpdate(BaseModel):
    """PUT /suppliers/{id} request schema."""
    
    name: Optional[str] = Field(
        None,
        description="Supplier name",
        min_length=1,
        max_length=255
    )
    contact_person_name: Optional[str] = Field(
        None,
        description="Contact person name",
        max_length=255
    )
    contact_email: Optional[EmailStr] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(
        None,
        description="Contact phone number",
        max_length=50
    )
    address_line1: Optional[str] = Field(
        None,
        description="Address line 1",
        max_length=255
    )
    address_line2: Optional[str] = Field(
        None,
        description="Address line 2",
        max_length=255
    )
    city: Optional[str] = Field(None, description="City", max_length=100)
    state: Optional[str] = Field(None, description="State/Province", max_length=100)
    postal_code: Optional[str] = Field(
        None,
        description="Postal/ZIP code",
        max_length=20
    )
    country: Optional[str] = Field(None, description="Country", max_length=100)
    is_active: Optional[bool] = Field(None, description="Supplier active status")
    
    @validator("contact_phone")
    def validate_phone_format(cls, v):
        """Basic phone number validation."""
        if v is None:
            return v
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 7:
            raise ValueError("Phone number appears to be invalid")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Supplier Name",
                "contact_person_name": "Updated Contact",
                "contact_email": "updated@supplier.com",
                "contact_phone": "+1-555-0125",
                "address_line1": "789 Updated Ave",
                "address_line2": "Suite 200",
                "city": "Los Angeles",
                "state": "CA",
                "postal_code": "90001",
                "country": "United States",
                "is_active": False
            }
        }
    )