from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger("http")


class BadRequestError(HTTPException):
    def __init__(self, detail: str = "Datos inválidos"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadGatewayError(HTTPException):
    def __init__(self, detail: str = "Error en servicio externo"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP {exc.status_code} | {request.method} {request.url.path} | {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"HTTP 422 | {request.method} {request.url.path} | Error de validación")
        return JSONResponse(
            status_code=422,
            content={"error": "Error de validación en la solicitud.", "details": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Error no manejado | {request.method} {request.url.path} | {type(exc).__name__}: {exc}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Ocurrió un error interno en el servidor."},
        )
