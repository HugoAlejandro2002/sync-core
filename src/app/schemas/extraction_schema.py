from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class ExtractedTransactionSchema(BaseModel):
    transaction_type: Literal["income", "expense", "unknown"]
    amount: Decimal = Field(gt=0)
    currency: str = "BOB"
    description: str | None = None
    transaction_date: str | None = None
    payment_method: Literal["qr", "cash", "transfer", "unknown"] = "unknown"
    evidence_text: str | None = None
    confidence_score: float = Field(ge=0, le=1)


class FinancialExtractionSchema(BaseModel):
    document_type: Literal[
        "sales_notebook",
        "qr_receipt",
        "purchase_receipt",
        "expense_note",
        "mixed",
        "unknown",
    ]
    document_type_label: str | None = None
    detected_amount: Decimal | None = None
    raw_text: str | None = None
    transactions: list[ExtractedTransactionSchema] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)
