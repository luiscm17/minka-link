"""
Complaint Reporter Agent - Conversational agent for reporting complaints

This agent:
1. Collects user information in a friendly, conversational way
2. Structures information according to required format
3. Saves complaint to Cosmos DB
4. Returns tracking number to user

The agent can be used as a tool by the Complaint Handler.
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Annotated, Optional

# Import configuration
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from config.settings import settings

# Agent Framework imports
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# Cosmos DB imports
try:
    from azure.cosmos import CosmosClient, PartitionKey
    from azure.cosmos.exceptions import CosmosResourceNotFoundError
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False


def _get_chat_client() -> AzureOpenAIChatClient:
    """Creates Azure OpenAI client."""
    credential = AzureCliCredential()
    
    return AzureOpenAIChatClient(
        credential=credential,
        endpoint=settings.AZURE_OPENAI.ENDPOINT,
        deployment_name=settings.AZURE_OPENAI.DEPLOYMENT,
        api_version=settings.AZURE_OPENAI.API_VERSION
    )


def _get_cosmos_container():
    """
    Gets Cosmos DB container to store complaints.
    
    Returns:
        ContainerProxy: Cosmos DB container
    """
    if not COSMOS_AVAILABLE:
        raise ImportError("azure-cosmos is not installed")
    
    # Validate configuration
    settings.validate_cosmos_db()
    
    # Create Cosmos DB client
    if settings.COSMOS_DB.KEY:
        # Use key if available
        client = CosmosClient(
            settings.COSMOS_DB.ENDPOINT,
            credential=settings.COSMOS_DB.KEY
        )
    else:
        # Use Azure CLI credential
        credential = AzureCliCredential()
        client = CosmosClient(
            settings.COSMOS_DB.ENDPOINT,
            credential=credential
        )
    
    # Get database and container
    database = client.get_database_client(settings.COSMOS_DB.DATABASE_NAME)
    container = database.get_container_client(settings.COSMOS_DB.CONTAINER_NAME)
    
    return container


def save_complaint_to_cosmos(complaint_data: dict) -> dict:
    """
    Saves a complaint to Cosmos DB.
    
    Args:
        complaint_data: Dictionary with complaint data
    
    Returns:
        dict: Response with saved complaint ID
    """
    try:
        container = _get_cosmos_container()
        
        # Verify it has location structure with city (partition key)
        if "location" not in complaint_data or "city" not in complaint_data["location"]:
            return {
                "success": False,
                "error": "Missing location.city",
                "message": "Error: Complaint must include city (location.city)"
            }
        
        # Create item with timestamp and unique ID
        item = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **complaint_data,
            "_ts": int(datetime.now(timezone.utc).timestamp())
        }
        
        # Save to Cosmos DB
        # Partition key is /location/city, taken automatically from item
        created_item = container.create_item(body=item)
        
        return {
            "success": True,
            "complaint_id": created_item["id"],
            "message": f"Complaint registered successfully with ID: {created_item['id']}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error saving complaint: {str(e)}"
        }


# ============================================================================
# AGENT INSTRUCTIONS
# ============================================================================

COMPLAINT_REPORTER_INSTRUCTIONS = """
You are Minka Link's assistant that processes urban problem reports.

When you receive a problem description, you must:

REQUIRED INFORMATION:
1. **City** (city): What city is the problem in?
2. **Address** (address): Exact address or location description
3. **Description** (contenido): What problem did you observe? (detailed)
4. **Category** (metadata.categoria): Problem type (infer from description)
   - Options: "mobiliario urbano", "espacio público", "infraestructura", "limpieza", "iluminación", "seguridad", "otro"

OPTIONAL INFORMATION (infer if possible):
5. **Coordinates** (lat, lon): If user provides them
6. **Criticality**: "baja", "media", "alta" (infer from description)
7. **Tags** (metadata.etiquetas): Problem keywords

CONVERSATION RULES:
- Be friendly and empathetic
- Ask ONE question at a time
- If user already provided info, don't ask again
- Infer information when obvious (e.g., "pothole" → category "infraestructura")
- Confirm information before saving
- **USE USER'S LANGUAGE** (Spanish, English, etc.)

PROCESS:
1. Greet and ask what problem they want to report
2. Ask for location (city and address)
3. Request more details if needed
4. Confirm all information
5. Save to Cosmos DB
6. Provide tracking number

IMPORTANT:
- DON'T invent information
- If critical info is missing (city, address, description), ask for it
- Be brief and direct
- At the end, call save_complaint function to save

FINAL RESPONSE FORMAT:
When you have all information, structure like this:
{
    "criticidad": "baja|media|alta",
    "location": {
        "city": "City",
        "address": "Full address",
        "lat": -34.xxxx (optional),
        "lon": -58.xxxx (optional)
    },
    "contenido": "Detailed problem description",
    "origen": "texto",
    "estado": "en evaluación",
    "usuarioId": null,
    "metadata": {
        "categoria": "inferred category",
        "etiquetas": ["tag1", "tag2", "tag3"]
    }
}
"""


async def create_complaint_reporter_agent() -> ChatAgent:
    """
    Creates the complaint reporter agent.
    
    Returns:
        ChatAgent: Agent configured to report complaints
    """
    # Create function to save to Cosmos DB
    from agent_framework import ai_function
    
    @ai_function
    def save_complaint(
        complaint_json: Annotated[str, "JSON string with complaint data in specified format"]
    ) -> str:
        """
        Saves a complaint to Cosmos DB.
        Use this function when you have all information collected from user.
        """
        import json
        
        try:
            # Parse JSON
            complaint_data = json.loads(complaint_json)
            
            # Save to Cosmos DB
            result = save_complaint_to_cosmos(complaint_data)
            
            if result["success"]:
                return f"✅ {result['message']}\n\nYou can use this ID to track your complaint."
            else:
                return f"❌ {result['message']}\n\nPlease try again or contact support."
                
        except json.JSONDecodeError as e:
            return f"Error processing data: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    # Create agent with save tool
    agent = ChatAgent(
        name="Complaint Reporter",
        description="Conversational agent that collects information to report citizen complaints",
        instructions=COMPLAINT_REPORTER_INSTRUCTIONS,
        chat_client=_get_chat_client(),
        tools=[save_complaint]
    )
    
    return agent


def is_complaint_reporter_available() -> bool:
    """
    Checks if Complaint Reporter is available.
    
    Returns:
        bool: True if Cosmos DB is configured
    """
    return (
        COSMOS_AVAILABLE and
        bool(settings.COSMOS_DB.ENDPOINT) and
        bool(settings.COSMOS_DB.DATABASE_NAME) and
        bool(settings.COSMOS_DB.CONTAINER_NAME)
    )


async def get_complaint_reporter_tool():
    """
    Gets Complaint Reporter as a tool for other agents.
    
    This function converts the agent into a tool that can be used
    by the Complaint Handler.
    
    Returns:
        Tool: Tool that encapsulates the reporter agent
    """
    if not is_complaint_reporter_available():
        return None
    
    # Create agent
    reporter_agent = await create_complaint_reporter_agent()
    
    # Convert to tool
    reporter_tool = reporter_agent.as_tool(
        name="file_complaint",
        description=(
            "Starts a conversational process to report a citizen complaint. "
            "This tool collects user information (location, description, etc.) "
            "and saves the complaint to the system. Use it when user wants to report "
            "an urban problem like potholes, trash, graffiti, etc."
        ),
        arg_name="initial_complaint",
        arg_description="Initial description of the problem the user wants to report"
    )
    
    return reporter_tool



