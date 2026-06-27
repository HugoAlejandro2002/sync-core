from app.core.config import Settings
from app.providers.ai.base import FinancialExtractionProvider
from app.providers.ai.fake_provider import FakeFinancialExtractionProvider
from app.schemas.extraction_schema import FinancialExtractionSchema

_PLACEHOLDER_KEYS = {"", "replace-me"}


def build_extraction_provider(settings: Settings) -> FinancialExtractionProvider:
    """Select the real Gemini provider when a key is configured, else the fake one."""
    api_key = (settings.GEMINI_API_KEY or "").strip()
    if api_key not in _PLACEHOLDER_KEYS:
        # Imported lazily so the SDK is only loaded when actually used.
        from app.providers.ai.gemini_provider import GeminiFinancialExtractionProvider

        return GeminiFinancialExtractionProvider(api_key=api_key, model=settings.GEMINI_MODEL)
    return FakeFinancialExtractionProvider()


class AIExtractionService:
    """Thin orchestration over a FinancialExtractionProvider."""

    def __init__(self, provider: FinancialExtractionProvider) -> None:
        self.provider = provider

    async def extract(
        self, image_bytes: bytes, mime_type: str, filename: str
    ) -> FinancialExtractionSchema:
        return await self.provider.extract_from_image(image_bytes, mime_type, filename)
