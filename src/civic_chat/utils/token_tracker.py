"""Token usage tracking for LLM API calls.

This module provides utilities for tracking and logging token usage
across all LLM API calls, enabling cost tracking and performance monitoring.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from civic_chat.utils.logging_config import log_agent_operation

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token usage information for an LLM API call."""
    
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: Optional[str] = None
    
    @property
    def estimated_cost_usd(self) -> float:
        """Estimate cost in USD based on token usage.
        
        Uses approximate pricing for GPT-4o-mini:
        - Input: $0.15 per 1M tokens
        - Output: $0.60 per 1M tokens
        
        Returns:
            Estimated cost in USD
        """
        # GPT-4o-mini pricing (approximate)
        input_cost_per_1m = 0.15
        output_cost_per_1m = 0.60
        
        input_cost = (self.prompt_tokens / 1_000_000) * input_cost_per_1m
        output_cost = (self.completion_tokens / 1_000_000) * output_cost_per_1m
        
        return input_cost + output_cost


class TokenTracker:
    """Tracks token usage across LLM API calls.
    
    This class provides methods for logging token usage with structured
    logging, enabling cost tracking and performance monitoring per agent.
    """
    
    def __init__(self):
        """Initialize the token tracker."""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.call_count = 0
        self.agent_usage: Dict[str, TokenUsage] = {}
    
    def log_token_usage(
        self,
        agent_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        model: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ) -> TokenUsage:
        """Log token usage for an LLM API call.
        
        This method logs token usage with structured logging and updates
        the tracker's internal counters.
        
        Args:
            agent_name: Name of the agent making the API call
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            model: Model name (e.g., "gpt-4o-mini")
            operation: Operation description (e.g., "intent_classification")
            **kwargs: Additional fields to include in the log
        
        Returns:
            TokenUsage object with usage information
        
        Validates: Requirements 10.5
        """
        total_tokens = prompt_tokens + completion_tokens
        
        # Create TokenUsage object
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=model
        )
        
        # Update tracker counters
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_tokens += total_tokens
        self.call_count += 1
        
        # Update per-agent usage
        if agent_name not in self.agent_usage:
            self.agent_usage[agent_name] = TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=model
            )
        
        agent_usage = self.agent_usage[agent_name]
        agent_usage.prompt_tokens += prompt_tokens
        agent_usage.completion_tokens += completion_tokens
        agent_usage.total_tokens += total_tokens
        
        # Log token usage with structured logging (Requirement 10.5)
        log_data = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": usage.estimated_cost_usd,
            "call_count": self.call_count,
            "cumulative_tokens": self.total_tokens,
        }
        
        if model:
            log_data["model"] = model
        
        if operation:
            log_data["llm_operation"] = operation
        
        # Add any additional fields
        log_data.update(kwargs)
        
        log_agent_operation(
            logger,
            agent_name=agent_name,
            operation="llm_api_call",
            outcome="success",
            **log_data
        )
        
        return usage
    
    def get_agent_usage(self, agent_name: str) -> Optional[TokenUsage]:
        """Get token usage for a specific agent.
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            TokenUsage object or None if agent has no usage
        """
        return self.agent_usage.get(agent_name)
    
    def get_total_usage(self) -> TokenUsage:
        """Get total token usage across all agents.
        
        Returns:
            TokenUsage object with total usage
        """
        return TokenUsage(
            prompt_tokens=self.total_prompt_tokens,
            completion_tokens=self.total_completion_tokens,
            total_tokens=self.total_tokens
        )
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get a summary of token usage across all agents.
        
        Returns:
            Dictionary with usage summary including per-agent breakdown
        """
        total_usage = self.get_total_usage()
        
        summary = {
            "total_calls": self.call_count,
            "total_tokens": self.total_tokens,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "estimated_total_cost_usd": total_usage.estimated_cost_usd,
            "agents": {}
        }
        
        for agent_name, usage in self.agent_usage.items():
            summary["agents"][agent_name] = {
                "total_tokens": usage.total_tokens,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "estimated_cost_usd": usage.estimated_cost_usd,
                "model": usage.model
            }
        
        return summary
    
    def reset(self) -> None:
        """Reset all token usage counters."""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.call_count = 0
        self.agent_usage.clear()
        
        logger.info(
            "Token tracker reset",
            extra={"operation": "reset"}
        )


# Global token tracker instance
_global_tracker = TokenTracker()


def get_global_tracker() -> TokenTracker:
    """Get the global token tracker instance.
    
    Returns:
        Global TokenTracker instance
    """
    return _global_tracker


def log_llm_call(
    agent_name: str,
    prompt_tokens: int,
    completion_tokens: int,
    model: Optional[str] = None,
    operation: Optional[str] = None,
    **kwargs
) -> TokenUsage:
    """Log an LLM API call using the global tracker.
    
    This is a convenience function for logging token usage without
    managing a TokenTracker instance.
    
    Args:
        agent_name: Name of the agent making the API call
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        model: Model name (e.g., "gpt-4o-mini")
        operation: Operation description (e.g., "intent_classification")
        **kwargs: Additional fields to include in the log
    
    Returns:
        TokenUsage object with usage information
    
    Validates: Requirements 10.5
    """
    return _global_tracker.log_token_usage(
        agent_name=agent_name,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        model=model,
        operation=operation,
        **kwargs
    )


def extract_token_usage_from_response(response: Any) -> Optional[Dict[str, int]]:
    """Extract token usage from an LLM API response.
    
    This function attempts to extract token usage information from
    various response formats (OpenAI, Azure OpenAI, etc.).
    
    Args:
        response: LLM API response object
    
    Returns:
        Dictionary with prompt_tokens, completion_tokens, total_tokens
        or None if usage information is not available
    """
    # Try to extract usage from common response formats
    if hasattr(response, 'usage'):
        usage = response.usage
        if hasattr(usage, 'prompt_tokens') and hasattr(usage, 'completion_tokens'):
            return {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": getattr(usage, 'total_tokens', 
                                       usage.prompt_tokens + usage.completion_tokens)
            }
    
    # Try dictionary format
    if isinstance(response, dict) and 'usage' in response:
        usage = response['usage']
        if 'prompt_tokens' in usage and 'completion_tokens' in usage:
            return {
                "prompt_tokens": usage['prompt_tokens'],
                "completion_tokens": usage['completion_tokens'],
                "total_tokens": usage.get('total_tokens', 
                                         usage['prompt_tokens'] + usage['completion_tokens'])
            }
    
    return None
