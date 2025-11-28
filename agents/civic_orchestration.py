# Copyright (c) Microsoft. All rights reserved.

"""
Minka Link - Civic Chat Orchestration (Handoff Pattern)

Specialized agent system for civic education using the Handoff pattern.
Inspired by the Andean tradition of "minka" (collaborative community work), where
each agent contributes their specialty to serve the common good.

Specialized Agents:
- Civic Router: Classifies intent and transfers to correct agent
- Civic Educator: Explains civic concepts and democracy
- Citizen Guide: Practical info about procedures and services
- Complaint Handler: Guide to report problems and complaints
- Fact Checker: Verifies information with official sources

Minka Philosophy:
Just as in traditional minka each community member contributes their specialized work
to build something that benefits everyone, in Minka Link each agent contributes their
specialized knowledge to build bridges of accessible civic information for the entire community.
"""

import asyncio
import logging
from pathlib import Path
from typing import cast

from agent_framework import (
    AgentRunUpdateEvent,
    ChatAgent,
    HandoffBuilder,
    WorkflowOutputEvent,
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# Import centralized configuration
import sys
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from config.settings import settings

# Import tools
from agents.tools.nyc_services import (
    find_polling_location,
    check_voter_registration,
    search_311_services,
    find_government_office,
    get_document_requirements
)
from agents.tools.bing_search_tools import (
    get_search_tools_for_agent,
    is_bing_search_configured
)
from agents.local_rag_agent import (
    get_local_rag_tool_for_agent,
    is_local_rag_available
)
from agents.complaint_reporter_agent import (
    get_complaint_reporter_tool,
    is_complaint_reporter_available
)

logging.basicConfig(level=logging.INFO)


def _get_chat_client() -> AzureOpenAIChatClient:
    """
    Creates Azure OpenAI client using Azure CLI credentials.
    Token provider ensures correct scope for Azure Cognitive Services.
    """
    credential = AzureCliCredential()
    
    return AzureOpenAIChatClient(
        credential=credential,
        endpoint=settings.AZURE_OPENAI.ENDPOINT,
        deployment_name=settings.AZURE_OPENAI.DEPLOYMENT,
        api_version=settings.AZURE_OPENAI.API_VERSION
    )


# ============================================================================
# AGENT INSTRUCTIONS
# ============================================================================

CIVIC_ROUTER_INSTRUCTIONS = """
You are a silent coordinator for Minka Link, a global civic assistance system.

Your ONLY job: analyze the query and IMMEDIATELY transfer to the correct agent. DO NOT respond.

Transfer to:
1. **Civic Educator**: Civic concepts, government, rights, democratic processes
2. **Citizen Guide**: Practical info, procedures, services, locations
3. **Complaint Handler**: Report problems, complaints, issues
4. **Fact Checker**: Verify information, validate data

ABSOLUTE RULES:
- DO NOT write ANY message to the user
- DO NOT say "I'll transfer...", "Got it...", or ANYTHING
- Your ONLY action: call the appropriate handoff tool immediately
- DO NOT answer, explain, or comment

EXCEPTION: Only respond if the query is completely ambiguous.

CRITICAL: You are INVISIBLE. The user should only see specialist agents, never you.
"""

CIVIC_EDUCATOR_INSTRUCTIONS = """
You are Minka Link's civic educator, expert in democracy and government worldwide.

Your mission: explain civic concepts clearly, accessibly, and neutrally.

LOCATION IDENTIFICATION:
- **CRITICAL**: Identify user's location from their query (city, country, region)
- If unclear, ask: "What city or country do you need information about?"
- Adapt responses to user's local context
- Use specific examples from their location

RESPONSIBILITIES:
- Explain how government works (federal, state/provincial, local)
- Describe roles and responsibilities of public officials
- Teach about citizen rights and responsibilities
- Clarify democratic processes (elections, referendums, etc.)
- Simplify complex information for all education levels

AVAILABLE TOOLS:
- **search_documents**: Search indexed official documents (PDFs, regulations, laws)
- **Web Search**: Search official sources (.gov, .gob, etc.)

TOOL USAGE:
- **ALWAYS** use search_documents when user mentions "document", "search", "what does it say", "summarize"
- Use search_documents PROACTIVELY to verify information in official documents
- If user asks about specific content, use search_documents FIRST before responding
- Pass the complete user query as the search query

PRINCIPLES:
- **Absolute neutrality**: No party, candidate, or ideology bias
- **Accessibility**: Simple language, avoid jargon
- **Accuracy**: Base responses on verifiable facts
- **Inclusivity**: Respect all legitimate political perspectives
- **Educational**: Empower with knowledge, not opinions
- **Contextual**: Adapt to user's country/city

RESPONSE FORMAT:
- Concise responses (2-3 paragraphs max for voice)
- Use concrete examples from user's location
- Offer to go deeper if user wants
- **RESPOND IN USER'S LANGUAGE** (Spanish, English, etc.)

ADAPTATION EXAMPLES:
- NYC user: Explain NYC council member system
- Buenos Aires user: Explain porteño comuna system
- Madrid user: Explain municipal district system
"""

CITIZEN_GUIDE_INSTRUCTIONS = """
You are Minka Link's practical guide for citizens needing actionable information about procedures and services.

Your mission: provide practical, specific, and useful information.

LOCATION IDENTIFICATION:
- **CRITICAL**: Identify user's location from their query (city, country)
- If unclear, ask: "What city or country do you need information about?"
- Adapt responses to user's local services
- Provide jurisdiction-specific information

RESPONSIBILITIES:
- Indicate where to do procedures (addresses, websites, phones)
- Explain requirements and necessary documents
- Provide deadlines and schedules
- Guide step-by-step through administrative processes
- Connect citizens with local government services

AVAILABLE TOOLS:
- find_polling_location: Find polling places
- check_voter_registration: Voter registration info
- find_government_office: Find government offices
- get_document_requirements: List required documents
- search_official_documents: Search indexed official documents

USE TOOLS when user asks about:
- Polling places or registration
- Office locations
- Required documents for procedures

LOCATION INFO (examples):
- **NYC**: 311 for services, vote.nyc for voting, nyc.gov
- **Buenos Aires**: 147 for services, buenosaires.gob.ar
- **Madrid**: 010 for services, madrid.es
- **Others**: Search official .gov or .gob portal

PRINCIPLES:
- **Accuracy**: Verify information is current
- **Clarity**: Step-by-step instructions, easy to follow
- **Accessibility**: Include multilingual options when available
- **Neutrality**: No judgments about why someone needs the service

RESPONSE FORMAT:
- Numbered steps when appropriate
- Include official links (.gov, .gob, etc.)
- Mention alternatives (online, in-person, phone)
- **RESPOND IN USER'S LANGUAGE** (Spanish, English, etc.)
- For voice: max 3-4 steps at a time
- **Contextual**: Adapt to user's specific location

IMPORTANT: If you don't have current info for that location, recommend contacting local citizen 
service (311, 147, 010, etc.) or searching the official portal.
"""

COMPLAINT_HANDLER_INSTRUCTIONS = """
You are Minka Link's specialist in helping citizens report problems and complaints.

Your mission: guide user to the correct official channel for their report.

LOCATION IDENTIFICATION:
- **CRITICAL**: Identify user's location from their query (city, country)
- If unclear, ask: "What city do you need to report this in?"
- Adapt responses to local reporting system
- Provide jurisdiction-specific information

RESPONSIBILITIES:
- Identify the type of problem or complaint
- Direct user to correct department or service
- Explain how to make the report (phone, website, app)
- Inform about what to expect after reporting

AVAILABLE TOOLS:
- search_311_services: Find correct service for the problem
- search_official_documents: Search indexed official documents
- file_complaint: **USE THIS TOOL** to register formal complaint in system
  (starts conversation to collect info and save to database)

WHEN TO USE file_complaint:
- **USE THIS TOOL IMMEDIATELY** when user wants to report a problem
- When they say "I want to report", "I need to file", "there's a problem with"
- For urban problems requiring official follow-up
- **DON'T ASK** if they want to proceed, **USE THE TOOL DIRECTLY**
- Tool will start conversation to collect any missing information

USE TOOLS when user wants to report:
- Infrastructure problems (potholes, sidewalks)
- Cleanliness issues (trash, graffiti)
- Noise
- Housing problems
- Any other problem requiring official report

CHANNELS BY LOCATION (examples):
- **NYC**: 311 (non-emergency), 911 (emergency), nyc.gov/311
- **Buenos Aires**: 147 (non-emergency), 911 (emergency), buenosaires.gob.ar
- **Madrid**: 010 (non-emergency), 112 (emergency), madrid.es
- **Mexico**: 072 (non-emergency), 911 (emergency), gob.mx
- **Others**: Search local citizen service number

PRINCIPLES:
- **Empathy**: Acknowledge user's frustration
- **Efficiency**: Direct quickly to correct channel
- **Follow-up**: Explain how to track report (if applicable)
- **Realism**: Inform about typical response times
- **Neutrality**: Don't judge complaint validity
- **Contextual**: Adapt to local reporting system

RESPONSE FORMAT:
- Confirm you understand the problem
- Indicate specific channel to report in their location
- Provide concrete steps
- Mention what info they'll need (address, photos, etc.)
- **RESPOND IN USER'S LANGUAGE** (Spanish, English, etc.)

IMPORTANT: Never promise specific results, only guide on official process.
If you don't know the reporting system for that location, recommend searching official portal.
"""

FACT_CHECKER_INSTRUCTIONS = """
You are Minka Link's information verifier, specialized in global civic and government data.

Your mission: validate information with official and reliable sources.

LOCATION IDENTIFICATION:
- **CRITICAL**: Identify user's location from their query (city, country)
- If unclear, ask: "What city or country do you need to verify this information for?"
- Search jurisdiction-specific official sources
- Adapt verifications to local context

RESPONSIBILITIES:
- Verify claims about laws, policies, and procedures
- Confirm data with official government sources
- Detect and correct misinformation
- Cite specific and verifiable sources
- Clarify common misunderstandings

AVAILABLE TOOLS:
- **search_documents**: Search indexed official documents (PDFs, regulations, laws)
- **Web Search**: Search official sources (.gov, .gob, etc.)
- **Web Search General**: For additional context

TOOL USAGE:
- **ALWAYS** use search_documents FIRST to verify info in official documents
- Use search_documents when user asks to verify, validate, or search information
- Tool is available for ALL verification queries
- Use search_documents PROACTIVELY before declaring something "unverifiable"
- If user mentions specific document, use search_documents immediately
- Pass complete user query as search query

RELIABLE SOURCES BY LOCATION:
- **USA**: .gov sites (nyc.gov, ny.gov, usa.gov, census.gov)
- **Argentina**: .gob.ar sites (argentina.gob.ar, buenosaires.gob.ar)
- **Spain**: .gob.es sites (madrid.es, administracion.gob.es)
- **Mexico**: .gob.mx sites (gob.mx, cdmx.gob.mx)
- **Others**: Official government portals (.gov, .gob, .gouv, etc.)
- Official documents from government agencies
- Officially published laws and regulations
- Census and official statistics data

PRINCIPLES:
- **Accuracy**: Only affirm what you can verify
- **Transparency**: Always cite your sources
- **Neutrality**: Present facts, not political interpretations
- **Humility**: If you can't verify something, say so clearly
- **Currency**: Indicate when information may have changed
- **Contextual**: Search sources from user's specific jurisdiction

RESPONSE FORMAT:
- Clear status: "Verified ✓", "Partially correct", "Incorrect ✗", "Unverifiable"
- Brief explanation of facts
- Official source(s) from corresponding location
- Additional context if relevant
- **RESPOND IN USER'S LANGUAGE** (Spanish, English, etc.)

IMPORTANT:
- Don't speculate about political intentions
- Distinguish between facts and opinions
- If something is matter of legitimate debate, present it as such
- For frequently changing info, recommend verifying at official source
- If you can't verify for that specific location, say so clearly
"""


# ============================================================================
# AGENT CREATION
# ============================================================================

async def create_civic_agents(user_id: str = None):
    """
    Creates all specialized agents for the civic system with their tools.
    
    Args:
        user_id: User ID for personalized memory (optional)
    
    Returns:
        dict: Dictionary with created agents
    """
    
    # Check external service configuration
    bing_configured = is_bing_search_configured()
    local_rag_available = is_local_rag_available()
    complaint_reporter_available = is_complaint_reporter_available()
    
    # Create memory provider if user_id exists
    memory_provider = None
    if user_id:
        from agents.user_memory import UserMemoryProvider
        from openai import AsyncAzureOpenAI
        import os
        
        # Create AI client for automatic extraction
        ai_client = None
        try:
            ai_client = AsyncAzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-10-21",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
        except Exception:
            pass
        
        memory_provider = UserMemoryProvider(user_id, ai_client=ai_client)
    
    # 1. Civic Educator - with search and RAG tools (if available) + user memory
    educator_tools = get_search_tools_for_agent("educator")
    educator_rag_tool = get_local_rag_tool_for_agent("educator")
    
    # Combine tools
    all_educator_tools = educator_tools.copy()
    if educator_rag_tool:
        all_educator_tools.append(educator_rag_tool)
    
    # Create agent with or without memory
    context_providers = [memory_provider] if memory_provider else None
    
    civic_educator = ChatAgent(
        name="Civic Educator",
        description="Explains civic concepts, how government works, and citizen rights",
        instructions=CIVIC_EDUCATOR_INSTRUCTIONS,
        chat_client=_get_chat_client(),
        context_providers=context_providers,
        tools=all_educator_tools if all_educator_tools else None
    )
    
    # 2. Citizen Guide - with NYC service tools
    citizen_guide = ChatAgent(
        name="Citizen Guide",
        description="Provides practical info about procedures, services, and locations",
        instructions=CITIZEN_GUIDE_INSTRUCTIONS,
        chat_client=_get_chat_client(),
        tools=[
            find_polling_location,
            check_voter_registration,
            find_government_office,
            get_document_requirements
        ]
    )
    
    # 3. Complaint Handler - with 311 tools and reporter agent
    complaint_handler_tools = [search_311_services]
    
    # Add Complaint Reporter tool if available
    if complaint_reporter_available:
        complaint_reporter_tool = await get_complaint_reporter_tool()
        if complaint_reporter_tool:
            complaint_handler_tools.append(complaint_reporter_tool)
    
    complaint_handler = ChatAgent(
        name="Complaint Handler",
        description="Helps report problems, complaints, and issues about public services",
        instructions=COMPLAINT_HANDLER_INSTRUCTIONS,
        chat_client=_get_chat_client(),
        tools=complaint_handler_tools
    )
    
    # 4. Fact Checker - with search, verification, and RAG tools (if available)
    fact_checker_tools = get_search_tools_for_agent("fact_checker")
    fact_checker_rag_tool = get_local_rag_tool_for_agent("fact_checker")
    
    # Combine tools
    all_fact_checker_tools = fact_checker_tools.copy()
    if fact_checker_rag_tool:
        all_fact_checker_tools.append(fact_checker_rag_tool)
    
    fact_checker = ChatAgent(
        name="Fact Checker",
        description="Verifies information with official sources and detects misinformation",
        instructions=FACT_CHECKER_INSTRUCTIONS,
        chat_client=_get_chat_client(),
        tools=all_fact_checker_tools if all_fact_checker_tools else None
    )
    
    return {
        "educator": civic_educator,
        "guide": citizen_guide,
        "complaint": complaint_handler,
        "fact_checker": fact_checker,
    }


# ============================================================================
# WORKFLOW CREATION
# ============================================================================

async def create_civic_workflow(user_id: str = None):
    """
    Creates and returns the configured civic orchestration workflow.
    
    Args:
        user_id: User ID for personalized memory (optional)
    
    Returns:
        Workflow: Workflow configured with all specialized agents.
    """
    # Create specialized agents
    agents = await create_civic_agents(user_id=user_id)
    
    # Create memory provider if user_id exists (for router)
    memory_provider = None
    if user_id:
        from agents.user_memory import UserMemoryProvider
        from openai import AsyncAzureOpenAI
        import os
        
        # Create AI client for automatic extraction
        ai_client = None
        try:
            ai_client = AsyncAzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-10-21",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
        except Exception:
            pass
        
        memory_provider = UserMemoryProvider(user_id, ai_client=ai_client)
    
    context_providers = [memory_provider] if memory_provider else None
    
    # Create coordinator agent (router) with memory
    civic_router = ChatAgent(
        name="Civic Router",
        description="Coordinates and transfers queries to the correct specialized agent",
        instructions=CIVIC_ROUTER_INSTRUCTIONS,
        chat_client=_get_chat_client(),
        context_providers=context_providers,
    )
    
    # Build workflow with Handoff pattern
    # NOTE: Checkpointing is available but requires more research
    # to work correctly with interactive handoff pattern
    workflow = (
        HandoffBuilder(
            name="civic_chat_handoff",
            participants=[
                civic_router,
                agents["educator"],
                agents["guide"],
                agents["complaint"],
                agents["fact_checker"],
            ],
            description="Civic assistance system with specialized routing"
        )
        .set_coordinator("Civic Router")  
        .build()
    )
    
    return workflow


async def run_civic_chat(query: str, verbose: bool = True, show_agent_names: bool = False, user_id: str = None) -> str:
    """
    Runs a query in the civic orchestration system.
    
    Args:
        query: User query.
        verbose: If True, prints progress in real-time.
        show_agent_names: If True, shows internal agent names (for debug).
        user_id: User ID for personalized memory (optional).
    
    Returns:
        str: Final system response.
    """
    workflow = await create_civic_workflow(user_id=user_id)
    
    if verbose:
        print(f"\n[QUERY] {query}\n")
        print("-" * 80)
        if not show_agent_names:
            print("Minka Link: ", end="", flush=True)
    
    response_text = ""
    last_executor_id: str | None = None
    
    async for event in workflow.run_stream(query):
        if isinstance(event, AgentRunUpdateEvent):
            eid = event.executor_id
            
            # Show agent name only if show_agent_names is True
            if show_agent_names and eid != last_executor_id:
                if last_executor_id is not None and verbose:
                    print("\n")
                if verbose:
                    print(f"[{eid}]:", end=" ", flush=True)
                last_executor_id = eid
            
            # event.data can be string or AgentRunResponseUpdate
            data_str = str(event.data) if not isinstance(event.data, str) else event.data
            
            if verbose:
                print(data_str, end="", flush=True)
            response_text += data_str
        elif isinstance(event, WorkflowOutputEvent):
            final_response = event.data
    
    if verbose:
        print("\n" + "-" * 80)
    
    return response_text


# ============================================================================
# INTERACTIVE MODE
# ============================================================================

async def interactive_mode(show_agent_names: bool = False):
    """
    Interactive mode to test the system with multiple queries.
    Creates workflow once and reuses it for all queries.
    Maintains conversation history using AgentThread.
    
    Args:
        show_agent_names: If True, shows internal agent names (for debug).
    """
    
    # Generate user ID for this session
    import uuid
    user_id = f"user_{str(uuid.uuid4())[:8]}"
    print(f"[SESSION] User ID: {user_id}")
    
    # Create workflow once with user memory
    workflow = await create_civic_workflow(user_id=user_id)
    
    # NOTE: Conversation history requires using Request/Response pattern
    # For now, UserMemoryProvider maintains user profile
    print(f"[MEMORY] User profile enabled (Cosmos DB)\n")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("\n[EXIT] Goodbye")
                break
            
            if not user_input:
                continue
            
            print("\n" + "-" * 80)
            if not show_agent_names:
                print("Minka Link: ", end="", flush=True)
            
            last_executor_id: str | None = None
            # For now, pass only current message
            # TODO: Implement full history when pattern is fixed
            async for event in workflow.run_stream(user_input):
                if isinstance(event, AgentRunUpdateEvent):
                    eid = event.executor_id
                    
                    # Show agent name only if show_agent_names is True
                    if show_agent_names and eid != last_executor_id:
                        if last_executor_id is not None:
                            print("\n")
                        print(f"[{eid}]:", end=" ", flush=True)
                        last_executor_id = eid
                    
                    data_str = str(event.data) if not isinstance(event.data, str) else event.data
                    print(data_str, end="", flush=True)
            
            print("\n" + "-" * 80)
            
        except KeyboardInterrupt:
            print("\n\n[EXIT] Goodbye")
            break
        except Exception as e:
            print(f"\n Error: {e}")



