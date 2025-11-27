"""
Agent Orchestration using SwitchCase Pattern with Thread Persistence.

Routes user messages to specialized agents based on intent classification:
- Civic Knowledge Agent: Voting, elections, government information
- Complaint Agent: Filing complaints and reports
- City Guide Agent: City adaptation and practical information

Threads are persisted manually to enable multi-turn conversations.
"""

import logging
from agent_framework import WorkflowBuilder, Case, Default
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from openai import AsyncAzureOpenAI
from civic_chat.config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION
)
from civic_chat.agents.memory.memory_manager import CivicMemoryManager
from civic_chat.agents.complaint.complaint_manager import ComplaintManager
from civic_chat.agents.civic_knowledge_agent import AGENT_INSTRUCTIONS as CIVIC_INSTRUCTIONS
from civic_chat.agents.complaint_agent import AGENT_INSTRUCTIONS as COMPLAINT_INSTRUCTIONS
from civic_chat.agents.city_guide_agent import AGENT_INSTRUCTIONS as CITY_GUIDE_INSTRUCTIONS

logger = logging.getLogger(__name__)

CLASSIFIER_INSTRUCTIONS = """You are an intent classifier for a Civic Chat system.

Analyze the user's message and classify it into ONE of these categories:

1. **COMPLAINT**: User wants to file a complaint, report a problem, or denounce an issue
   - Keywords: denuncia, queja, reportar, problema, bache, servicio público, corrupción
   - Examples: "Quiero reportar un bache", "Hay un problema con la basura", "Denuncia de corrupción"

2. **CIVIC_KNOWLEDGE**: User asks about voting, elections, government, or civic processes
   - Keywords: votar, elecciones, candidato, registro, gobierno, derechos, ciudadanía
   - Examples: "¿Cómo me registro para votar?", "¿Cuándo son las elecciones?", "¿Qué es el Senado?"

3. **CITY_GUIDE**: User needs help adapting to the city or practical information
   - Keywords: transporte, metro, hospital, escuela, trabajo, vivienda, barrio, cómo llegar
   - Examples: "¿Cómo funciona el metro?", "¿Dónde hay hospitales?", "Necesito clases de inglés"

4. **GENERAL**: Greetings, unclear intent, or doesn't fit the above categories
   - Examples: "Hola", "Gracias", "¿Qué puedes hacer?", unclear messages

IMPORTANT:
- Respond with ONLY ONE WORD: COMPLAINT, CIVIC_KNOWLEDGE, CITY_GUIDE, or GENERAL
- Do NOT add explanations, punctuation, or extra text
- Be decisive - choose the best match even if uncertain"""


async def create_agents_orchestration(user_id: str = "demo_user"):
    """Create agent orchestration using SwitchCase pattern for intelligent routing.
    
    Args:
        user_id: User identifier for persistent memory
    
    Returns:
        Configured workflow with intent-based routing to specialized agents
    
    Note:
        Uses SwitchCase pattern to route messages to the appropriate specialized agent
        based on intent classification. Only the selected agent responds to the user.
        Threads can be persisted manually using serialize/deserialize methods.
    """
    # Create OpenAI client for memory AI analysis
    ai_client = AsyncAzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION or "2024-10-21",
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )
    
    # Create memory manager (ContextProvider)
    memory_manager = CivicMemoryManager(user_id=user_id, ai_client=ai_client)
    
    # Create complaint manager (ContextProvider)
    complaint_manager = ComplaintManager(user_id=user_id, ai_client=ai_client)
    
    # Create Azure Chat Client
    chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())
    
    # Create classifier agent (lightweight, just for intent detection)
    classifier_agent = chat_client.create_agent(
        instructions=CLASSIFIER_INSTRUCTIONS,
        name="IntentClassifier"
    )
    
    # Create specialized agents WITH memory manager
    civic_knowledge_agent = chat_client.create_agent(
        instructions=CIVIC_INSTRUCTIONS,
        name="CivicKnowledgeAgent",
        context_providers=[memory_manager]
    )
    
    # Complaint agent WITH both memory and complaint managers
    complaint_agent = chat_client.create_agent(
        instructions=COMPLAINT_INSTRUCTIONS,
        name="ComplaintAgent",
        context_providers=[memory_manager, complaint_manager]
    )
    
    city_guide_agent = chat_client.create_agent(
        instructions=CITY_GUIDE_INSTRUCTIONS,
        name="CityGuideAgent",
        context_providers=[memory_manager]
    )
    
    # Create a general assistant for unclear intents WITH memory
    general_agent = chat_client.create_agent(
        instructions="""You are a friendly general assistant for Civic Chat.
        
When users greet you or have unclear requests, help them understand what you can do:

1. **Civic Knowledge**: Answer questions about voting, elections, and government
2. **File Complaints**: Help report problems with public services
3. **City Guide**: Provide information about adapting to the city

Be warm and guide them to specify what they need help with.""",
        name="GeneralAssistant",
        context_providers=[memory_manager]
    )
    
    # Helper function to extract text from agent response
    def get_response_text(result) -> str:
        """Extract text from AgentExecutorResponse."""
        try:
            if hasattr(result, 'agent_run_response') and hasattr(result.agent_run_response, 'text'):
                return result.agent_run_response.text.upper()
            elif hasattr(result, 'text'):
                return result.text.upper()
            return ""
        except Exception:
            return ""
    
    # Build workflow with SwitchCase routing
    workflow = (
        WorkflowBuilder()
        .set_start_executor(classifier_agent)
        .add_switch_case_edge_group(
            classifier_agent,
            [
                # Route to Complaint Agent
                Case(
                    condition=lambda result: "COMPLAINT" in get_response_text(result),
                    target=complaint_agent
                ),
                # Route to Civic Knowledge Agent
                Case(
                    condition=lambda result: "CIVIC_KNOWLEDGE" in get_response_text(result),
                    target=civic_knowledge_agent
                ),
                # Route to City Guide Agent
                Case(
                    condition=lambda result: "CITY_GUIDE" in get_response_text(result),
                    target=city_guide_agent
                ),
                # Default: Route to General Assistant for greetings/unclear intents
                Default(target=general_agent)
            ],
        )
        .build()
    )
    
    return workflow
