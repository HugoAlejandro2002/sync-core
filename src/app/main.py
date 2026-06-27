from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controllers.health_controller import router as health_router
from app.controllers.managements_controller import router as managements_router
from app.controllers.transactions_controller import router as transactions_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import setup_logging
from app.schemas.common import ErrorDetail, ErrorResponse

settings = get_settings()

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    debug=settings.APP_DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message, details=exc.details),
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Datos inválidos.",
                details={"errors": exc.errors()},
            ),
        ).model_dump(),
    )


app.include_router(health_router)
app.include_router(managements_router)
app.include_router(transactions_router)
