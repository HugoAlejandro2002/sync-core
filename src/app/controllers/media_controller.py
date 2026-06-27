from urllib.parse import quote

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.media_service import MediaService

router = APIRouter(prefix="/api/v1/media", tags=["media"])


@router.get("/{media_asset_id}/original")
async def download_original(
    media_asset_id: str,
    session: AsyncSession = Depends(get_session),
) -> Response:
    file = await MediaService(session).get_original_file(media_asset_id)
    ascii_name = file.filename.encode("ascii", "ignore").decode() or "evidencia"
    disposition = (
        f'attachment; filename="{ascii_name}"; '
        f"filename*=UTF-8''{quote(file.filename)}"
    )
    return Response(
        content=file.content,
        media_type=file.mime_type,
        headers={"Content-Disposition": disposition},
    )
