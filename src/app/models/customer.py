from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUID_TYPE, Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.management import Management


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(UUID_TYPE, primary_key=True, default=new_uuid)

    full_name: Mapped[str] = mapped_column(String(180), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    nit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    business_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    business_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    business_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    market_location: Mapped[str | None] = mapped_column(String(180), nullable=True)

    managements: Mapped[list[Management]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_customers_full_name", "full_name"),
        Index("idx_customers_phone_number", "phone_number"),
    )
