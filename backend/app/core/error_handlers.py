"""
Global error handling middleware for production-ready error responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import structlog
import traceback

logger = structlog.get_logger(__name__)


class APIError(Exception):
    """Base API error class."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(APIError):
    """Database related errors."""
    
    def __init__(self, message: str = "Database error occurred", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )


class AuthenticationError(APIError):
    """Authentication related errors."""
    
    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_ERROR",
            details=details
        )


class AuthorizationError(APIError):
    """Authorization related errors."""
    
    def __init__(self, message: str = "Access denied", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ResourceNotFoundError(APIError):
    """Resource not found errors."""
    
    def __init__(self, resource: str = "Resource", details: dict = None):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )


class ValidationError(APIError):
    """Validation related errors."""
    
    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class RateLimitError(APIError):
    """Rate limit errors."""
    
    def __init__(self, message: str = "Too many requests", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


class ExternalAPIError(APIError):
    """External API integration errors."""
    
    def __init__(self, service: str, message: str = None, details: dict = None):
        super().__init__(
            message=message or f"{service} API error",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_API_ERROR",
            details=details or {"service": service}
        )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom API errors."""
    logger.error(
        "API Error",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            },
            "path": request.url.path
        }
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        "Validation Error",
        path=request.url.path,
        errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "errors": errors
                }
            },
            "path": request.url.path
        }
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors."""
    error_msg = str(exc)
    logger.error(
        "Database Error",
        path=request.url.path,
        error=error_msg,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "A database error occurred",
                "details": {
                    "info": "Please try again later"
                }
            },
            "path": request.url.path
        }
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all uncaught exceptions."""
    error_traceback = traceback.format_exc()
    
    logger.error(
        "Unhandled Exception",
        path=request.url.path,
        error=str(exc),
        traceback=error_traceback,
        exc_info=True
    )
    
    # In production, don't expose internal error details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {
                    "info": "Our team has been notified"
                }
            },
            "path": request.url.path
        }
    )


def setup_error_handlers(app):
    """Register all error handlers with FastAPI app."""
    from fastapi.exceptions import RequestValidationError
    
    # Custom API errors
    app.add_exception_handler(APIError, api_error_handler)
    
    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    
    # Database errors
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    
    # Generic errors (catch-all)
    app.add_exception_handler(Exception, generic_error_handler)
    
    logger.info("✅ Error handlers registered")
