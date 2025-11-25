from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CivicChatResponse:
    """Model for civic chat responses."""
    text: str
    sources: List[str]
    language: str
    agent_name: str
    confidence: float
    neutrality_score: float
    processing_time_ms: int
    token_usage: Dict[str, Any]
