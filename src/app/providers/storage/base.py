from typing import Protocol


class StorageProvider(Protocol):
    async def save_bytes(
        self,
        content: bytes,
        filename: str,
        content_type: str,
        folder: str,
    ) -> str: ...

    async def read_bytes(self, path: str) -> bytes: ...
