"""Error response models for the civic chat system.

This module defines the data structures used for representing
errors and providing user-friendly error messages with actionable
guidance for recovery.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ErrorResponse:
    """Model for error responses with recovery guidance.
    
    This data class encapsulates error information in a structured format
    that includes both technical details for logging and user-friendly
    messages for display.
    
    Attributes:
        error_code: Machine-readable error code (e.g., "RATE_LIMIT_EXCEEDED")
        error_message: Technical error message for logging
        user_message: User-friendly error message for display
        retry_after_seconds: Optional seconds to wait before retrying
        suggested_actions: Optional list of suggested recovery actions
        correlation_id: Optional correlation ID for tracking the error
    
    Example:
        >>> error = ErrorResponse(
        ...     error_code="RATE_LIMIT_EXCEEDED",
        ...     error_message="Azure OpenAI rate limit exceeded: 429 Too Many Requests",
        ...     user_message="The system is experiencing high demand. Please try again in a moment.",
        ...     retry_after_seconds=30,
        ...     suggested_actions=["Wait 30 seconds and try again", "Simplify your query"],
        ...     correlation_id="abc-123-def-456"
        ... )
    """
    error_code: str
    error_message: str
    user_message: str
    retry_after_seconds: Optional[int] = None
    suggested_actions: Optional[List[str]] = None
    correlation_id: Optional[str] = None
