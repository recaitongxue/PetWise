"""
Structured Logging Module
Provides JSON-formatted structured logging for better log analysis
"""
import logging
import json
import time
import traceback
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar

from config import Config

request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id
        
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data, ensure_ascii=False)

def setup_structured_logging():
    """Setup structured logging configuration"""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    if Config.LOG_FORMAT == "structured":
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(handler)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

def set_request_context(request_id: str, user_id: Optional[str] = None):
    """Set request context for logging"""
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)

def clear_request_context():
    """Clear request context"""
    request_id_var.set('')
    user_id_var.set('')

class APILogger:
    """API-specific logger for request/response logging"""
    
    def __init__(self, name: str = "api"):
        self.logger = get_logger(name)
    
    def log_request(self, method: str, path: str, headers: Dict[str, str], 
                   body: Optional[Dict[str, Any]] = None):
        """Log API request"""
        self.logger.info(
            f"API Request: {method} {path}",
            extra={
                "event": "api_request",
                "method": method,
                "path": path,
                "headers": self._sanitize_headers(headers),
                "body": body
            }
        )
    
    def log_response(self, method: str, path: str, status_code: int, 
                    duration_ms: float, body: Optional[Dict[str, Any]] = None):
        """Log API response"""
        self.logger.info(
            f"API Response: {method} {path} - {status_code}",
            extra={
                "event": "api_response",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "body": body
            }
        )
    
    def log_error(self, method: str, path: str, error: Exception, 
                 status_code: Optional[int] = None):
        """Log API error"""
        self.logger.error(
            f"API Error: {method} {path} - {type(error).__name__}",
            extra={
                "event": "api_error",
                "method": method,
                "path": path,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "status_code": status_code
            }
        )
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize sensitive headers"""
        sanitized = {}
        sensitive_keys = ['authorization', 'api-key', 'x-api-key']
        
        for key, value in headers.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized

class PerformanceLogger:
    """Performance monitoring logger"""
    
    def __init__(self, name: str = "performance"):
        self.logger = get_logger(name)
    
    def log_query_time(self, query_type: str, duration_ms: float, 
                      details: Optional[Dict[str, Any]] = None):
        """Log database query time"""
        self.logger.info(
            f"Query executed: {query_type}",
            extra={
                "event": "query",
                "query_type": query_type,
                "duration_ms": round(duration_ms, 2),
                "details": details or {}
            }
        )
    
    def log_cache_operation(self, operation: str, key: str, 
                           hit: bool, duration_ms: float):
        """Log cache operation"""
        self.logger.debug(
            f"Cache {operation}: {key}",
            extra={
                "event": "cache",
                "operation": operation,
                "key": key,
                "hit": hit,
                "duration_ms": round(duration_ms, 2)
            }
        )
    
    def log_external_api_call(self, provider: str, endpoint: str, 
                             duration_ms: float, status_code: int):
        """Log external API call"""
        self.logger.info(
            f"External API call: {provider} {endpoint}",
            extra={
                "event": "external_api",
                "provider": provider,
                "endpoint": endpoint,
                "duration_ms": round(duration_ms, 2),
                "status_code": status_code
            }
        )