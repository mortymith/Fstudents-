from sqlalchemy import String, Boolean, DateTime, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from .base import Base

if TYPE_CHECKING:
    from .stock_movement import StockMovement, StockAdjustment
    from .purchase_order import PurchaseOrder


class User(Base):

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    created_purchase_orders: Mapped[List["PurchaseOrder"]] = relationship(  # type: ignore
        "PurchaseOrder",
        back_populates="creator",
        foreign_keys="PurchaseOrder.created_by",
    )
    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement", back_populates="creator"
    )
    stock_adjustments: Mapped[List["StockAdjustment"]] = relationship(
        "StockAdjustment", back_populates="creator"
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'inventory_manager', 'viewer')", name="ck_user_role"
        ),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
