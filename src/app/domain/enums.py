from enum import StrEnum


class ManagementStatus(StrEnum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    OBSERVED = "observed"
    READY_FOR_ANALYSIS = "ready_for_analysis"


class MediaAssetStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    REVIEW = "review"
    FAILED = "failed"


class DocumentType(StrEnum):
    SALES_NOTEBOOK = "sales_notebook"
    QR_RECEIPT = "qr_receipt"
    PURCHASE_RECEIPT = "purchase_receipt"
    EXPENSE_NOTE = "expense_note"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class TransactionSourceType(StrEnum):
    AI = "ai"
    MANUAL = "manual"


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
    UNKNOWN = "unknown"


class PaymentMethod(StrEnum):
    QR = "qr"
    CASH = "cash"
    TRANSFER = "transfer"
    UNKNOWN = "unknown"


class TransactionStatus(StrEnum):
    EXTRACTED = "extracted"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CORRECTED = "corrected"
    MANUAL = "manual"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class SalesFrequency(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class DocumentaryEvidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class AlertLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
