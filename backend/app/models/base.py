from sqlalchemy import DateTime, func, Integer, Identity
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

from datetime import datetime


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=True),  # This maps to GENERATED ALWAYS AS IDENTITY
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
