"""Translation tools using Azure Translator service.

This module provides AI functions for language detection and translation
using Azure Translator. These tools are used by the Language Agent (Post-MVP)
to support multilingual interactions.

The tools gracefully handle missing configuration by defaulting to English
and returning original text when translation is not available.
"""

from typing import Annotated
from pydantic import Field
from agent_framework import ai_function
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# Azure Translator configuration from environment variables
endpoint = os.getenv("TRANSLATOR_ENDPOINT")
key = os.getenv("TRANSLATOR_KEY")
region = os.getenv("TRANSLATOR_REGION", "eastus")

@ai_function(
    name="detect_language",
    description="Detects the language of the input text using Azure Translator"
)
async def detect_language(
    text: Annotated[str, Field(description="The text to analyze")],
) -> str:
    """Detect the language of input text using Azure Translator.
    
    This function uses Azure Translator's language detection API to identify
    the language of the input text. It returns a two-letter language code
    (e.g., 'en', 'es', 'fr').
    
    Args:
        text: The text to analyze for language detection
    
    Returns:
        Two-letter language code (e.g., 'en', 'es'). Defaults to 'en' if:
        - Azure Translator is not configured
        - API call fails
        - Language cannot be detected
    
    Example:
        >>> lang = await detect_language("Hello, how are you?")
        >>> print(lang)  # 'en'
        >>> lang = await detect_language("Hola, ¿cómo estás?")
        >>> print(lang)  # 'es'
    """
    # Explicitly check for None so static type checkers can narrow the type.
    if endpoint is None or key is None:
        return "en"  # Default to English if not configured

    # Also guard against empty strings (preserve previous behavior).
    if not endpoint or not key:
        return "en"

    # Now `endpoint` is a non-empty string; normalize trailing slash.
    endpoint_normalized = endpoint.rstrip('/')
    url = f"{endpoint_normalized}/detect?api-version=3.0"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=[{"text": text}], timeout=10.0)
            resp.raise_for_status()
            result = resp.json()
            if result and isinstance(result, list) and "language" in result[0]:
                return result[0]["language"].split("-")[0]
    except Exception as e:
        # Silent fail for production
        pass
    
    return "en"  # Default to English on error

@ai_function(
    name="translate_text",
    description="Translates text between languages using Azure Translator"
)
async def translate_text(
    text: str,
    target_language: Annotated[str, Field(description="Target language code (e.g., 'es', 'en')")],
    source_language: Annotated[str, Field(description="Source language code (e.g., 'es', 'en')", default="auto")] = "auto"
) -> str:
    """Translate text to the target language using Azure Translator.
    
    This function uses Azure Translator's translation API to convert text
    from one language to another. It supports automatic source language
    detection when source_language is set to "auto".
    
    Args:
        text: The text to translate
        target_language: Target language code (e.g., 'es', 'en', 'fr')
        source_language: Source language code or 'auto' for automatic detection
    
    Returns:
        Translated text in the target language. Returns original text if:
        - Azure Translator is not configured
        - API call fails
        - Source and target languages are the same
        - Text is empty
    
    Example:
        >>> translated = await translate_text(
        ...     "Hello, how are you?",
        ...     target_language="es",
        ...     source_language="en"
        ... )
        >>> print(translated)  # "Hola, ¿cómo estás?"
    """
    if not text or source_language == target_language:
        return text

    # Explicitly check for None so static type checkers can narrow the type.
    if endpoint is None or key is None:
        return text  # Return original text if not configured

    if not endpoint or not key:
        return text

    endpoint_normalized = endpoint.rstrip('/')
    url = f"{endpoint_normalized}/translate?api-version=3.0&to={target_language}"
    if source_language != "auto":
        url += f"&from={source_language}"

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=[{"text": text}], timeout=10.0)
            resp.raise_for_status()
            result = resp.json()
            if result and isinstance(result, list) and "translations" in result[0]:
                return result[0]["translations"][0]["text"]
    except Exception as e:
        # Silent fail for production
        pass

    return text
