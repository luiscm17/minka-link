"""Intent classification models for the Router Agent.

This module defines the data structures used for classifying user intents
and routing queries to appropriate specialist agents.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class IntentType(Enum):
    """Enumeration of possible user intent types.
    
    The Router Agent classifies all user queries into one of these intent types
    to determine the appropriate handling strategy.
    
    Attributes:
        CIVIC_EDUCATION: Questions about government, voting, civic processes
        MULTILINGUAL_INPUT: Queries requiring translation or language detection
        PROHIBITED_QUERY: Requests for voting recommendations or political opinions
        UNKNOWN: Ambiguous queries that require clarification
    """
    CIVIC_EDUCATION = "civic_education"
    MULTILINGUAL_INPUT = "multilingual_input"
    PROHIBITED_QUERY = "prohibited_query"
    UNKNOWN = "unknown"


@dataclass
class IntentClassification:
    """Model for intent classification results.
    
    This data class encapsulates the result of intent classification,
    including the classified intent type, confidence score, and reasoning.
    
    Attributes:
        intent: The classified intent type
        confidence: Confidence score between 0.0 and 1.0
        reasoning: Optional explanation of the classification decision
    
    Example:
        >>> classification = IntentClassification(
        ...     intent=IntentType.CIVIC_EDUCATION,
        ...     confidence=1.0,
        ...     reasoning="Matched deterministic pattern: voting requirements"
        ... )
    """
    intent: IntentType
    confidence: float
    reasoning: Optional[str] = None
