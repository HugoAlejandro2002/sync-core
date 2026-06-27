from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.providers.storage.local_storage_provider import LocalStorageProvider
from app.repositories.media_asset_repository import MediaAssetRepository


@dataclass
class OriginalFile:
    content: bytes
    filename: str
    mime_type: str


class MediaService:
    """Serves stored media files (e.g. the original image uploaded by the customer)."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = MediaAssetRepository(session)
        self.storage = LocalStorageProvider(get_settings().LOCAL_MEDIA_DIR)

    async def get_original_file(self, media_asset_id: str) -> OriginalFile:
        media = await self.repo.get_by_id(media_asset_id)
        if media is None:
            raise NotFoundError(message="No se encontró la evidencia.")
        try:
            content = await self.storage.read_bytes(media.original_path)
        except FileNotFoundError as exc:
            raise NotFoundError(
                message="No se encontró el archivo original de la evidencia."
            ) from exc
        return OriginalFile(
            content=content,
            filename=media.original_filename,
            mime_type=media.mime_type,
        )
