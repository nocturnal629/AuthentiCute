import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthentiCuteException(Exception):
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(AuthentiCuteException):
    pass

class ValidationError(AuthentiCuteException):
    pass

class DatabaseError(AuthentiCuteException):
    pass

class EmailError(AuthentiCuteException):
    pass

class RateLimitError(AuthentiCuteException):
    pass

def create_error_response(
    message: str,
    error_code: str = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Dict[str, Any] = None
) -> JSONResponse:
    """Create a standardized error response"""
    error_data = {
        "error": {
            "message": message,
            "code": error_code or "UNKNOWN_ERROR",
            "details": details or {}
        }
    }
    
    return JSONResponse(
        status_code=status_code,
        content=error_data
    )

def handle_authentication_error(message: str, error_code: str = "AUTH_ERROR") -> HTTPException:
    """Create authentication error exception"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "message": message,
                "code": error_code
            }
        }
    )

def handle_validation_error(message: str, field: str = None) -> HTTPException:
    """Create validation error exception"""
    details = {"field": field} if field else {}
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "error": {
                "message": message,
                "code": "VALIDATION_ERROR",
                "details": details
            }
        }
    )

def handle_rate_limit_error(remaining_time: int = None) -> HTTPException:
    """Create rate limit error exception"""
    message = "Rate limit exceeded. Please try again later."
    if remaining_time:
        message = f"Rate limit exceeded. Please try again in {remaining_time} seconds."
    
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": {
                "message": message,
                "code": "RATE_LIMIT_EXCEEDED",
                "details": {"retry_after": remaining_time}
            }
        }
    )

def log_error(error: Exception, context: Dict[str, Any] = None):
    """
    Log error with context information
    
    Args:
        error: The exception that occurred
        context: Additional context information
    """
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }
    
    logger.error(f"Application error: {error_info}")
    
    if isinstance(error, DatabaseError):
        logger.error(f"Database error: {error.details}")
    elif isinstance(error, EmailError):
        logger.error(f"Email error: {error.details}")
    elif isinstance(error, RateLimitError):
        logger.warning(f"Rate limit exceeded: {error.details}")

def handle_unexpected_error(error: Exception, request_info: Dict[str, Any] = None):
    """
    Handle unexpected errors with proper logging
    
    Args:
        error: The unexpected exception
        request_info: Information about the request that caused the error
    """
    context = {
        "request_info": request_info or {},
        "error_traceback": str(error)
    }
    
    log_error(error, context)
    
    return create_error_response(
        message="An unexpected error occurred. Please try again later.",
        error_code="INTERNAL_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    ) 