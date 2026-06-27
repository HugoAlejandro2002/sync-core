from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from app.domain.enums import (
    AlertLevel,
    DocumentaryEvidenceLevel,
    MediaAssetStatus,
    RiskLevel,
    SalesFrequency,
    TransactionSourceType,
    TransactionStatus,
    TransactionType,
)
from app.domain.labels import ALERT_LEVEL_LABELS, level_label
from app.domain.money import to_money, zero_money
from app.models.media_asset import MediaAsset
from app.models.transaction import Transaction

LOW_CONFIDENCE = Decimal("0.75")
HIGH_CONFIDENCE = Decimal("0.85")


@dataclass
class SummaryResult:
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    confidence_score: Decimal | None
    analysis_summary: dict[str, Any]
    alerts: list[dict[str, Any]] = field(default_factory=list)


def _labeled(value: str) -> dict[str, str]:
    return {"value": value, "label": level_label(value)}


def _alert(level: AlertLevel, message: str) -> dict[str, Any]:
    return {"level": level.value, "message": message, "level_label": ALERT_LEVEL_LABELS[level]}


class SummaryService:
    """Pure financial calculator. Excludes rejected transactions. No DB access."""

    def calculate(
        self,
        transactions: list[Transaction],
        media_assets: list[MediaAsset],
    ) -> SummaryResult:
        active = [t for t in transactions if t.status != TransactionStatus.REJECTED.value]

        total_income = sum(
            (t.amount for t in active if t.transaction_type == TransactionType.INCOME.value),
            zero_money(),
        )
        total_expense = sum(
            (t.amount for t in active if t.transaction_type == TransactionType.EXPENSE.value),
            zero_money(),
        )
        total_income = to_money(total_income)
        total_expense = to_money(total_expense)
        net_balance = to_money(total_income - total_expense)

        confidence_score = self._confidence(active)
        analysis = self._analysis(active, media_assets, net_balance)
        alerts = self._alerts(active, media_assets)

        return SummaryResult(
            total_income=total_income,
            total_expense=total_expense,
            net_balance=net_balance,
            confidence_score=confidence_score,
            analysis_summary=analysis,
            alerts=alerts,
        )

    def _confidence(self, active: list[Transaction]) -> Decimal | None:
        scores = [
            t.confidence_score
            for t in active
            if t.source_type == TransactionSourceType.AI.value and t.confidence_score is not None
        ]
        if not scores:
            return None
        average = sum(scores, Decimal("0")) / Decimal(len(scores))
        return average.quantize(Decimal("0.0001"))

    def _analysis(
        self,
        active: list[Transaction],
        media_assets: list[MediaAsset],
        net_balance: Decimal,
    ) -> dict[str, Any]:
        sales = self._sales_frequency(active, media_assets)
        evidence = self._documentary_evidence(media_assets)
        risk = self._preliminary_risk(active, media_assets, net_balance, evidence)
        return {
            "sales_frequency": _labeled(sales.value),
            "documentary_evidence": _labeled(evidence.value),
            "preliminary_risk": _labeled(risk.value),
        }

    def _sales_frequency(
        self, active: list[Transaction], media_assets: list[MediaAsset]
    ) -> SalesFrequency:
        if not active and not media_assets:
            return SalesFrequency.UNKNOWN
        income_count = sum(1 for t in active if t.transaction_type == TransactionType.INCOME.value)
        if income_count >= 3:
            return SalesFrequency.HIGH
        if income_count >= 1:
            return SalesFrequency.MEDIUM
        return SalesFrequency.LOW

    def _documentary_evidence(self, media_assets: list[MediaAsset]) -> DocumentaryEvidenceLevel:
        total = len(media_assets)
        if total == 0:
            return DocumentaryEvidenceLevel.UNKNOWN
        failed = sum(1 for m in media_assets if m.status == MediaAssetStatus.FAILED.value)
        high_conf = sum(
            1
            for m in media_assets
            if m.status == MediaAssetStatus.PROCESSED.value
            and m.confidence_score is not None
            and m.confidence_score >= HIGH_CONFIDENCE
        )
        if high_conf >= 2 and failed == 0:
            return DocumentaryEvidenceLevel.HIGH
        if failed > total / 2:
            return DocumentaryEvidenceLevel.LOW
        return DocumentaryEvidenceLevel.MEDIUM

    def _preliminary_risk(
        self,
        active: list[Transaction],
        media_assets: list[MediaAsset],
        net_balance: Decimal,
        evidence: DocumentaryEvidenceLevel,
    ) -> RiskLevel:
        if not active and not media_assets:
            return RiskLevel.UNKNOWN
        failed = sum(1 for m in media_assets if m.status == MediaAssetStatus.FAILED.value)
        if net_balance < 0:
            return RiskLevel.HIGH
        if media_assets and failed > len(media_assets) / 2:
            return RiskLevel.HIGH
        if net_balance > 0 and evidence in (
            DocumentaryEvidenceLevel.MEDIUM,
            DocumentaryEvidenceLevel.HIGH,
        ):
            return RiskLevel.LOW
        return RiskLevel.MEDIUM

    def _alerts(
        self, active: list[Transaction], media_assets: list[MediaAsset]
    ) -> list[dict[str, Any]]:
        alerts: list[dict[str, Any]] = []

        for media in media_assets:
            if media.status == MediaAssetStatus.FAILED.value:
                alerts.append(
                    _alert(
                        AlertLevel.WARNING,
                        f"La evidencia «{media.original_filename}» no se pudo procesar. "
                        "Verificar el archivo original.",
                    )
                )
                continue
            if media.confidence_score is not None and media.confidence_score < LOW_CONFIDENCE:
                pct = int(media.confidence_score * 100)
                alerts.append(
                    _alert(
                        AlertLevel.WARNING,
                        f"La evidencia «{media.original_filename}» tiene baja confianza de "
                        f"lectura ({pct}%). Verificar documento original.",
                    )
                )
            raw = media.ai_raw_response or {}
            for warning in raw.get("warnings", []) or []:
                alerts.append(_alert(AlertLevel.WARNING, str(warning)))

        for tx in active:
            if tx.confidence_score is not None and tx.confidence_score < LOW_CONFIDENCE:
                pct = int(tx.confidence_score * 100)
                desc = tx.description or "sin descripción"
                alerts.append(
                    _alert(
                        AlertLevel.WARNING,
                        f"La transacción «{desc}» tiene baja confianza ({pct}%).",
                    )
                )
            if tx.transaction_type == TransactionType.UNKNOWN.value:
                desc = tx.description or "sin descripción"
                alerts.append(
                    _alert(
                        AlertLevel.WARNING,
                        f"La transacción «{desc}» no pudo clasificarse como ingreso o gasto.",
                    )
                )

        processed = [
            m
            for m in media_assets
            if m.status in (MediaAssetStatus.PROCESSED.value, MediaAssetStatus.REVIEW.value)
        ]
        if processed and not active:
            alerts.append(
                _alert(
                    AlertLevel.INFO,
                    "Se procesaron evidencias pero no se detectaron transacciones. "
                    "Considere agregar transacciones manualmente.",
                )
            )

        return alerts
