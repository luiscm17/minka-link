from typing import Annotated
from pydantic import Field
from agent_framework import ai_function
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

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
    """Detect the language of input text using Azure Translator."""
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
        print(f"Error detecting language: {e}")
    
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
    """Translate text to the target language using Azure Translator."""
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
        print(f"Error translating text: {e}")

    return text
