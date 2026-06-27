from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, object] = {}


class ErrorResponse(BaseModel):
    """Top-level error body, e.g. {"error": {"code": ..., "message": ..., "details": {}}}."""

    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "Caja Inteligente API"


class Alert(BaseModel):
    level: str
    message: str
    level_label: str | None = None


class FinancialSummary(BaseModel):
    """Full financial summary used in create/detail responses (money as strings)."""

    total_income: str
    total_expense: str
    net_balance: str
    sales_frequency: str
    documentary_evidence: str
    preliminary_risk: str
    confidence_score: float | None = None


class FinancialSummaryCard(BaseModel):
    """Compact summary used in list cards."""

    total_income: str
    total_expense: str
    net_balance: str
    preliminary_risk: str
    confidence_score: float | None = None


class FinancialSummaryShort(BaseModel):
    """Minimal summary returned after a single transaction change."""

    total_income: str
    total_expense: str
    net_balance: str
    confidence_score: float | None = None
