"""
Loud Hawk v2 - Custom Exception Classes

Professional error taxonomy for consistent API responses
"""

from typing import Optional


class LoudHawkException(Exception):
    """Base exception for Loud Hawk application"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FetchError(LoudHawkException):
    """Error during fetching data from external sources"""
    def __init__(self, message: str, source: Optional[str] = None, status_code: Optional[int] = None):
        self.source = source
        self.status_code = status_code
        super().__init__(message, "FETCH_ERROR")


class ParseError(LoudHawkException):
    """Error during parsing of data (XML, HTML, JSON)"""
    def __init__(self, message: str, source: Optional[str] = None, content_type: Optional[str] = None):
        self.source = source
        self.content_type = content_type
        super().__init__(message, "PARSE_ERROR")


class RateLimitError(LoudHawkException):
    """Rate limit exceeded for external API or source"""
    def __init__(self, message: str, source: Optional[str] = None, retry_after: Optional[int] = None):
        self.source = source
        self.retry_after = retry_after
        super().__init__(message, "RATE_LIMIT_ERROR")


class CircuitBreakerOpen(LoudHawkException):
    """Circuit breaker is open for a source"""
    def __init__(self, message: str, source: Optional[str] = None, cooldown_until: Optional[str] = None):
        self.source = source
        self.cooldown_until = cooldown_until
        super().__init__(message, "CIRCUIT_BREAKER_OPEN")


class DatabaseError(LoudHawkException):
    """Database operation failed"""
    def __init__(self, message: str, operation: Optional[str] = None):
        self.operation = operation
        super().__init__(message, "DATABASE_ERROR")


class ValidationError(LoudHawkException):
    """Data validation failed"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")


class ConfigurationError(LoudHawkException):
    """Configuration or environment setup error"""
    def __init__(self, message: str, setting: Optional[str] = None):
        self.setting = setting
        super().__init__(message, "CONFIGURATION_ERROR")
