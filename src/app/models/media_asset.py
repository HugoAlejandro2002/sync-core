from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import MediaAssetStatus
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
    from app.models.transaction import Transaction


class MediaAsset(TimestampMixin, Base):
    __tablename__ = "media_assets"

    id: Mapped[str] = mapped_column(UUID_TYPE, primary_key=True, default=new_uuid)
    management_id: Mapped[str] = mapped_column(
        UUID_TYPE, ForeignKey("managements.id"), nullable=False
    )
    customer_id: Mapped[str] = mapped_column(UUID_TYPE, ForeignKey("customers.id"), nullable=False)

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(80), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    original_path: Mapped[str] = mapped_column(Text, nullable=False)
    processed_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    document_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    document_type_label: Mapped[str | None] = mapped_column(String(120), nullable=True)

    status: Mapped[str] = mapped_column(
        String(40), nullable=False, default=MediaAssetStatus.UPLOADED.value
    )

    detected_amount: Mapped[Decimal | None] = mapped_column(MONEY_TYPE, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Decimal | None] = mapped_column(CONFIDENCE_TYPE, nullable=True)

    ai_raw_response: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    management: Mapped[Management] = relationship(back_populates="media_assets")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="media_asset")

    __table_args__ = (
        Index("idx_media_assets_management_id", "management_id"),
        Index("idx_media_assets_customer_id", "customer_id"),
        Index("idx_media_assets_status", "status"),
    )
