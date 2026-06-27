from __future__ import annotations

import json

from app.core.exceptions import ExtractionError
from app.schemas.extraction_schema import FinancialExtractionSchema

BASE_PROMPT = """You are a financial extraction assistant for informal merchants in Bolivia.

You will receive one image that may contain:
- QR payment receipt
- bank transfer receipt
- notebook page with daily or monthly sales
- notebook page with expenses
- handwritten financial notes
- purchase receipt
- expense receipt
- mixed income and expense records

Extract only information that is visible in the image.

Rules:
1. Do not invent amounts.
2. Do not invent dates.
3. Do not invent names.
4. If a value is not visible, return null.
5. Use currency BOB when the image mentions Bs, Bs., bolivianos, BOB, or when the
   context is clearly Bolivia.
6. Classify as income when the evidence suggests money received by the merchant.
7. Classify as expense when the evidence suggests purchase, supplier payment, rent,
   transport, merchandise, debt payment, or money leaving the business.
8. Use unknown when the transaction type is ambiguous.
9. Include evidence_text with the visible text that justifies each transaction.
10. Return only valid structured JSON matching the provided schema.
"""


class GeminiFinancialExtractionProvider:
    """Real Gemini Flash provider using Vertex AI API key."""

    def __init__(self, api_key: str, model: str) -> None:
        from google import genai
        from google.genai import types

        self.client = genai.Client(
            vertexai=True,
            api_key=api_key,
            http_options=types.HttpOptions(api_version="v1"),
        )
        self.model = model

    async def extract_from_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        filename: str,
    ) -> FinancialExtractionSchema:
        from google.genai import types

        schema_json = json.dumps(
            FinancialExtractionSchema.model_json_schema(),
            ensure_ascii=False,
        )

        prompt = (
            f"{BASE_PROMPT}\n\n"
            "Devuelve únicamente JSON válido que cumpla este JSON Schema "
            "y todo el texto exclusivamente en español:\n"
            f"{schema_json}"
        )

        contents = [
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ]

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        )

        last_error: Exception | None = None

        for _ in range(2):
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )

                return FinancialExtractionSchema.model_validate_json(response.text or "")
 
            except Exception as exc:
                last_error = exc

        raise ExtractionError(details={"reason": str(last_error)})