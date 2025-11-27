"""Structured logging configuration for Civic Chat.

This module provides JSON-formatted structured logging with:
- Correlation IDs for request tracking
- Agent name, duration, and outcome tracking
- PII redaction for sensitive data
- Consistent log format across all components
"""

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging.
    
    This formatter converts log records into JSON format with:
    - Timestamp in ISO 8601 format
    - Log level
    - Logger name
    - Message
    - Additional structured fields from 'extra' parameter
    - Correlation ID for request tracking
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record to format
        
        Returns:
            JSON-formatted log string
        """
        # Base log structure
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            log_data["correlation_id"] = record.correlation_id
        
        # Add agent name if available
        if hasattr(record, 'agent_name'):
            log_data["agent_name"] = record.agent_name
        
        # Add duration if available
        if hasattr(record, 'duration_ms'):
            log_data["duration_ms"] = record.duration_ms
        
        # Add outcome if available
        if hasattr(record, 'outcome'):
            log_data["outcome"] = record.outcome
        
        # Add any extra fields from the 'extra' parameter
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add all custom attributes from extra parameter
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName',
                          'relativeCreated', 'thread', 'threadName', 'exc_info',
                          'exc_text', 'stack_info', 'extra_fields']:
                # Only add if not already in log_data
                if key not in log_data:
                    log_data[key] = value
        
        return json.dumps(log_data)


class CorrelationIdFilter(logging.Filter):
    """Filter that adds correlation ID to log records.
    
    This filter ensures all log records have a correlation ID for
    tracking requests across multiple agents and components.
    """
    
    def __init__(self):
        super().__init__()
        self._correlation_id = None
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set the correlation ID for this filter.
        
        Args:
            correlation_id: Unique identifier for the request
        """
        self._correlation_id = correlation_id
    
    def get_correlation_id(self) -> Optional[str]:
        """Get the current correlation ID.
        
        Returns:
            Current correlation ID or None
        """
        return self._correlation_id
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to log record.
        
        Args:
            record: Log record to filter
        
        Returns:
            True (always allow the record)
        """
        if not hasattr(record, 'correlation_id') and self._correlation_id:
            record.correlation_id = self._correlation_id
        return True


# Global correlation ID filter instance
_correlation_filter = CorrelationIdFilter()


def configure_structured_logging(
    level: int = logging.INFO,
    enable_json: bool = True,
    log_file: Optional[str] = None
) -> None:
    """Configure structured logging for the application.
    
    This function sets up:
    - JSON-formatted logging (if enabled)
    - Correlation ID tracking
    - Console and file handlers
    - Appropriate log levels
    
    Args:
        level: Logging level (default: INFO)
        enable_json: Whether to use JSON formatting (default: True)
        log_file: Optional file path for log output
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler - set to WARNING to reduce console noise
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)  # Only show warnings and errors in console
    
    # Set formatter based on enable_json flag
    if enable_json:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    
    # Add correlation ID filter
    console_handler.addFilter(_correlation_filter)
    
    # Add console handler to root logger
    root_logger.addHandler(console_handler)
    
    # Add file handler if log_file specified - this will capture all logs
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)  # File gets all logs at specified level
        file_handler.setFormatter(formatter)
        file_handler.addFilter(_correlation_filter)
        root_logger.addHandler(file_handler)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set correlation ID for the current request.
    
    This function sets a correlation ID that will be included in all
    subsequent log messages until a new correlation ID is set.
    
    Args:
        correlation_id: Correlation ID to set (generates new UUID if None)
    
    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    
    _correlation_filter.set_correlation_id(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID.
    
    Returns:
        Current correlation ID or None
    """
    return _correlation_filter.get_correlation_id()


def clear_correlation_id() -> None:
    """Clear the current correlation ID."""
    _correlation_filter.set_correlation_id(None)


def log_agent_operation(
    logger: logging.Logger,
    agent_name: str,
    operation: str,
    duration_ms: Optional[int] = None,
    outcome: str = "success",
    **kwargs
) -> None:
    """Log an agent operation with structured data.
    
    This is a convenience function for logging agent operations with
    consistent structure and required fields.
    
    Args:
        logger: Logger instance to use
        agent_name: Name of the agent performing the operation
        operation: Description of the operation
        duration_ms: Duration in milliseconds (optional)
        outcome: Operation outcome (success, failure, etc.)
        **kwargs: Additional fields to include in the log
    """
    log_data = {
        "agent_name": agent_name,
        "operation": operation,
        "outcome": outcome,
    }
    
    if duration_ms is not None:
        log_data["duration_ms"] = duration_ms
    
    # Add any additional fields
    log_data.update(kwargs)
    
    # Determine log level based on outcome
    if outcome == "success":
        logger.info(f"Agent operation: {operation}", extra=log_data)
    elif outcome == "failure":
        logger.error(f"Agent operation failed: {operation}", extra=log_data)
    else:
        logger.warning(f"Agent operation: {operation}", extra=log_data)


def redact_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """Redact PII from data dictionary.
    
    This function redacts common PII fields to ensure sensitive
    information is not logged.
    
    Args:
        data: Dictionary that may contain PII
    
    Returns:
        Dictionary with PII fields redacted
    """
    pii_fields = [
        "user_id", "email", "name", "phone", "address",
        "ssn", "credit_card", "password", "token"
    ]
    
    redacted = data.copy()
    
    for field in pii_fields:
        if field in redacted:
            # Keep first 4 characters for debugging, redact rest
            value = str(redacted[field])
            if len(value) > 4:
                redacted[field] = value[:4] + "***"
            else:
                redacted[field] = "***"
    
    return redacted
