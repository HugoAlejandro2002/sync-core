from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    CONFIDENCE_TYPE,
    MONEY_TYPE,
    UUID_TYPE,
    Base,
    TimestampMixin,
    new_uuid,
)

if TYPE_CHECKING:
    from app.models.management import Management
    from app.models.media_asset import MediaAsset


class Transaction(TimestampMixin, Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(UUID_TYPE, primary_key=True, default=new_uuid)
    management_id: Mapped[str] = mapped_column(
        UUID_TYPE, ForeignKey("managements.id"), nullable=False
    )
    customer_id: Mapped[str] = mapped_column(
        UUID_TYPE, ForeignKey("customers.id"), nullable=False
    )
    media_asset_id: Mapped[str | None] = mapped_column(
        UUID_TYPE, ForeignKey("media_assets.id"), nullable=True
    )

    source_type: Mapped[str] = mapped_column(String(40), nullable=False)

    transaction_type: Mapped[str] = mapped_column(String(40), nullable=False)
    amount: Mapped[Decimal] = mapped_column(MONEY_TYPE, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="BOB")

    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_method: Mapped[str] = mapped_column(String(40), nullable=False)
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[Decimal | None] = mapped_column(CONFIDENCE_TYPE, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False)

    management: Mapped[Management] = relationship(back_populates="transactions")
    media_asset: Mapped[MediaAsset | None] = relationship(back_populates="transactions")

    __table_args__ = (
        Index("idx_transactions_management_id", "management_id"),
        Index("idx_transactions_customer_id", "customer_id"),
        Index("idx_transactions_media_asset_id", "media_asset_id"),
        Index("idx_transactions_status", "status"),
        Index("idx_transactions_type", "transaction_type"),
    )
