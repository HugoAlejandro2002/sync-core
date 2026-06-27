"""Pure ORM -> response-DTO builders (money as strings, raw value + Spanish label)."""

from __future__ import annotations

from typing import Any

from app.domain.labels import (
    UNKNOWN_LABEL,
    document_type_label,
    management_status_label,
    media_asset_status_label,
    payment_method_label,
    transaction_source_label,
    transaction_status_label,
    transaction_type_label,
)
from app.domain.money import format_money
from app.models.customer import Customer
from app.models.management import Management
from app.models.media_asset import MediaAsset
from app.models.transaction import Transaction
from app.schemas.common import (
    Alert,
    FinancialSummary,
    FinancialSummaryCard,
    FinancialSummaryShort,
)
from app.schemas.customer_schema import CustomerMini, CustomerResponse
from app.schemas.management_schema import (
    ManagementDetail,
    ManagementListItem,
)
from app.schemas.media_asset_schema import EvidenceResponse
from app.schemas.transaction_schema import TransactionResponse


def _to_float(value: Any) -> float | None:
    return float(value) if value is not None else None


def build_customer_response(customer: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        full_name=customer.full_name,
        phone_number=customer.phone_number,
        nit=customer.nit,
        business_name=customer.business_name,
        business_type=customer.business_type,
        business_description=customer.business_description,
        market_location=customer.market_location,
    )


def build_customer_mini(customer: Customer) -> CustomerMini:
    return CustomerMini(
        full_name=customer.full_name,
        phone_number=customer.phone_number,
        business_name=customer.business_name,
    )


def build_evidence_response(media: MediaAsset) -> EvidenceResponse:
    label = media.document_type_label or (
        document_type_label(media.document_type) if media.document_type else None
    )
    return EvidenceResponse(
        id=media.id,
        filename=media.original_filename,
        status=media.status,
        status_label=media_asset_status_label(media.status),
        document_type=media.document_type,
        document_type_label=label,
        detected_amount=format_money(media.detected_amount)
        if media.detected_amount is not None
        else None,
        confidence_score=_to_float(media.confidence_score),
        extracted_text=media.extracted_text,
    )


def build_transaction_response(tx: Transaction) -> TransactionResponse:
    return TransactionResponse(
        id=tx.id,
        management_id=tx.management_id,
        media_asset_id=tx.media_asset_id,
        source_type=tx.source_type,
        source_type_label=transaction_source_label(tx.source_type),
        transaction_type=tx.transaction_type,
        transaction_type_label=transaction_type_label(tx.transaction_type),
        amount=format_money(tx.amount),
        currency=tx.currency,
        description=tx.description,
        transaction_date=tx.transaction_date.isoformat() if tx.transaction_date else None,
        payment_method=tx.payment_method,
        payment_method_label=payment_method_label(tx.payment_method),
        evidence_text=tx.evidence_text,
        confidence_score=_to_float(tx.confidence_score),
        status=tx.status,
        status_label=transaction_status_label(tx.status),
    )


def _analysis_label(management: Management, key: str) -> str:
    analysis = management.analysis_summary or {}
    node = analysis.get(key) or {}
    return node.get("label", UNKNOWN_LABEL)


def build_financial_summary(management: Management) -> FinancialSummary:
    return FinancialSummary(
        total_income=format_money(management.total_income),
        total_expense=format_money(management.total_expense),
        net_balance=format_money(management.net_balance),
        sales_frequency=_analysis_label(management, "sales_frequency"),
        documentary_evidence=_analysis_label(management, "documentary_evidence"),
        preliminary_risk=_analysis_label(management, "preliminary_risk"),
        confidence_score=_to_float(management.confidence_score),
    )


def build_financial_summary_card(management: Management) -> FinancialSummaryCard:
    return FinancialSummaryCard(
        total_income=format_money(management.total_income),
        total_expense=format_money(management.total_expense),
        net_balance=format_money(management.net_balance),
        preliminary_risk=_analysis_label(management, "preliminary_risk"),
        confidence_score=_to_float(management.confidence_score),
    )


def build_financial_summary_short(management: Management) -> FinancialSummaryShort:
    return FinancialSummaryShort(
        total_income=format_money(management.total_income),
        total_expense=format_money(management.total_expense),
        net_balance=format_money(management.net_balance),
        confidence_score=_to_float(management.confidence_score),
    )


def build_alerts(management: Management) -> list[Alert]:
    alerts = management.alerts or []
    return [
        Alert(
            level=str(a.get("level", "info")),
            message=str(a.get("message", "")),
            level_label=a.get("level_label"),
        )
        for a in alerts
    ]


def build_management_detail(management: Management) -> ManagementDetail:
    evidences = sorted(management.media_assets, key=lambda m: m.created_at)
    transactions = sorted(management.transactions, key=lambda t: t.created_at)
    return ManagementDetail(
        id=management.id,
        application_code=management.application_code,
        status=management.status,
        status_label=management_status_label(management.status),
        submitted_at=management.submitted_at.isoformat(),
        requested_amount=format_money(management.requested_amount),
        currency=management.currency,
        visit_date=management.visit_date.isoformat() if management.visit_date else None,
        customer=build_customer_response(management.customer),
        financial_summary=build_financial_summary(management),
        evidences=[build_evidence_response(m) for m in evidences],
        transactions=[build_transaction_response(t) for t in transactions],
        alerts=build_alerts(management),
        advisor_notes=management.advisor_notes,
    )


def build_management_list_item(management: Management) -> ManagementListItem:
    return ManagementListItem(
        id=management.id,
        application_code=management.application_code,
        status=management.status,
        status_label=management_status_label(management.status),
        submitted_at=management.submitted_at.isoformat(),
        requested_amount=format_money(management.requested_amount),
        currency=management.currency,
        customer=build_customer_mini(management.customer),
        financial_summary=build_financial_summary_card(management),
        evidences_count=len(management.media_assets),
        alerts_count=len(management.alerts or []),
    )
