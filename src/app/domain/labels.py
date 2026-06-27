"""Spanish (es-BO) labels for domain enum values.

The backend always returns both the raw enum value and its Spanish label so the
frontend never has to guess translations.
"""

from app.domain.enums import (
    AlertLevel,
    DocumentaryEvidenceLevel,
    DocumentType,
    ManagementStatus,
    MediaAssetStatus,
    PaymentMethod,
    RiskLevel,
    SalesFrequency,
    TransactionSourceType,
    TransactionStatus,
    TransactionType,
)

UNKNOWN_LABEL = "Desconocido"

MANAGEMENT_STATUS_LABELS: dict[str, str] = {
    ManagementStatus.PENDING: "Pendiente",
    ManagementStatus.IN_REVIEW: "En revisión",
    ManagementStatus.OBSERVED: "Observado",
    ManagementStatus.READY_FOR_ANALYSIS: "Listo para análisis",
}

MEDIA_ASSET_STATUS_LABELS: dict[str, str] = {
    MediaAssetStatus.UPLOADED: "Subido",
    MediaAssetStatus.PROCESSING: "Procesando",
    MediaAssetStatus.PROCESSED: "Procesado",
    MediaAssetStatus.REVIEW: "Revisar",
    MediaAssetStatus.FAILED: "Fallido",
}

DOCUMENT_TYPE_LABELS: dict[str, str] = {
    DocumentType.SALES_NOTEBOOK: "Cuaderno de ventas",
    DocumentType.QR_RECEIPT: "Comprobante QR",
    DocumentType.PURCHASE_RECEIPT: "Recibo de compra",
    DocumentType.EXPENSE_NOTE: "Nota de gasto",
    DocumentType.MIXED: "Mixto",
    DocumentType.UNKNOWN: UNKNOWN_LABEL,
}

# Shared low/medium/high scale used by risk, sales frequency and documentary evidence.
_LEVEL_LABELS: dict[str, str] = {
    "low": "Bajo",
    "medium": "Media",
    "high": "Alta",
    "unknown": UNKNOWN_LABEL,
}

TRANSACTION_TYPE_LABELS: dict[str, str] = {
    TransactionType.INCOME: "Ingreso",
    TransactionType.EXPENSE: "Gasto",
    TransactionType.UNKNOWN: UNKNOWN_LABEL,
}

TRANSACTION_SOURCE_LABELS: dict[str, str] = {
    TransactionSourceType.AI: "IA",
    TransactionSourceType.MANUAL: "Manual",
}

TRANSACTION_STATUS_LABELS: dict[str, str] = {
    TransactionStatus.EXTRACTED: "Extraído",
    TransactionStatus.CONFIRMED: "Confirmado",
    TransactionStatus.REJECTED: "Rechazado",
    TransactionStatus.CORRECTED: "Corregido",
    TransactionStatus.MANUAL: "Manual",
}

PAYMENT_METHOD_LABELS: dict[str, str] = {
    PaymentMethod.QR: "QR",
    PaymentMethod.CASH: "Efectivo",
    PaymentMethod.TRANSFER: "Transferencia",
    PaymentMethod.UNKNOWN: UNKNOWN_LABEL,
}

ALERT_LEVEL_LABELS: dict[str, str] = {
    AlertLevel.INFO: "Información",
    AlertLevel.WARNING: "Advertencia",
    AlertLevel.ERROR: "Error",
}


def management_status_label(value: str) -> str:
    return MANAGEMENT_STATUS_LABELS.get(value, UNKNOWN_LABEL)


def media_asset_status_label(value: str) -> str:
    return MEDIA_ASSET_STATUS_LABELS.get(value, UNKNOWN_LABEL)


def document_type_label(value: str | None) -> str:
    if value is None:
        return UNKNOWN_LABEL
    return DOCUMENT_TYPE_LABELS.get(value, UNKNOWN_LABEL)


def level_label(value: str) -> str:
    return _LEVEL_LABELS.get(value, UNKNOWN_LABEL)


def transaction_type_label(value: str) -> str:
    return TRANSACTION_TYPE_LABELS.get(value, UNKNOWN_LABEL)


def transaction_source_label(value: str) -> str:
    return TRANSACTION_SOURCE_LABELS.get(value, UNKNOWN_LABEL)


def transaction_status_label(value: str) -> str:
    return TRANSACTION_STATUS_LABELS.get(value, UNKNOWN_LABEL)


def payment_method_label(value: str) -> str:
    return PAYMENT_METHOD_LABELS.get(value, UNKNOWN_LABEL)
