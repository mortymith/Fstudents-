from sqlalchemy import String, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List,TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .product import Product


class Category(Base):
    __tablename__ = "categories"
    
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category", 
        remote_side="Category.id",
        back_populates="children"
    )
    children: Mapped[List["Category"]] = relationship(
        "Category", 
        back_populates="parent"
    )
    products: Mapped[List["Product"]] = relationship(
        "Product", 
        back_populates="category"
    )
        
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"