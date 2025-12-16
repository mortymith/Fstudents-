"""
Enums for Inventory Management System API.
"""
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    
    ADMIN = "admin"
    INVENTORY_MANAGER = "inventory_manager"
    VIEWER = "viewer"


class StockMovementType(str, Enum):
    """Stock movement type enumeration."""
    
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"


class StockReferenceType(str, Enum):
    """Stock reference type enumeration."""
    
    PURCHASE_ORDER = "purchase_order"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"


class StockAdjustmentType(str, Enum):
    """Stock adjustment type enumeration."""
    
    DAMAGED = "damaged"
    EXPIRED = "expired"
    RETURNED = "returned"
    FOUND = "found"
    THEFT = "theft"
    INTERNAL_USE = "internal_use"


class PurchaseOrderStatus(str, Enum):
    """Purchase order status enumeration."""
    
    DRAFT = "draft"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class BarcodeAction(str, Enum):
    """Barcode scan action enumeration."""
    
    VIEW = "view"
    UPDATE = "update"


class BarcodeType(str, Enum):
    """Barcode/QR code type enumeration."""
    
    BARCODE = "barcode"
    QRCODE = "qrcode"


class BarcodeFormat(str, Enum):
    """Barcode output format enumeration."""
    
    SVG = "svg"
    PNG = "png"
    BASE64 = "base64"