from __future__ import annotations

import os
from pathlib import Path

from app.core.exceptions import AppError


class LocalStorageProvider:
    def __init__(self, base_dir: str | os.PathLike[str]) -> None:
        self._base = Path(base_dir)

    async def save_bytes(
        self,
        content: bytes,
        filename: str,
        content_type: str,
        folder: str,
    ) -> str:
        dest = self._base / folder / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        return str(dest)

    async def read_bytes(self, path: str) -> bytes:
        target = Path(path)
        if not target.exists():
            raise AppError(
                status_code=404,
                code="FILE_NOT_FOUND",
                message="No se encontró el archivo.",
            )
        return target.read_bytes()
