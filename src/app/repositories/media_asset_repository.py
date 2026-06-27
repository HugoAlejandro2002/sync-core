from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import MediaAssetStatus
from app.models.media_asset import MediaAsset


class MediaAssetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, media_asset: MediaAsset) -> MediaAsset:
        self.session.add(media_asset)
        await self.session.flush()
        return media_asset

    async def get_by_id(self, media_asset_id: str) -> MediaAsset | None:
        return await self.session.get(MediaAsset, media_asset_id)

    async def list_by_management(self, management_id: str) -> list[MediaAsset]:
        stmt = (
            select(MediaAsset)
            .where(MediaAsset.management_id == management_id)
            .order_by(MediaAsset.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_processing_result(
        self,
        media_asset: MediaAsset,
        *,
        status: str,
        document_type: str | None,
        document_type_label: str | None,
        detected_amount: Decimal | None,
        extracted_text: str | None,
        confidence_score: Decimal | None,
        ai_raw_response: dict[str, Any] | None,
        processed_path: str | None,
    ) -> None:
        media_asset.status = status
        media_asset.document_type = document_type
        media_asset.document_type_label = document_type_label
        media_asset.detected_amount = detected_amount
        media_asset.extracted_text = extracted_text
        media_asset.confidence_score = confidence_score
        media_asset.ai_raw_response = ai_raw_response
        media_asset.processed_path = processed_path
        await self.session.flush()

    async def mark_failed(
        self,
        media_asset: MediaAsset,
        *,
        error_message: str,
        ai_raw_response: dict[str, Any] | None = None,
    ) -> None:
        media_asset.status = MediaAssetStatus.FAILED.value
        media_asset.error_message = error_message
        if ai_raw_response is not None:
            media_asset.ai_raw_response = ai_raw_response
        await self.session.flush()
