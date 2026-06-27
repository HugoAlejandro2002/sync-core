class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: dict[str, object] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppError):
    def __init__(
        self,
        code: str = "NOT_FOUND",
        message: str = "No se encontró el recurso.",
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, status_code=404, details=details)


class ValidationError(AppError):
    def __init__(
        self,
        code: str = "VALIDATION_ERROR",
        message: str = "Datos inválidos.",
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, status_code=400, details=details)


class ImageProcessingError(AppError):
    def __init__(
        self,
        code: str = "IMAGE_PROCESSING_FAILED",
        message: str = "No se pudo procesar la imagen.",
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, status_code=500, details=details)


class ExtractionError(AppError):
    def __init__(
        self,
        code: str = "EXTRACTION_FAILED",
        message: str = "No se pudo extraer información financiera de la imagen.",
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, status_code=500, details=details)


class InvalidStatusError(AppError):
    def __init__(
        self,
        code: str = "INVALID_STATUS",
        message: str = "El estado enviado no es válido.",
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, status_code=400, details=details)
