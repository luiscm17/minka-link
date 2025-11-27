# Civic Chat Utilities

This directory contains utility modules for comprehensive error handling, retry logic, fallback mechanisms, and clarification handling.

## Modules

### `retry.py` - Retry Logic with Exponential Backoff

Implements retry logic for external service failures with exponential backoff.

**Key Components:**
- `RetryConfig`: Configuration for retry behavior (max retries, backoff settings)
- `retry_with_backoff()`: Execute functions with automatic retry
- `@with_retry`: Decorator for adding retry logic to async functions

**Example Usage:**

```python
from civic_chat.utils.retry import retry_with_backoff, RetryConfig, with_retry

# Using the function directly
config = RetryConfig(MAX_RETRIES=3)
result = await retry_with_backoff(
    some_api_call,
    arg1, arg2,
    config=config,
    operation_name="API call"
)

# Using the decorator
@with_retry(config=RetryConfig(MAX_RETRIES=5), operation_name="translation")
async def translate_with_retry(text, target_lang):
    return await translator.translate(text, target_lang)
```

**Validates:** Requirements 9.1

---

### `fallback.py` - Fallback Mechanisms

Implements graceful degradation when services fail.

**Key Components:**
- `ResponseCache`: In-memory cache for responses
- `with_translation_fallback()`: Translation with fallback to original text
- `with_search_fallback()`: Search with fallback to cached responses
- `with_generation_fallback()`: Generation with fallback to generic response

**Example Usage:**

```python
from civic_chat.utils.fallback import (
    with_translation_fallback,
    with_search_fallback,
    get_response_cache
)

# Translation with fallback
translated = await with_translation_fallback(
    translate_func,
    text="Hello",
    target_language="es"
)

# Search with cache fallback
cache = get_response_cache()
result = await with_search_fallback(
    search_func,
    query="voting requirements",
    language="en",
    cache=cache
)
```

**Validates:** Requirements 9.2

---

### `error_handler.py` - Error Response Models

Creates standardized, user-friendly error responses.

**Key Components:**
- `create_error_response()`: Generic error response creator
- `create_rate_limit_error()`: Rate limit error
- `create_service_unavailable_error()`: Service unavailable error
- `create_translation_error()`: Translation failure error
- `create_validation_error()`: Validation failure error
- `create_no_results_error()`: No search results error
- `create_ambiguous_query_error()`: Ambiguous query error
- `create_prohibited_query_response()`: Prohibited query response
- `format_error_for_user()`: Format error for display

**Example Usage:**

```python
from civic_chat.utils.error_handler import (
    create_rate_limit_error,
    format_error_for_user
)

# Create error response
error = create_rate_limit_error(retry_after_seconds=60)

# Format for user display
message = format_error_for_user(error)
print(message)
```

**Validates:** Requirements 11.4

---

### `clarification.py` - Clarification Handling

Handles ambiguous queries by requesting clarification from users.

**Key Components:**
- `needs_clarification()`: Check if classification needs clarification
- `create_clarification_response()`: Create clarification request
- `get_clarification_examples()`: Get example queries
- `format_clarification_message()`: Format clarification message

**Example Usage:**

```python
from civic_chat.utils.clarification import (
    needs_clarification,
    create_clarification_response
)

# Check if clarification is needed
classification = await router.classify_intent(query)
if needs_clarification(classification, threshold=0.6):
    # Create clarification response
    response = create_clarification_response(
        classification,
        language="en"
    )
    return format_error_for_user(response)
```

**Validates:** Requirements 9.4

---

## Integration Example

Here's how these utilities work together in the workflow:

```python
from civic_chat.utils.retry import retry_with_backoff, RetryConfig
from civic_chat.utils.fallback import with_search_fallback
from civic_chat.utils.error_handler import (
    create_rate_limit_error,
    create_service_unavailable_error,
    format_error_for_user
)
from civic_chat.utils.clarification import (
    needs_clarification,
    create_clarification_response
)

async def process_query(query: str, language: str = "en"):
    """Process a user query with comprehensive error handling."""
    
    # Step 1: Classify intent with retry
    try:
        classification = await retry_with_backoff(
            router.classify_intent,
            query,
            config=RetryConfig(MAX_RETRIES=3),
            operation_name="intent_classification"
        )
    except Exception as e:
        if "RateLimitExceeded" in str(e):
            error = create_rate_limit_error()
            return format_error_for_user(error)
        else:
            error = create_service_unavailable_error("classification service")
            return format_error_for_user(error)
    
    # Step 2: Check if clarification is needed
    if needs_clarification(classification, threshold=0.6):
        response = create_clarification_response(classification, language)
        return format_error_for_user(response)
    
    # Step 3: Search with fallback to cache
    try:
        result = await with_search_fallback(
            civic_knowledge_agent.search_civic_knowledge,
            query=query,
            language=language
        )
        return result
    except Exception as e:
        error = create_service_unavailable_error("knowledge base")
        return format_error_for_user(error)
```

---

## Configuration

### Retry Configuration

Default retry settings (can be customized):
- `MAX_RETRIES`: 3
- `INITIAL_BACKOFF_MS`: 100
- `MAX_BACKOFF_MS`: 5000
- `BACKOFF_MULTIPLIER`: 2.0

### Cache Configuration

Default cache settings:
- `TTL_SECONDS`: 3600 (1 hour)

### Clarification Threshold

Default confidence threshold for clarification:
- `CONFIDENCE_THRESHOLD`: 0.6

---

## Testing

All utilities include comprehensive logging for monitoring and debugging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Run your code with detailed logs
result = await retry_with_backoff(...)
```

---

## Requirements Validation

This implementation validates the following requirements:

- **9.1**: Retry logic with exponential backoff for Azure OpenAI rate limits
- **9.2**: Fallback mechanisms (translation, search, generation)
- **9.3**: No search results handling (via error_handler)
- **9.4**: Clarification requests for ambiguous queries
- **9.5**: Prohibited query handling (via error_handler)
- **11.4**: ErrorResponse model usage for all errors
