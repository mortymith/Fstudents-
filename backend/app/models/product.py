from sqlalchemy import (
    String,
    Boolean,
    Text,
    ForeignKey,
    Numeric,
    Integer,
    Date,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from .base import Base

if TYPE_CHECKING:
    from .supplier import Supplier
    from .product_inventory import ProductInventory
    from .category import Category
    from .stock_movement import StockMovement, StockAdjustment
    from .purchase_order import PurchaseOrderItem


class Product(Base):
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cost_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10)
    reorder_point: Mapped[int] = mapped_column(Integer, default=15)
    reorder_quantity: Mapped[int] = mapped_column(Integer, default=50)
    expiry_date: Mapped[Optional[Date]] = mapped_column(Date)
    barcode_data: Mapped[Optional[str]] = mapped_column(String(255))
    qr_code_data: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="products")
    inventory: Mapped["ProductInventory"] = relationship(
        "ProductInventory",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )
    purchase_order_items: Mapped[List["PurchaseOrderItem"]] = relationship(
        "PurchaseOrderItem", back_populates="product"
    )
    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement", back_populates="product"
    )
    stock_adjustments: Mapped[List["StockAdjustment"]] = relationship(
        "StockAdjustment", back_populates="product"
    )

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_product_price_positive"),
        CheckConstraint("cost_price >= 0", name="ck_product_cost_price_positive"),
        CheckConstraint(
            "low_stock_threshold >= 0", name="ck_low_stock_threshold_positive"
        ),
        CheckConstraint("reorder_point >= 0", name="ck_reorder_point_positive"),
        CheckConstraint("reorder_quantity >= 0", name="ck_reorder_quantity_positive"),
    )

    def __repr__(self):
        return f"<Product(id={self.id}, sku={self.sku}, name={self.name})>"
