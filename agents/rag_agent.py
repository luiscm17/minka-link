"""
RAG Agent - Specialized agent for official document search

This agent is used as a tool by other agents to search for information
in official documents indexed in Azure AI Foundry.
"""

import sys
from pathlib import Path
from agent_framework import ChatAgent, HostedFileSearchTool
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# Import configuration
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from config.settings import settings


def _get_chat_client() -> AzureOpenAIChatClient:
    """Creates Azure OpenAI client."""
    credential = AzureCliCredential()
    
    return AzureOpenAIChatClient(
        credential=credential,
        endpoint=settings.AZURE_OPENAI.ENDPOINT,
        deployment_name=settings.AZURE_OPENAI.DEPLOYMENT,
        api_version=settings.AZURE_OPENAI.API_VERSION
    )


RAG_AGENT_INSTRUCTIONS = """
You are a document search specialist with access to official civic documents.

Your job is to search through indexed documents and provide relevant information.

CRITICAL RULES:
- Use your search capabilities to find information in the indexed documents
- Search for ANY query that could be answered by official documents
- Return the most relevant excerpts from the documents
- Include document names and sources when available
- If no relevant information is found, say so clearly
- Be thorough in your search before concluding information is not available

RESPONSE FORMAT:
- Quote relevant text from documents
- Cite the document source and page if available
- Be concise but complete
- Respond in the same language as the query

IMPORTANT:
- You have access to civic documents including electoral platforms, regulations, and official documents
- Search broadly - documents may be in Spanish or other languages
- If you find relevant information, provide detailed quotes and citations
"""


def create_rag_agent() -> ChatAgent:
    """
    Creates specialized document search agent (RAG).
    
    This agent uses HostedFileSearchTool to search documents
    indexed in Azure AI Foundry.
    
    Returns:
        ChatAgent: Agent configured with File Search
    """
    if not settings.is_foundry_configured():
        raise ValueError(
            "Azure AI Foundry is not configured. "
            "Set AZURE_AI_PROJECT_ENDPOINT in your .env"
        )
    
    # Create file search tool
    # If vector_store_id is configured, use it
    if settings.AZURE_AI_PROJECT.VECTOR_STORE_ID:
        file_search_tool = HostedFileSearchTool(
            vector_store_ids=[settings.AZURE_AI_PROJECT.VECTOR_STORE_ID]
        )
    else:
        # Without vector store ID, use default (may not work)
        file_search_tool = HostedFileSearchTool()
    
    # Create RAG agent
    rag_agent = ChatAgent(
        name="Document Search Agent",
        description="Searches through official documents to find relevant information",
        instructions=RAG_AGENT_INSTRUCTIONS,
        chat_client=_get_chat_client(),
        tools=[file_search_tool]
    )
    
    return rag_agent


def create_rag_tool():
    """
    Creates a tool from the RAG agent using .as_tool().
    
    This tool can be used by other agents to search documents.
    
    Returns:
        Tool: Tool that encapsulates the RAG agent
    """
    rag_agent = create_rag_agent()
    
    # Convert agent to tool with custom description
    rag_tool = rag_agent.as_tool(
        name="search_documents",
        description=(
            "Search through official government documents (PDFs, regulations, laws) "
            "indexed in the system. Use this tool whenever you need to find specific "
            "information from official documents, verify facts, or cite sources. "
            "Works for documents in any language."
        ),
        arg_name="query",
        arg_description="The search query or question to find in official documents"
    )
    
    return rag_tool


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_rag_available() -> bool:
    """
    Checks if RAG agent is available.
    
    Returns:
        bool: True if Azure AI Foundry is configured
    """
    return settings.is_foundry_configured()


def get_rag_tool_for_agent(agent_type: str):
    """
    Gets RAG tool for an agent type.
    
    Args:
        agent_type: Agent type
    
    Returns:
        Tool or None: RAG tool if available
    """
    if not is_rag_available():
        return None
    
    # All agents that need RAG use the same tool
    if agent_type in ["educator", "fact_checker", "guide"]:
        return create_rag_tool()
    
    return None
