"""Retry logic with exponential backoff for external service failures."""

import asyncio
import logging
from typing import TypeVar, Callable, Any, Optional, List
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry logic with exponential backoff.
    
    This configuration implements the retry strategy specified in the design document:
    - Maximum of 3 retry attempts
    - Exponential backoff starting at 100ms
    - Maximum backoff of 5 seconds
    - Backoff multiplier of 2
    
    Validates: Requirements 9.1
    """
    MAX_RETRIES: int = 3
    INITIAL_BACKOFF_MS: int = 100
    MAX_BACKOFF_MS: int = 5000
    BACKOFF_MULTIPLIER: float = 2.0
    
    # Error types that should trigger retries
    RETRYABLE_ERRORS: List[str] = None
    
    def __post_init__(self):
        """Initialize default retryable errors if not provided."""
        if self.RETRYABLE_ERRORS is None:
            self.RETRYABLE_ERRORS = [
                "RateLimitExceeded",
                "RateLimitError",
                "ServiceUnavailable",
                "Timeout",
                "NetworkError",
                "ConnectionError",
                "TooManyRequests",
                "429",  # HTTP status code for rate limiting
                "503",  # HTTP status code for service unavailable
                "504",  # HTTP status code for gateway timeout
            ]


def is_retryable_error(error: Exception, config: RetryConfig) -> bool:
    """Check if an error is retryable based on configuration.
    
    Args:
        error: The exception to check
        config: Retry configuration with retryable error types
    
    Returns:
        True if the error should trigger a retry, False otherwise
    """
    error_str = str(error)
    error_type = type(error).__name__
    
    # Check if error type or message contains any retryable error pattern
    for retryable in config.RETRYABLE_ERRORS:
        if retryable.lower() in error_type.lower() or retryable.lower() in error_str.lower():
            return True
    
    return False


def calculate_backoff(attempt: int, config: RetryConfig) -> float:
    """Calculate backoff delay for a given attempt using exponential backoff.
    
    Formula: min(INITIAL_BACKOFF * (MULTIPLIER ^ attempt), MAX_BACKOFF)
    
    Args:
        attempt: The current attempt number (0-indexed)
        config: Retry configuration
    
    Returns:
        Backoff delay in seconds
    """
    backoff_ms = min(
        config.INITIAL_BACKOFF_MS * (config.BACKOFF_MULTIPLIER ** attempt),
        config.MAX_BACKOFF_MS
    )
    return backoff_ms / 1000.0  # Convert to seconds


async def retry_with_backoff(
    func: Callable[..., Any],
    *args,
    config: Optional[RetryConfig] = None,
    operation_name: str = "operation",
    **kwargs
) -> Any:
    """Execute a function with retry logic and exponential backoff.
    
    This function implements the retry strategy for external service calls:
    1. Attempt the operation
    2. If it fails with a retryable error, wait with exponential backoff
    3. Retry up to MAX_RETRIES times
    4. If all retries fail, raise the last exception
    
    Args:
        func: The async function to execute
        *args: Positional arguments for the function
        config: Retry configuration (uses default if not provided)
        operation_name: Name of the operation for logging
        **kwargs: Keyword arguments for the function
    
    Returns:
        The result of the function call
    
    Raises:
        The last exception if all retries fail
    
    Validates: Requirements 9.1
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.MAX_RETRIES + 1):  # +1 for initial attempt
        try:
            logger.info(
                f"Attempting {operation_name}",
                extra={
                    "attempt": attempt + 1,
                    "max_attempts": config.MAX_RETRIES + 1
                }
            )
            
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Success!
            if attempt > 0:
                logger.info(
                    f"{operation_name} succeeded after retry",
                    extra={
                        "attempt": attempt + 1,
                        "total_attempts": attempt + 1
                    }
                )
            
            return result
            
        except Exception as e:
            last_exception = e
            
            # Check if this is the last attempt
            if attempt >= config.MAX_RETRIES:
                logger.error(
                    f"{operation_name} failed after all retries",
                    extra={
                        "total_attempts": attempt + 1,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )
                raise
            
            # Check if error is retryable
            if not is_retryable_error(e, config):
                logger.warning(
                    f"{operation_name} failed with non-retryable error",
                    extra={
                        "attempt": attempt + 1,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )
                raise
            
            # Calculate backoff delay
            backoff_seconds = calculate_backoff(attempt, config)
            
            logger.warning(
                f"{operation_name} failed, retrying after backoff",
                extra={
                    "attempt": attempt + 1,
                    "max_attempts": config.MAX_RETRIES + 1,
                    "backoff_seconds": backoff_seconds,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            
            # Wait before retrying
            await asyncio.sleep(backoff_seconds)
    
    # This should never be reached, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError(f"{operation_name} failed with unknown error")


def with_retry(
    config: Optional[RetryConfig] = None,
    operation_name: Optional[str] = None
):
    """Decorator to add retry logic with exponential backoff to async functions.
    
    Usage:
        @with_retry(config=RetryConfig(MAX_RETRIES=5), operation_name="my_operation")
        async def my_function():
            # ... code that might fail ...
            pass
    
    Args:
        config: Retry configuration (uses default if not provided)
        operation_name: Name of the operation for logging (uses function name if not provided)
    
    Returns:
        Decorated function with retry logic
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            return await retry_with_backoff(
                func,
                *args,
                config=config,
                operation_name=op_name,
                **kwargs
            )
        return wrapper
    return decorator
