from typing import Protocol

from app.schemas.extraction_schema import FinancialExtractionSchema


class FinancialExtractionProvider(Protocol):
    async def extract_from_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        filename: str,
    ) -> FinancialExtractionSchema:
        """Extract structured financial data from a single evidence image."""
        ...
