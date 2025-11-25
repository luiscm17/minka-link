from enum import Enum
from dataclasses import dataclass
from typing import Optional


class IntentType(Enum):
    """Enumeration of possible user intent types."""
    CIVIC_EDUCATION = "civic_education"
    MULTILINGUAL_INPUT = "multilingual_input"
    PROHIBITED_QUERY = "prohibited_query"
    UNKNOWN = "unknown"


@dataclass
class IntentClassification:
    """Model for intent classification results."""
    intent: IntentType
    confidence: float
    reasoning: Optional[str] = None
