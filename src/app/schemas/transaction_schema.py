from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import FinancialSummaryShort


class TransactionResponse(BaseModel):
    id: str
    management_id: str
    media_asset_id: str | None = None
    source_type: str
    source_type_label: str
    transaction_type: str
    transaction_type_label: str
    amount: str
    currency: str
    description: str | None = None
    transaction_date: str | None = None
    payment_method: str
    payment_method_label: str
    evidence_text: str | None = None
    confidence_score: float | None = None
    status: str
    status_label: str


class ManualTransactionCreate(BaseModel):
    transaction_type: Literal["income", "expense", "unknown"] = "income"
    amount: Decimal = Field(gt=0)
    currency: str = "BOB"
    description: str | None = None
    transaction_date: date | None = None
    payment_method: Literal["qr", "cash", "transfer", "unknown"] = "cash"


class TransactionUpdate(BaseModel):
    """All fields optional; only provided (set) fields are applied."""

    transaction_type: Literal["income", "expense", "unknown"] | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    description: str | None = None
    transaction_date: date | None = None
    payment_method: Literal["qr", "cash", "transfer", "unknown"] | None = None


class TransactionMutationResponse(BaseModel):
    transaction: TransactionResponse
    financial_summary: FinancialSummaryShort


class RejectTransactionResponse(BaseModel):
    transaction_id: str
    financial_summary: FinancialSummaryShort
