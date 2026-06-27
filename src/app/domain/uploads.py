from dataclasses import dataclass


@dataclass(frozen=True)
class UploadedFile:
    """Framework-agnostic uploaded file passed from controllers into services."""

    filename: str
    content_type: str
    content: bytes
