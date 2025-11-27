"""Error handling utilities for creating user-friendly error responses."""

import logging
import uuid
from typing import Optional, List
from datetime import datetime

try:
    from ..models.error import ErrorResponse
except ImportError:
    from civic_chat.models.error import ErrorResponse

logger = logging.getLogger(__name__)


def create_error_response(
    error_code: str,
    error_message: str,
    user_message: str,
    retry_after_seconds: Optional[int] = None,
    suggested_actions: Optional[List[str]] = None,
    correlation_id: Optional[str] = None
) -> ErrorResponse:
    """Create a standardized error response.
    
    This function ensures all errors use the ErrorResponse model
    with consistent formatting and helpful information.
    
    Args:
        error_code: Machine-readable error code (e.g., "RATE_LIMIT_EXCEEDED")
        error_message: Technical error message for logging
        user_message: User-friendly error message
        retry_after_seconds: Optional seconds to wait before retrying
        suggested_actions: Optional list of suggested actions for the user
        correlation_id: Optional correlation ID for tracking (generated if not provided)
    
    Returns:
        ErrorResponse object
    
    Validates: Requirements 11.4
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    
    # Log the error with correlation ID
    logger.error(
        f"Error response created: {error_code}",
        extra={
            "error_code": error_code,
            "error_message": error_message,
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    return ErrorResponse(
        error_code=error_code,
        error_message=error_message,
        user_message=user_message,
        retry_after_seconds=retry_after_seconds,
        suggested_actions=suggested_actions,
        correlation_id=correlation_id
    )


def create_rate_limit_error(
    retry_after_seconds: int = 60,
    correlation_id: Optional[str] = None
) -> ErrorResponse:
    """Create an error response for rate limit exceeded.
    
    Args:
        retry_after_seconds: Seconds to wait before retrying
        correlation_id: Optional correlation ID
    
    Returns:
        ErrorResponse for rate limit error
    """
    return create_error_response(
        error_code="RATE_LIMIT_EXCEEDED",
        error_message="Azure OpenAI rate limit exceeded",
        user_message=(
            "I'm currently experiencing high demand. "
            f"Please try again in {retry_after_seconds} seconds."
        ),
        retry_after_seconds=retry_after_seconds,
        suggested_actions=[
            "Wait a moment and try again",
            "Rephrase your question if it's complex",
            "Visit https://www.usa.gov for immediate information"
        ],
        correlation_id=correlation_id
    )


def create_service_unavailable_error(
    service_name: str = "service",
    correlation_id: Optional[str] = None
) -> ErrorResponse:
    """Create an error response for service unavailable.
    
    Args:
        service_name: Name of the unavailable service
        correlation_id: Optional correlation ID
    
    Returns:
        ErrorResponse for service unavailable error
    """
    return create_error_response(
        error_code="SERVICE_UNAVAILABLE",
        error_message=f"{service_name} is currently unavailable",
        user_message=(
            "I'm having trouble connecting to my knowledge base. "
            "Please try again in a moment."
        ),
        retry_after_seconds=30,
        suggested_actions=[
            "Try again in a few moments",
            "Visit https://www.usa.gov for official information",
            "Contact your local election office for specific questions"
        ],
        correlation_id=correlation_id
    )


def create_translation_error(
    target_language: str,
    correlation_id: Optional[str] = None
) -> ErrorResponse:
    """Create an error response for translation failure.
    
    Args:
        target_language: The target language that failed
        correlation_id: Optional correlation ID
    
    Returns:
        ErrorResponse for translation error
    """
    return create_error_response(
        error_code="TRANSLATION_FAILED",
        error_message=f"Translation to {target_language} failed",
        user_message=(
            "I'm having trouble translating your request. "
            "I'll respond in English for now."
        ),
        suggested_actions=[
            "Continue in English",
            "Try rephrasing your question",
            "Visit https://www.usa.gov/espanol for Spanish resources"
        ],
        correlation_id=correlation_id
    )


def create_validation_error(
    reason: str,
    correlation_id: Optional[str] = None
) -> ErrorResponse:
    """Create an error response for validation failure.
    
    Args:
        reason: Reason for validation failure
        correlation_id: Optional correlation ID
    
    Returns:
        ErrorResponse for validation error
    """
    return create_error_response(
        error_code="VALIDATION_FAILED",
        error_message=f"Response validation failed: {reason}",
        user_message=(
            "I'm unable to provide a response that meets our neutrality standards. "
            "Let me try to help you differently."
        ),
        suggested_actions=[
            "Rephrase your question to focus on factual information",
            "Ask about government processes or civic procedures",
            "Visit https://www.usa.gov for comprehensive information"
        ],
        correlation_id=correlation_id
    )


def create_no_results_error(
    query: str,
    language: str = "en",
    correlation_id: Optional[str] = None
) -> ErrorResponse:
    """Create an error response for no search results.
    
    Args:
        query: The search query that returned no results
        language: Language code
        correlation_id: Optional correlation ID
    
    Returns:
        ErrorResponse for no results
    """
    if language == "es":
        user_message = (
            "No encontré información específica sobre ese tema. "
            "Sin embargo, puedo ayudarte con información general sobre gobierno y procesos cívicos."
        )
        suggested_actions = [
            "Reformula tu pregunta",
            "Pregunta sobre procesos gubernamentales generales",
            "Visita https://www.usa.gov/espanol para información oficial"
        ]
    else:
        user_message = (
            "I don't have specific information on that topic. "
            "However, I can help with general government and civic process information."
        )
        suggested_actions = [
            "Rephrase your question",
            "Ask about general government processes",
            "Visit https://www.usa.gov for official information"
        ]
    
    return create_error_response(
        error_code="NO_RESULTS_FOUND",
        error_message=f"No knowledge base results for query: {query[:100]}",
        user_message=user_message,
        suggested_actions=suggested_actions,
        correlation_id=correlation_id
    )


def create_ambiguous_query_error(
    language: str = "en",
    correlation_id: Optional[str] = None
) -> ErrorResponse:
    """Create an error response for ambiguous queries.
    
    Args:
        language: Language code
        correlation_id: Optional correlation ID
    
    Returns:
        ErrorResponse for ambiguous query
    """
    if language == "es":
        user_message = (
            "No estoy seguro de cómo ayudarte con esa pregunta. "
            "¿Podrías ser más específico?"
        )
        suggested_actions = [
            "Proporciona más detalles sobre lo que quieres saber",
            "Pregunta sobre un tema específico del gobierno",
            "Ejemplos: '¿Cómo me registro para votar?' o '¿Qué hace el Congreso?'"
        ]
    else:
        user_message = (
            "I'm not sure how to help with that question. "
            "Could you be more specific?"
        )
        suggested_actions = [
            "Provide more details about what you want to know",
            "Ask about a specific government topic",
            "Examples: 'How do I register to vote?' or 'What does Congress do?'"
        ]
    
    return create_error_response(
        error_code="AMBIGUOUS_QUERY",
        error_message="Query classification confidence too low",
        user_message=user_message,
        suggested_actions=suggested_actions,
        correlation_id=correlation_id
    )


def create_prohibited_query_response(
    language: str = "en",
    correlation_id: Optional[str] = None
) -> ErrorResponse:
    """Create a response for prohibited queries (not technically an error).
    
    Args:
        language: Language code
        correlation_id: Optional correlation ID
    
    Returns:
        ErrorResponse explaining system limitations
    """
    if language == "es":
        user_message = (
            "Estoy diseñado para proporcionar información cívica neutral. "
            "No puedo hacer recomendaciones de voto ni expresar opiniones políticas. "
            "Sin embargo, puedo ayudarte a entender:\n"
            "- Cómo funciona el gobierno\n"
            "- Requisitos y registro para votar\n"
            "- Fechas y procesos electorales\n"
            "- Los roles y responsabilidades de tus representantes"
        )
        suggested_actions = [
            "Pregunta sobre procesos gubernamentales",
            "Pregunta sobre requisitos para votar",
            "Pregunta sobre cómo encontrar a tus representantes"
        ]
    else:
        user_message = (
            "I'm designed to provide neutral civic education information. "
            "I cannot make voting recommendations or express political opinions. "
            "However, I can help you understand:\n"
            "- How government works\n"
            "- Voting requirements and registration\n"
            "- Election dates and processes\n"
            "- Your representatives' roles and responsibilities"
        )
        suggested_actions = [
            "Ask about government processes",
            "Ask about voting requirements",
            "Ask about finding your representatives"
        ]
    
    return create_error_response(
        error_code="PROHIBITED_QUERY",
        error_message="Query classified as prohibited (voting recommendation request)",
        user_message=user_message,
        suggested_actions=suggested_actions,
        correlation_id=correlation_id
    )


def format_error_for_user(error_response: ErrorResponse) -> str:
    """Format an ErrorResponse for display to the user.
    
    This function converts an ErrorResponse object into a user-friendly
    string that can be displayed in the chat interface.
    
    Args:
        error_response: The ErrorResponse to format
    
    Returns:
        Formatted error message string
    """
    parts = [error_response.user_message]
    
    if error_response.retry_after_seconds:
        parts.append(f"\nPlease try again in {error_response.retry_after_seconds} seconds.")
    
    if error_response.suggested_actions:
        parts.append("\n\nSuggested actions:")
        for action in error_response.suggested_actions:
            parts.append(f"- {action}")
    
    if error_response.correlation_id:
        parts.append(f"\n\nReference ID: {error_response.correlation_id}")
    
    return "\n".join(parts)
