from sqlalchemy import String, ForeignKey, Numeric, Integer, DateTime, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List,TYPE_CHECKING
from decimal import Decimal
from datetime import datetime
from .base import Base

if TYPE_CHECKING:
    from .supplier import Supplier
    from .user import User
    from .product import Product

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    po_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    ordered_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expected_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    received_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="purchase_orders")
    creator: Mapped["User"] = relationship("User", back_populates="created_purchase_orders")
    items: Mapped[List["PurchaseOrderItem"]] = relationship(
        "PurchaseOrderItem", 
        back_populates="purchase_order",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'ordered', 'received', 'cancelled')", name="ck_po_status"),
    )
    
    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, po_number={self.po_number}, status={self.status})>"

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity_ordered: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_received: Mapped[int] = mapped_column(Integer, default=0)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Relationships
    purchase_order: Mapped[PurchaseOrder] = relationship(
        "PurchaseOrder", 
        back_populates="items"
    )
    product: Mapped["Product"] = relationship("Product", back_populates="purchase_order_items")
    
    def __repr__(self):
        return f"<PurchaseOrderItem(id={self.id}, po_id={self.purchase_order_id}, product_id={self.product_id})>"