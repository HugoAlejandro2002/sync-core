from decimal import Decimal

from app.schemas.extraction_schema import (
    ExtractedTransactionSchema,
    FinancialExtractionSchema,
)


class FakeFinancialExtractionProvider:
    """Deterministic stand-in for Gemini. Used when no GEMINI_API_KEY is configured
    and in tests, so the full evidence flow works without API spend."""

    async def extract_from_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        filename: str,
    ) -> FinancialExtractionSchema:
        seed = sum(ord(ch) for ch in filename) or 7
        amount = Decimal(1000 + (seed % 50) * 100)  # 1000..5900, stable per filename
        confidence = 0.9

        transaction = ExtractedTransactionSchema(
            transaction_type="income",
            amount=amount,
            currency="BOB",
            description="Ventas detectadas (extracción simulada)",
            transaction_date=None,
            payment_method="cash",
            evidence_text=f"Total simulado: Bs {amount}",
            confidence_score=confidence,
        )
        return FinancialExtractionSchema(
            document_type="sales_notebook",
            document_type_label="Cuaderno de ventas",
            detected_amount=amount,
            raw_text=f"Extracción simulada de «{filename}».",
            transactions=[transaction],
            confidence_score=confidence,
            warnings=[],
        )
