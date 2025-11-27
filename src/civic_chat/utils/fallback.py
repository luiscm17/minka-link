"""Fallback mechanisms for graceful degradation when services fail."""

import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ResponseCache:
    """Simple in-memory cache for responses to enable fallback when search fails.
    
    This cache stores recent successful responses and can be used as a fallback
    when the knowledge base or search service is unavailable.
    
    Validates: Requirements 9.2
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        """Initialize the response cache.
        
        Args:
            ttl_seconds: Time-to-live for cached responses in seconds (default: 1 hour)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[str]:
        """Get a cached response if it exists and hasn't expired.
        
        Args:
            key: Cache key (typically a normalized query)
        
        Returns:
            Cached response text if available and not expired, None otherwise
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        timestamp = entry.get("timestamp")
        
        # Check if entry has expired
        if timestamp:
            age = datetime.utcnow() - timestamp
            if age.total_seconds() > self._ttl_seconds:
                logger.info(
                    "Cache entry expired",
                    extra={
                        "key": key[:50],
                        "age_seconds": age.total_seconds(),
                        "ttl_seconds": self._ttl_seconds
                    }
                )
                del self._cache[key]
                return None
        
        logger.info(
            "Cache hit",
            extra={"key": key[:50]}
        )
        
        return entry.get("response")
    
    def set(self, key: str, response: str) -> None:
        """Store a response in the cache.
        
        Args:
            key: Cache key (typically a normalized query)
            response: Response text to cache
        """
        self._cache[key] = {
            "response": response,
            "timestamp": datetime.utcnow()
        }
        
        logger.info(
            "Response cached",
            extra={
                "key": key[:50],
                "response_length": len(response)
            }
        )
    
    def clear(self) -> None:
        """Clear all cached responses."""
        count = len(self._cache)
        self._cache.clear()
        
        logger.info(
            "Cache cleared",
            extra={"entries_removed": count}
        )
    
    def normalize_key(self, query: str, language: str = "en") -> str:
        """Normalize a query into a cache key.
        
        This method creates a consistent cache key by:
        - Converting to lowercase
        - Removing extra whitespace
        - Including language code
        
        Args:
            query: The user query
            language: Language code
        
        Returns:
            Normalized cache key
        """
        normalized = " ".join(query.lower().strip().split())
        return f"{language}:{normalized}"


# Global response cache instance
_response_cache = ResponseCache()


def get_response_cache() -> ResponseCache:
    """Get the global response cache instance.
    
    Returns:
        The global ResponseCache instance
    """
    return _response_cache


async def with_translation_fallback(
    translate_func: Callable,
    text: str,
    target_language: str,
    source_language: str = "auto"
) -> str:
    """Execute translation with fallback to English on failure.
    
    This function implements the fallback strategy for translation:
    1. Attempt translation
    2. If translation fails, return original text (fallback to English)
    3. Log the failure for monitoring
    
    Args:
        translate_func: The translation function to call
        text: Text to translate
        target_language: Target language code
        source_language: Source language code
    
    Returns:
        Translated text, or original text if translation fails
    
    Validates: Requirements 9.2
    """
    try:
        result = await translate_func(text, target_language, source_language)
        return result
    except Exception as e:
        logger.warning(
            "Translation failed, falling back to original text",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "target_language": target_language,
                "text_length": len(text)
            }
        )
        return text


async def with_search_fallback(
    search_func: Callable,
    query: str,
    language: str = "en",
    cache: Optional[ResponseCache] = None
) -> str:
    """Execute search with fallback to cached response on failure.
    
    This function implements the fallback strategy for knowledge base search:
    1. Attempt search
    2. If search fails, try to use cached response
    3. If no cache available, return helpful error message
    
    Args:
        search_func: The search function to call
        query: Search query
        language: Language code
        cache: Response cache (uses global cache if not provided)
    
    Returns:
        Search results, cached response, or error message
    
    Validates: Requirements 9.2
    """
    if cache is None:
        cache = get_response_cache()
    
    try:
        result = await search_func(query, language)
        
        # Cache successful result
        cache_key = cache.normalize_key(query, language)
        cache.set(cache_key, result)
        
        return result
    except Exception as e:
        logger.warning(
            "Search failed, attempting cache fallback",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "query": query[:100],
                "language": language
            }
        )
        
        # Try to get cached response
        cache_key = cache.normalize_key(query, language)
        cached_response = cache.get(cache_key)
        
        if cached_response:
            logger.info(
                "Using cached response as fallback",
                extra={
                    "query": query[:100],
                    "language": language
                }
            )
            return cached_response
        
        # No cache available, return error message
        logger.error(
            "Search failed and no cache available",
            extra={
                "error": str(e),
                "query": query[:100],
                "language": language
            }
        )
        
        return get_search_failure_message(language)


async def with_generation_fallback(
    generate_func: Callable,
    *args,
    language: str = "en",
    **kwargs
) -> str:
    """Execute generation with fallback to generic response on failure.
    
    This function implements the fallback strategy for LLM generation:
    1. Attempt generation
    2. If generation fails, return generic neutral response
    3. Log the failure for monitoring
    
    Args:
        generate_func: The generation function to call
        *args: Positional arguments for the function
        language: Language code for fallback message
        **kwargs: Keyword arguments for the function
    
    Returns:
        Generated response or generic fallback response
    
    Validates: Requirements 9.2
    """
    try:
        result = await generate_func(*args, **kwargs)
        return result
    except Exception as e:
        logger.error(
            "Generation failed, using generic fallback response",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "language": language
            }
        )
        
        return get_generic_fallback_response(language)


def get_search_failure_message(language: str = "en") -> str:
    """Get error message for search failures.
    
    Args:
        language: Language code
    
    Returns:
        User-friendly error message in the specified language
    """
    messages = {
        "en": (
            "I'm currently unable to search my knowledge base. "
            "Please try again in a moment, or visit these official resources:\n\n"
            "- USA.gov: https://www.usa.gov\n"
            "- Vote.gov: https://vote.gov\n"
            "- Congress.gov: https://www.congress.gov"
        ),
        "es": (
            "Actualmente no puedo buscar en mi base de conocimientos. "
            "Por favor intente nuevamente en un momento, o visite estos recursos oficiales:\n\n"
            "- USA.gov en español: https://www.usa.gov/espanol\n"
            "- Vote.gov: https://vote.gov\n"
            "- Congress.gov: https://www.congress.gov"
        )
    }
    
    return messages.get(language, messages["en"])


def get_generic_fallback_response(language: str = "en") -> str:
    """Get generic fallback response when generation fails.
    
    Args:
        language: Language code
    
    Returns:
        Generic neutral response in the specified language
    """
    responses = {
        "en": (
            "I apologize, but I'm experiencing technical difficulties. "
            "For reliable civic information, please visit:\n\n"
            "- USA.gov: https://www.usa.gov\n"
            "- Vote.gov: https://vote.gov\n"
            "- Your local election office\n\n"
            "Please try again shortly."
        ),
        "es": (
            "Disculpe, pero estoy experimentando dificultades técnicas. "
            "Para información cívica confiable, por favor visite:\n\n"
            "- USA.gov en español: https://www.usa.gov/espanol\n"
            "- Vote.gov: https://vote.gov\n"
            "- Su oficina electoral local\n\n"
            "Por favor intente nuevamente en breve."
        )
    }
    
    return responses.get(language, responses["en"])
