from sqlalchemy import ForeignKey, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from .base import Base

if TYPE_CHECKING:
    from .product import Product


class ProductInventory(Base):
    __tablename__ = "product_inventory"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), unique=True, nullable=False
    )
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_committed: Mapped[int] = mapped_column(Integer, default=0)
    quantity_available: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_restocked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    last_counted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="inventory")

    def __repr__(self):
        return f"<ProductInventory(product_id={self.product_id}, available={self.quantity_available})>"
