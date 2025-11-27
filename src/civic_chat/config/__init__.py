"""Configuration package for Civic Chat application."""

from .settings import (
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
    
    # Bing Search
    BING_CONNECTION_ID,
    
    # Azure Translator
    TRANSLATOR_ENDPOINT,
    TRANSLATOR_KEY,
    TRANSLATOR_REGION,
    
    # Azure Content Safety
    CONTENT_SAFETY_ENDPOINT,
    CONTENT_SAFETY_KEY,
    
    # Logging
    ENABLE_JSON_LOGGING,
    LOG_FILE,
    
    # Validation
    validate_config,
)

__all__ = [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME",
    "BING_CONNECTION_ID",
    "TRANSLATOR_ENDPOINT",
    "TRANSLATOR_KEY",
    "TRANSLATOR_REGION",
    "CONTENT_SAFETY_ENDPOINT",
    "CONTENT_SAFETY_KEY",
    "ENABLE_JSON_LOGGING",
    "LOG_FILE",
    "validate_config",
]
