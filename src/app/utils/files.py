import re
from uuid import uuid4

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")

ALLOWED_IMAGE_MIME_TYPES: frozenset[str] = frozenset({"image/jpeg", "image/png", "image/webp"})

_MIME_EXTENSIONS: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def safe_filename(filename: str) -> str:
    """Collapse unsafe characters in a filename, keeping a readable, path-safe name."""
    name = (filename or "archivo").strip().replace(" ", "_")
    name = _SAFE_CHARS.sub("_", name)
    return name or "archivo"


def unique_filename(filename: str) -> str:
    """Prefix a safe filename with a short unique token so files never collide."""
    return f"{uuid4().hex[:12]}_{safe_filename(filename)}"


def extension_for_mime(mime_type: str) -> str:
    return _MIME_EXTENSIONS.get(mime_type, ".bin")


def is_allowed_image(mime_type: str | None) -> bool:
    return mime_type in ALLOWED_IMAGE_MIME_TYPES
