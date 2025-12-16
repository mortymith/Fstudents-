"""
Pydantic schemas for Inventory Management System API.
"""

from .enums import *
from .shared import *  
from .params.inventory_params import *
from .requests.auth_requests import *
from .requests.user_requests import *
from .requests.category_requests import *
from .requests.supplier_requests import *
from .requests.product_requests import *
from .requests.inventory_requests import *
from .requests.stock_requests import *
from .requests.purchase_order_requests import *
from .responses.auth_responses import *
from .responses.user_responses import *
from .responses.category_responses import *
from .responses.supplier_responses import *
from .responses.product_responses import *
from .responses.inventory_responses import *
from .responses.stock_responses import *
from .responses.purchase_order_responses import *
from .responses.report_responses import *

__all__ = [
    # Enums
    "UserRole",
    "StockMovementType",
    "StockReferenceType",
    "StockAdjustmentType",
    "PurchaseOrderStatus",
    "BarcodeAction",
    "BarcodeType",
    "BarcodeFormat",
    
    # Shared
    "TimestampFields",
    "Pagination",
    "PaginatedResponse",
    "ErrorDetail",
    "ErrorResponse",
    
    # Params
    "PaginationParams",
    "SortParams",
    "IncludeParams",
    "IdPathParam",
    "UserFilterParams",
    "CategoryFilterParams",
    "SupplierFilterParams",
    "ProductFilterParams",
    "PurchaseOrderFilterParams",
    "StockMovementFilterParams",
    "StockAdjustmentFilterParams",
    "ReportParams",
    
    # Requests
    "LoginRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "UserCreate",
    "UserUpdate",
    "PasswordChange",
    "CategoryCreate",
    "CategoryUpdate",
    "SupplierCreate",
    "SupplierUpdate",
    "ProductCreate",
    "ProductUpdate",
    "InventoryUpdate",
    "ProductInventoryCreate",
    "StockAdjustmentCreate",
    "StockMovementCreate",
    "StockMovementUpdate",
    "StockAdjustmentUpdate",
    "OutgoingStockCreate",
    "BarcodeScanRequest",
    "PurchaseOrderItemCreate",
    "PurchaseOrderCreate",
    "PurchaseOrderUpdate",
    "PurchaseOrderItemUpdate",
    "PurchaseOrderItemAdd",
    "PurchaseOrderReceiveRequest",
    "PurchaseOrderReceiveItem",
    
    # Responses
    "UserResponse",
    "LoginResponse",
    "LogoutResponse",
    "PasswordResetResponse",
    "PasswordResetConfirmResponse",
    "UserSessionResponse",
    "UserSessionsResponse",
    "UsersResponse",
    "PasswordChangeResponse",
    "CategoryResponse",
    "CategoriesResponse",
    "CategoryProductsResponse",
    "SupplierResponse",
    "SuppliersResponse",
    "SupplierProductsResponse",
    "SupplierPurchaseOrdersResponse",
    "ProductResponse",
    "ProductsResponse",
    "BarcodeScanResponse",
    "BarcodeGenerateResponse",
    "ProductInventoryResponse",
    "LowStockProductsResponse",
    "StockMovementResponse",
    "StockAdjustmentResponse",
    "StockMovementsResponse",
    "ProductStockMovementsResponse",
    "ProductStockAdjustmentsResponse",
    "PurchaseOrderItemResponse",
    "PurchaseOrderResponse",
    "PurchaseOrdersResponse",
    "LowStockReportResponse",
    "LowStockReportParameters",
    "StockMovementReportResponse",
    "StockMovementReportParameters",
    "MostSoldReportResponse",
    "MostSoldReportParameters",
    "MostSoldProduct",
    "DashboardOverviewResponse",
]