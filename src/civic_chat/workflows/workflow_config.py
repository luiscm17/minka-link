"""
Configuration constants for the multi-agent workflow.

This module contains configuration settings for the HandoffBuilder workflow,
including agent names, handoff relationships, and termination conditions.
"""

# Agent names
ROUTER_AGENT_NAME = "RouterAgent"
CIVIC_KNOWLEDGE_AGENT_NAME = "CivicKnowledgeAgent"
LANGUAGE_AGENT_NAME = "LanguageAgent"
OUTPUT_VALIDATOR_AGENT_NAME = "OutputValidatorAgent"

# Workflow configuration
WORKFLOW_NAME = "civic_chat_workflow"

# Azure OpenAI configuration
DEFAULT_API_VERSION = "2023-05-15"
DEFAULT_MODEL = "gpt-4o-mini"

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF_MS = 100
MAX_BACKOFF_MS = 5000
BACKOFF_MULTIPLIER = 2

RETRYABLE_ERRORS = [
    "RateLimitExceeded",
    "ServiceUnavailable",
    "Timeout",
    "NetworkError"
]

# Validation configuration
MAX_REGENERATION_ATTEMPTS = 2
NEUTRALITY_VIOLATION_THRESHOLD = 5

# Bias keywords for neutrality validation
BIAS_KEYWORDS = [
    "should vote for",
    "best candidate",
    "better party",
    "more trustworthy",
    "superior policy",
    "recommend voting",
    "vote for",
    "support this candidate"
]
