from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import (
    Alert,
    FinancialSummary,
    FinancialSummaryCard,
)
from app.schemas.customer_schema import CustomerMini, CustomerResponse
from app.schemas.media_asset_schema import EvidenceResponse
from app.schemas.transaction_schema import TransactionResponse


class ManagementCreateInput(BaseModel):
    """Validated customer + application data parsed from the multipart create form."""

    full_name: str = Field(min_length=1)
    phone_number: str | None = None
    nit: str | None = None
    business_name: str | None = None
    business_type: str | None = None
    business_description: str | None = None
    market_location: str | None = None

    requested_amount: Decimal = Field(gt=0)
    currency: str = "BOB"
    visit_date: date | None = None
    advisor_notes: str | None = None


class ManagementListItem(BaseModel):
    id: str
    application_code: str
    status: str
    status_label: str
    submitted_at: str
    requested_amount: str
    currency: str
    customer: CustomerMini
    financial_summary: FinancialSummaryCard
    evidences_count: int
    alerts_count: int


class ManagementListResponse(BaseModel):
    items: list[ManagementListItem]


class ManagementDetail(BaseModel):
    id: str
    application_code: str
    status: str
    status_label: str
    submitted_at: str
    requested_amount: str
    currency: str
    visit_date: str | None = None
    customer: CustomerResponse
    financial_summary: FinancialSummary
    evidences: list[EvidenceResponse]
    transactions: list[TransactionResponse]
    alerts: list[Alert]
    advisor_notes: str | None = None


class AdvisorNotesUpdate(BaseModel):
    advisor_notes: str | None = None


class AdvisorNotesResponse(BaseModel):
    management_id: str
    advisor_notes: str | None = None


class StatusUpdate(BaseModel):
    status: str


class StatusResponse(BaseModel):
    management_id: str
    status: str
    status_label: str
