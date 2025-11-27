"""Response models for civic chat interactions.

This module defines the data structures used for representing
responses from the civic chat system, including metadata about
the response generation process.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CivicChatResponse:
    """Model for civic chat responses with metadata.
    
    This data class encapsulates a complete response from the civic chat system,
    including the response text, source citations, language, and metadata about
    the generation process.
    
    Attributes:
        text: The response text content
        sources: List of official source URLs cited in the response
        language: Language code of the response (e.g., 'en', 'es')
        agent_name: Name of the agent that generated the response
        confidence: Confidence score of the response (0.0 to 1.0)
        neutrality_score: Neutrality validation score (0.0 to 1.0)
        processing_time_ms: Total processing time in milliseconds
        token_usage: Dictionary containing token usage statistics
            - prompt_tokens: Number of tokens in the prompt
            - completion_tokens: Number of tokens in the completion
            - total_tokens: Total tokens used
    
    Example:
        >>> response = CivicChatResponse(
        ...     text="To vote in most U.S. elections...",
        ...     sources=["https://www.usa.gov/how-to-vote"],
        ...     language="en",
        ...     agent_name="CivicKnowledgeAgent",
        ...     confidence=0.95,
        ...     neutrality_score=1.0,
        ...     processing_time_ms=1250,
        ...     token_usage={"prompt_tokens": 150, "completion_tokens": 200, "total_tokens": 350}
        ... )
    """
    text: str
    sources: List[str]
    language: str
    agent_name: str
    confidence: float
    neutrality_score: float
    processing_time_ms: int
    token_usage: Dict[str, Any]
