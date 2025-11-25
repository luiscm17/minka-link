from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ErrorResponse:
    """Model for error responses."""
    error_code: str
    error_message: str
    user_message: str
    retry_after_seconds: Optional[int] = None
    suggested_actions: Optional[List[str]] = None
    correlation_id: Optional[str] = None
