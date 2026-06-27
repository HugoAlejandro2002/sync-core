from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ManagementStatus
from app.domain.money import zero_money
from app.models.base import CONFIDENCE_TYPE, MONEY_TYPE, UUID_TYPE, Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.media_asset import MediaAsset
    from app.models.transaction import Transaction


class Management(TimestampMixin, Base):
    __tablename__ = "managements"

    id: Mapped[str] = mapped_column(UUID_TYPE, primary_key=True, default=new_uuid)
    customer_id: Mapped[str] = mapped_column(UUID_TYPE, ForeignKey("customers.id"), nullable=False)

    application_code: Mapped[str] = mapped_column(String(40), nullable=False)

    requested_amount: Mapped[Decimal] = mapped_column(MONEY_TYPE, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="BOB")

    status: Mapped[str] = mapped_column(
        String(40), nullable=False, default=ManagementStatus.PENDING.value
    )

    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    visit_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    advisor_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    total_income: Mapped[Decimal] = mapped_column(MONEY_TYPE, nullable=False, default=zero_money)
    total_expense: Mapped[Decimal] = mapped_column(MONEY_TYPE, nullable=False, default=zero_money)
    net_balance: Mapped[Decimal] = mapped_column(MONEY_TYPE, nullable=False, default=zero_money)
    confidence_score: Mapped[Decimal | None] = mapped_column(CONFIDENCE_TYPE, nullable=True)

    analysis_summary: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    alerts: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="managements")
    media_assets: Mapped[list[MediaAsset]] = relationship(
        back_populates="management", cascade="all, delete-orphan"
    )
    transactions: Mapped[list[Transaction]] = relationship(
        back_populates="management", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_managements_customer_id", "customer_id"),
        Index("idx_managements_status", "status"),
        Index("idx_managements_submitted_at", "submitted_at"),
        Index("idx_managements_application_code", "application_code"),
    )
