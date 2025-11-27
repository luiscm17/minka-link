import os
import logging
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

setting_dir  = Path(__file__).parent
ENV_FILE = setting_dir.parent / ".env"

# Load environment variables from .env file
load_dotenv(ENV_FILE)

logger = logging.getLogger(__name__)

# Azure AI Foundry configuration
AZURE_AI_PROJECT_ENDPOINT: str = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
AZURE_AI_MODEL_DEPLOYMENT_NAME: str = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")

# Azure OpenAI configuration (Legacy)
AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

# Bing Search configuration
BING_CONNECTION_ID: Optional[str] = os.getenv("BING_CONNECTION_ID")

# Azure Translator configuration
TRANSLATOR_ENDPOINT: Optional[str] = os.getenv("TRANSLATOR_ENDPOINT")
TRANSLATOR_KEY: Optional[str] = os.getenv("TRANSLATOR_KEY")
TRANSLATOR_REGION: str = os.getenv("TRANSLATOR_REGION", "eastus")

# Azure Content Safety configuration
CONTENT_SAFETY_ENDPOINT: Optional[str] = os.getenv("CONTENT_SAFETY_ENDPOINT")
CONTENT_SAFETY_KEY: Optional[str] = os.getenv("CONTENT_SAFETY_KEY")

# Logging configuration
ENABLE_JSON_LOGGING: bool = os.getenv("ENABLE_JSON_LOGGING", "false").lower() == "true"
LOG_FILE: Optional[str] = os.getenv("LOG_FILE")


def validate_config() -> None:
    """Validate required configuration is present.
    
    Raises:
        ValueError: If required configuration is missing
    """
    if not AZURE_AI_PROJECT_ENDPOINT:
        raise ValueError(
            "AZURE_AI_PROJECT_ENDPOINT environment variable is required. "
            "Please set it in your .env file or environment."
        )
    
    if not AZURE_AI_MODEL_DEPLOYMENT_NAME:
        raise ValueError(
            "AZURE_AI_MODEL_DEPLOYMENT_NAME environment variable is required. "
            "Please set it in your .env file or environment."
        )
    
    logger.info("Configuration validated successfully")
    
    # Log optional features
    if BING_CONNECTION_ID:
        logger.info("Bing Search configured")
    else:
        logger.info("Bing Search not configured - using fallback tools")
    
    if CONTENT_SAFETY_ENDPOINT and CONTENT_SAFETY_KEY:
        logger.info("Azure Content Safety configured")
    else:
        logger.info("Azure Content Safety not configured")
    
    if TRANSLATOR_ENDPOINT and TRANSLATOR_KEY:
        logger.info("Azure Translator configured")
    else:
        logger.info("Azure Translator not configured")
