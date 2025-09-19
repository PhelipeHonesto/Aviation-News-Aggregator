"""
Loud Hawk v2 - Structured Logging Configuration

Professional logging with JSON format for production observability
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
import os


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'source'):
            log_entry['source'] = record.source
        if hasattr(record, 'run_id'):
            log_entry['run_id'] = record.run_id
        if hasattr(record, 'adapter'):
            log_entry['adapter'] = record.adapter
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'items_found'):
            log_entry['items_found'] = record.items_found
        if hasattr(record, 'items_saved'):
            log_entry['items_saved'] = record.items_saved
        if hasattr(record, 'error_type'):
            log_entry['error_type'] = record.error_type
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)


def setup_logging():
    """Setup structured logging configuration"""
    
    # Get log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("feedparser").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with structured logging"""
    return logging.getLogger(name)


# Convenience functions for structured logging
def log_ingest_start(logger: logging.Logger, source: str, run_id: str):
    """Log ingestion start"""
    logger.info(
        f"Starting ingestion for source: {source}",
        extra={
            "source": source,
            "run_id": run_id,
            "adapter": "ingest"
        }
    )


def log_ingest_success(logger: logging.Logger, source: str, run_id: str, 
                      items_found: int, items_saved: int, duration_ms: int):
    """Log successful ingestion"""
    logger.info(
        f"Ingestion completed for {source}: {items_saved}/{items_found} articles saved",
        extra={
            "source": source,
            "run_id": run_id,
            "adapter": "ingest",
            "items_found": items_found,
            "items_saved": items_saved,
            "duration_ms": duration_ms
        }
    )


def log_ingest_error(logger: logging.Logger, source: str, run_id: str, 
                    error_type: str, error_message: str):
    """Log ingestion error"""
    logger.error(
        f"Ingestion failed for {source}: {error_message}",
        extra={
            "source": source,
            "run_id": run_id,
            "adapter": "ingest",
            "error_type": error_type
        }
    )


def log_api_request(logger: logging.Logger, endpoint: str, method: str, 
                   status_code: int, duration_ms: int, user_id: str = None):
    """Log API request"""
    extra = {
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "duration_ms": duration_ms
    }
    if user_id:
        extra["user_id"] = user_id
        
    logger.info(
        f"{method} {endpoint} - {status_code} ({duration_ms}ms)",
        extra=extra
    )
