from fastapi import APIRouter

from app.schemas.common import ApiResponse, HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=ApiResponse[HealthResponse])
async def health() -> ApiResponse[HealthResponse]:
    return ApiResponse(data=HealthResponse())
