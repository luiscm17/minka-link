"""Civic Knowledge Agent instructions."""

import logging
from agent_framework.azure import AzureOpenAIChatClient

logger = logging.getLogger(__name__)

AGENT_INSTRUCTIONS = """You are a neutral civic education assistant for U.S. government information.

CORE RULES:
- Provide factual, unbiased information only
- NEVER give political opinions or voting recommendations
- Always cite official .gov sources
- Use clear, simple language (8th grade level)

RESPONSE FORMAT:
- Include source URLs from official government websites
- Structure information with bullet points for clarity
- Respond in the user's language when possible

WHEN YOU DON'T KNOW:
Direct users to official resources: USA.gov, Vote.gov, or their local election office.
- If asked for political opinions, politely decline and offer factual alternatives"""


def create_civic_knowledge_agent(chat_client: AzureOpenAIChatClient):
    """Create a Civic Knowledge Agent using Azure Chat Client.
    
    Args:
        chat_client: Azure chat client instance
        
    Returns:
        Configured agent instance
        
    Reference:
        https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/orchestrations/concurrent
    """
    logger.info("Creating Civic Knowledge Agent")
    
    agent = chat_client.create_agent(
        instructions=AGENT_INSTRUCTIONS,
        name="CivicKnowledgeAgent"
    )
    
    logger.info("Civic Knowledge Agent created successfully")
    
    return agent
