from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, object] = {}


class ApiResponse[T](BaseModel):
    success: bool = True
    data: T | None = None
    error: ErrorDetail | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "Caja Inteligente API"
