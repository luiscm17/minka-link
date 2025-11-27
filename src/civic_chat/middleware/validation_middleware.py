import json
import logging
from typing import Optional, Dict, Any, Callable, Awaitable
from dataclasses import dataclass, field

from agent_framework import AgentMiddleware, AgentRunContext
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework._types import AgentRunResponse, ChatMessage, Role

from civic_chat.utils.validation_constants import (
    BIAS_KEYWORDS,
    CONTENT_SAFETY_THRESHOLD,
    VIOLATION_THRESHOLD,
    get_generic_neutral_response,
)
from civic_chat.utils.logging_config import log_agent_operation
from civic_chat.utils.token_tracker import log_llm_call, extract_token_usage_from_response

logger = logging.getLogger(__name__)

try:
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.ai.contentsafety.models import AnalyzeTextOptions
    from azure.core.credentials import AzureKeyCredential
    CONTENT_SAFETY_AVAILABLE = True
except ImportError:
    CONTENT_SAFETY_AVAILABLE = False
    logger.warning("Azure Content Safety SDK not available")


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    reason: str = ""
    violation_type: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class BaseValidationMiddleware(AgentMiddleware):
    """Base class for validation middleware with common functionality."""
    
    def __init__(self, name: str):
        self.name = name
        self.violation_count = 0
    
    async def process(
        self,
        context: AgentRunContext,
        next: Callable[[AgentRunContext], Awaitable[None]],
    ) -> None:
        """Process agent run and validate response."""
        await next(context)
        
        if context.result and not context.is_streaming:
            response_text = self._extract_text(context)
            if response_text:
                result = await self.validate(response_text)
                if not result.is_valid:
                    self._handle_violation(result)
                    self._replace_response(context)
    
    def _extract_text(self, context: AgentRunContext) -> str:
        """Extract text from agent response."""
        try:
            if hasattr(context.result, 'messages') and context.result.messages:
                return context.result.messages[-1].text or ""
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
        return ""
    
    def _replace_response(self, context: AgentRunContext) -> None:
        """Replace response with generic neutral message."""
        language = context.metadata.get('language', 'en') if hasattr(context, 'metadata') and context.metadata else 'en'
        generic_response = get_generic_neutral_response(language)
        context.result = AgentRunResponse(
            messages=[ChatMessage(role=Role.ASSISTANT, text=generic_response)]
        )
    
    def _handle_violation(self, result: ValidationResult) -> None:
        """Handle a validation violation."""
        self.violation_count += 1
        log_agent_operation(
            logger,
            agent_name=self.name,
            operation="validation_violation",
            outcome="violation_detected",
            violation_count=self.violation_count,
            violation_type=result.violation_type,
            reason=result.reason,
            details=result.details
        )
        
        if self.violation_count >= VIOLATION_THRESHOLD:
            log_agent_operation(
                logger,
                agent_name=self.name,
                operation="violation_threshold_exceeded",
                outcome="alert",
                violation_count=self.violation_count,
                threshold=VIOLATION_THRESHOLD,
                alert_level="critical"
            )
    
    async def validate(self, text: str) -> ValidationResult:
        """Override this method to implement validation logic."""
        raise NotImplementedError


class BiasKeywordMiddleware(BaseValidationMiddleware):
    """Validates responses for bias keywords."""
    
    def __init__(self):
        super().__init__("BiasKeywordMiddleware")
    
    async def validate(self, text: str) -> ValidationResult:
        """Check for bias keywords."""
        text_lower = text.lower()
        for keyword in BIAS_KEYWORDS:
            if keyword in text_lower:
                logger.warning(f"Bias keyword detected: {keyword}")
                return ValidationResult(
                    is_valid=False,
                    reason=f"Contains bias keyword: '{keyword}'",
                    violation_type="bias_keyword",
                    details={"keyword": keyword}
                )
        return ValidationResult(is_valid=True, reason="No bias keywords")


