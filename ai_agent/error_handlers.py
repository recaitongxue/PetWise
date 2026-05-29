"""
Error Handling Middleware
Provides centralized exception handling for the API
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Dict, Optional
import traceback

from exceptions import AIAgentException, KnowledgeBaseException, APIException
from structured_logger import get_logger, set_request_context

logger = get_logger("error_handler")

class ErrorResponse:
    """Standardized error response format"""
    
    @staticmethod
    def create(
        status_code: int,
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            "success": False,
            "error": {
                "type": error_type,
                "message": message,
                "status_code": status_code
            }
        }
        
        if details:
            response["error"]["details"] = details
        
        if request_id:
            response["request_id"] = request_id
        
        return response

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    request_id = request.headers.get("X-Request-ID", "")
    
    logger.error(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "event": "http_exception",
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.create(
            status_code=exc.status_code,
            error_type="HTTPException",
            message=str(exc.detail),
            request_id=request_id
        )
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    request_id = request.headers.get("X-Request-ID", "")
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation Error: {len(errors)} errors",
        extra={
            "event": "validation_error",
            "errors": errors,
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse.create(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type="ValidationError",
            message="Request validation failed",
            details={"errors": errors},
            request_id=request_id
        )
    )

async def ai_agent_exception_handler(request: Request, exc: AIAgentException):
    """Handle AI Agent exceptions"""
    request_id = request.headers.get("X-Request-ID", "")
    
    logger.error(
        f"AI Agent Exception: {type(exc).__name__}",
        extra={
            "event": "ai_agent_exception",
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id
        }
    )
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(exc, KnowledgeBaseException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, APIException):
        status_code = status.HTTP_502_BAD_GATEWAY
    
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse.create(
            status_code=status_code,
            error_type=type(exc).__name__,
            message=str(exc),
            request_id=request_id
        )
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    request_id = request.headers.get("X-Request-ID", "")
    
    logger.critical(
        f"Unhandled Exception: {type(exc).__name__}",
        extra={
            "event": "unhandled_exception",
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse.create(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type="InternalServerError",
            message="An unexpected error occurred. Please try again later.",
            details={"traceback_id": request_id} if request_id else None,
            request_id=request_id
        )
    )

def setup_error_handlers(app):
    """Setup all error handlers for the FastAPI app"""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(AIAgentException, ai_agent_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers registered successfully")