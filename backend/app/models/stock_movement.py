from sqlalchemy import (
    String,
    ForeignKey,
    Integer,
    DateTime,
    CheckConstraint,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from .base import Base

if TYPE_CHECKING:
    from .product import Product
    from .user import User


class StockMovement(Base):
    __tablename__ = "stock_movements"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    movement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity_change: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_before: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[str] = mapped_column(String(20), nullable=False)
    reference_id: Mapped[Optional[int]] = mapped_column(Integer)
    movement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product", back_populates="stock_movements"
    )
    creator: Mapped["User"] = relationship("User", back_populates="stock_movements")

    __table_args__ = (
        CheckConstraint(
            "movement_type IN ('in', 'out', 'adjustment')", name="ck_movement_type"
        ),
        CheckConstraint(
            "reference_type IN ('purchase_order', 'sale', 'adjustment', 'transfer')",
            name="ck_reference_type",
        ),
    )

    def __repr__(self):
        return f"<StockMovement(id={self.id}, product_id={self.product_id}, type={self.movement_type})>"


class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    adjustment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity_adjusted: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    adjustment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product", back_populates="stock_adjustments"
    )
    creator: Mapped["User"] = relationship("User", back_populates="stock_adjustments")

    __table_args__ = (
        CheckConstraint(
            "adjustment_type IN ('damaged', 'expired', 'returned', 'found', 'theft', 'internal_use')",
            name="ck_adjustment_type",
        ),
    )

    def __repr__(self):
        return f"<StockAdjustment(id={self.id}, product_id={self.product_id}, type={self.adjustment_type})>"