class ContentSafetyMiddleware(BaseValidationMiddleware):
    """Validates responses using Azure Content Safety API."""
    
    def __init__(self, content_safety_endpoint: Optional[str] = None, content_safety_key: Optional[str] = None):
        super().__init__("ContentSafetyMiddleware")
        self.client = None
        
        if CONTENT_SAFETY_AVAILABLE and content_safety_endpoint and content_safety_key:
            try:
                self.client = ContentSafetyClient(
                    endpoint=content_safety_endpoint,
                    credential=AzureKeyCredential(content_safety_key)
                )
                logger.info("Azure Content Safety initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Content Safety: {e}")
    
    async def validate(self, text: str) -> ValidationResult:
        """Check content safety using Azure API."""
        if not self.client:
            return ValidationResult(is_valid=True, reason="Content safety not configured")
        
        try:
            response = self.client.analyze_text(AnalyzeTextOptions(text=text))
            
            for category, result in [
                ("hate", response.hate_result),
                ("self_harm", response.self_harm_result),
                ("sexual", response.sexual_result),
                ("violence", response.violence_result)
            ]:
                if result and result.severity >= CONTENT_SAFETY_THRESHOLD:
                    logger.warning(f"Content safety violation: {category}")
                    return ValidationResult(
                        is_valid=False,
                        reason=f"Content safety: {category} (severity: {result.severity})",
                        violation_type="content_safety",
                        details={"category": category, "severity": result.severity}
                    )
            
            return ValidationResult(is_valid=True, reason="Content safe")
        except Exception as e:
            logger.error(f"Content safety error: {e}")
            return ValidationResult(is_valid=True, reason=f"Error, allowing as fallback: {e}")


class NeutralityValidationMiddleware(BaseValidationMiddleware):
    """Validates responses for subtle bias using LLM."""
    
    def __init__(self, chat_client: AzureOpenAIChatClient):
        super().__init__("NeutralityValidationMiddleware")
        self.validator = chat_client.create_agent(
            name="NeutralityValidator",
            instructions="""You are a neutrality validator for civic education.

Reject content that:
- Makes voting recommendations or endorsements
- Expresses political opinions or preferences
- Shows bias toward any party, candidate, or ideology
- Contains harmful or inappropriate content

Factual, educational content is acceptable.

Return ONLY valid JSON (no markdown):
{
    "is_neutral": true/false,
    "reasoning": "explanation",
    "violation_type": "bias|safety|policy|none",
    "suggested_fix": "fix or empty string"
}"""
        )
    
    async def validate(self, text: str) -> ValidationResult:
        """Check for subtle bias using LLM."""
        try:
            prompt = f"""Analyze for political bias:

"{text}"

Return ONLY JSON (no markdown):
{{
    "is_neutral": true/false,
    "reasoning": "explanation",
    "violation_type": "bias|safety|policy|none",
    "suggested_fix": "fix or empty"
}}"""
            
            async with self.validator:
                response = await self.validator.run(prompt)
                response_text = response.text.strip()
                
                # Log token usage
                token_usage = extract_token_usage_from_response(response)
                if token_usage:
                    log_llm_call(
                        agent_name=self.name,
                        prompt_tokens=token_usage["prompt_tokens"],
                        completion_tokens=token_usage["completion_tokens"],
                        model="gpt-4o-mini",
                        operation="bias_detection"
                    )
                
                # Remove markdown if present
                if response_text.startswith("```"):
                    response_text = "\n".join(
                        line for line in response_text.split("\n")
                        if not line.strip().startswith("```")
                    )
                
                result = json.loads(response_text)
                is_neutral = result.get("is_neutral", True)
                
                if not is_neutral:
                    logger.warning(f"LLM detected bias: {result.get('reasoning')}")
                    return ValidationResult(
                        is_valid=False,
                        reason=f"LLM detected bias: {result.get('reasoning')}",
                        violation_type=f"llm_{result.get('violation_type', 'bias')}",
                        details={"reasoning": result.get("reasoning"), "suggested_fix": result.get("suggested_fix")}
                    )
                
                return ValidationResult(is_valid=True, reason="LLM validation passed")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return ValidationResult(is_valid=False, reason="Parse error, rejecting", violation_type="validation_error")
        except Exception as e:
            logger.error(f"LLM validation error: {e}")
            return ValidationResult(is_valid=False, reason=f"Validation error: {e}", violation_type="validation_error")
