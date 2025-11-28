"""
User Memory Provider - User memory for agents

This module provides persistent user memory using ContextProvider.
Allows agents to remember user information between interactions.

Stores information in Cosmos DB for cloud persistence.

Based on Microsoft Agent Framework ContextProvider pattern.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict
from openai import AsyncAzureOpenAI

# Import configuration
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agent_framework import ContextProvider, Context
from config.settings import settings

# Cosmos DB imports
try:
    from azure.cosmos import CosmosClient
    from azure.cosmos.exceptions import CosmosResourceNotFoundError
    from azure.identity import AzureCliCredential
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False

# Directory to save user profiles (local fallback)
USER_DATA_DIR = project_root / "data_user"


class UserMemoryProvider(ContextProvider):
    """
    User memory provider for agents with automatic AI extraction.
    
    Maintains:
    - User profile (name, location, profession)
    - Extracted context (procedures, documents, important dates)
    - Session statistics
    
    Does NOT save complete messages, only relevant context extracted with AI.
    Persists in Cosmos DB (with local file fallback if not configured).
    """
    
    def __init__(self, user_id: str, ai_client: Optional[AsyncAzureOpenAI] = None, use_cosmos: bool = True):
        """
        Initializes the memory provider.
        
        Args:
            user_id: Unique user identifier
            ai_client: Azure OpenAI client for automatic extraction (optional)
            use_cosmos: If True, tries to use Cosmos DB; if False, uses local files
        """
        self.user_id = user_id
        self.profile = {
            "user_info": {
                "name": None,
                "location": None,
                "profession": None,
                "last_updated": None
            },
            "extracted_data": {
                "procedures": [],      # Procedimientos/trámites consultados
                "documents": [],       # Documentos mencionados
                "important_dates": []  # Fechas importantes
            }
        }
        self.session_data = {
            "interaction_count": 0,
            "last_agent": None
        }
        self.ai_client = ai_client
        self.use_cosmos = use_cosmos and COSMOS_AVAILABLE and self._is_cosmos_configured()
        self.cosmos_container = None
        
        # Initialize Cosmos DB if available
        if self.use_cosmos:
            try:
                self.cosmos_container = self._get_cosmos_container()
            except Exception:
                self.use_cosmos = False
        
        # Fallback to local files if Cosmos not available
        if not self.use_cosmos:
            USER_DATA_DIR.mkdir(exist_ok=True)
        
        # Load existing profile
        self._load_profile()
    
    def _is_cosmos_configured(self) -> bool:
        """Checks if Cosmos DB is configured."""
        return bool(
            settings.COSMOS_DB.ENDPOINT and
            settings.COSMOS_DB.DATABASE_NAME and
            settings.COSMOS_DB.MEMORY_CONTAINER_NAME
        )
    
    def _get_cosmos_container(self):
        """Gets Cosmos DB container for user memory."""
        if not COSMOS_AVAILABLE:
            raise ImportError("azure-cosmos is not installed")
        
        # Validate configuration
        settings.validate_cosmos_db_memory()
        
        # Create client
        if settings.COSMOS_DB.KEY:
            client = CosmosClient(
                settings.COSMOS_DB.ENDPOINT,
                credential=settings.COSMOS_DB.KEY
            )
        else:
            credential = AzureCliCredential()
            client = CosmosClient(
                settings.COSMOS_DB.ENDPOINT,
                credential=credential
            )
        
        # Get container
        database = client.get_database_client(settings.COSMOS_DB.DATABASE_NAME)
        container = database.get_container_client(settings.COSMOS_DB.MEMORY_CONTAINER_NAME)
        
        return container
    
    def _get_profile_path(self) -> Path:
        """Gets user profile file path (local fallback)."""
        return USER_DATA_DIR / f"{self.user_id}_profile.json"
    
    def _load_profile(self):
        """Loads user profile from Cosmos DB or local file."""
        if self.use_cosmos and self.cosmos_container:
            self._load_from_cosmos()
        else:
            self._load_from_file()
    
    def _load_from_cosmos(self):
        """Loads profile from Cosmos DB."""
        try:
            item = self.cosmos_container.read_item(
                item=self.user_id,
                partition_key=self.user_id
            )
            self.profile = item.get('profile', self.profile)
            self.session_data = item.get('session_data', self.session_data)
        except CosmosResourceNotFoundError:
            # New user, empty profile
            pass
        except Exception:
            # Error loading, use empty profile
            pass
    
    def _load_from_file(self):
        """Loads profile from local file (fallback)."""
        profile_path = self._get_profile_path()
        
        if profile_path.exists():
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.profile = data.get('profile', self.profile)
                self.session_data = data.get('session_data', self.session_data)
            except Exception:
                pass
                self.profile = {
                    "user_info": {
                        "name": None,
                        "location": None,
                        "profession": None,
                        "last_updated": None
                    },
                    "extracted_data": {
                        "procedures": [],
                        "documents": [],
                        "important_dates": []
                    }
                }
    
    def _save_profile(self):
        """Saves user profile to Cosmos DB or local file."""
        if self.use_cosmos and self.cosmos_container:
            self._save_to_cosmos()
        else:
            self._save_to_file()
    
    def _save_to_cosmos(self):
        """Saves profile to Cosmos DB."""
        try:
            # Update timestamp
            self.profile['user_info']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            item = {
                'id': self.user_id,
                'user_id': self.user_id,  # Partition key
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'profile': self.profile,
                'session_data': self.session_data,
                '_ts': int(datetime.now(timezone.utc).timestamp())
            }
            
            # Upsert (create or update)
            self.cosmos_container.upsert_item(body=item)
        except Exception:
            pass
    
    def _save_to_file(self):
        """Saves profile to local file (fallback)."""
        profile_path = self._get_profile_path()
        
        try:
            # Actualizar timestamp
            self.profile['user_info']['last_updated'] = datetime.now().isoformat()
            
            data = {
                'user_id': self.user_id,
                'last_updated': datetime.now().isoformat(),
                'profile': self.profile
            }
            
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    async def invoking(self, messages, **kwargs) -> Context:
        """
        Called BEFORE the agent processes the request.
        Injects user profile and extracted context.
        
        Args:
            messages: Conversation messages
            **kwargs: Additional arguments
        
        Returns:
            Context: Context with user information
        """
        # Increment interaction counter
        self.session_data["interaction_count"] += 1
        
        instructions_parts = []
        
        # Inject user information
        user_info = self.profile.get('user_info', {})
        if user_info.get('name') or user_info.get('location') or user_info.get('profession'):
            info_items = []
            if user_info.get('name'):
                info_items.append(f"Name: {user_info['name']}")
            if user_info.get('location'):
                info_items.append(f"Location: {user_info['location']}")
            if user_info.get('profession'):
                info_items.append(f"Profession: {user_info['profession']}")
            
            if info_items:
                info_text = "\n".join([f"- {item}" for item in info_items])
                instructions_parts.append(f"""[USER PROFILE]:
{info_text}

This information persists between conversations. Use it to personalize your responses.""")
        
        # Inject extracted context (procedures, documents, dates)
        extracted = self.profile.get('extracted_data', {})
        context_items = []
        
        if extracted.get('procedures'):
            context_items.append(f"Consulted procedures: {', '.join(extracted['procedures'][-5:])}")
        if extracted.get('documents'):
            context_items.append(f"Mentioned documents: {', '.join(extracted['documents'][-5:])}")
        if extracted.get('important_dates'):
            context_items.append(f"Important dates: {', '.join(extracted['important_dates'][-5:])}")
        
        if context_items:
            context_text = "\n".join([f"- {item}" for item in context_items])
            instructions_parts.append(f"""[CONTEXT FROM PREVIOUS CONVERSATIONS]:
{context_text}

Relevant context from prior interactions.""")
        
        if instructions_parts:
            return Context(instructions="\n\n".join(instructions_parts))
        
        return Context()
    
    async def invoked(self, request_messages, response_messages, **kwargs) -> None:
        """
        Called AFTER the agent responds.
        Extracts relevant context with AI (does NOT save complete messages).
        
        Args:
            request_messages: Request messages
            response_messages: Response messages
            **kwargs: Additional arguments
        """
        # Extract last user message
        user_message = self._extract_last_user_message(request_messages)
        
        # Extract context with AI if available
        if self.ai_client and user_message:
            await self._extract_context_with_ai(user_message)
        
        # Save profile after each interaction
        self._save_profile()
    
    def _extract_last_user_message(self, request_messages) -> str:
        """
        Extracts last user message from request messages.
        
        Args:
            request_messages: Request messages
            
        Returns:
            str: Last user message or empty string
        """
        user_message = ""
        
        if isinstance(request_messages, (list, tuple)):
            for msg in reversed(list(request_messages)):
                if hasattr(msg, 'contents') and isinstance(msg.contents, list):
                    if len(msg.contents) > 0 and hasattr(msg.contents[0], 'text'):
                        user_message = str(msg.contents[0].text)
                        break
                elif hasattr(msg, 'text'):
                    user_message = str(msg.text)
                    break
                elif isinstance(msg, str):
                    user_message = msg
                    break
        elif isinstance(request_messages, str):
            user_message = request_messages
        
        return user_message
    
    async def _extract_context_with_ai(self, user_message: str) -> None:
        """
        Uses AI to extract relevant context from user message.
        Extracts: personal info, procedures, documents, dates.
        Does NOT save complete message, only keywords.
        
        Args:
            user_message: User message
        """
        if not user_message or len(user_message.strip()) < 3:
            return
        
        # Prompt to extract context
        analysis_prompt = f"""Extract information from this user message and return JSON.

User message: "{user_message}"

Extract these categories:
- user_info: name, location, profession
- procedures: procedures or services mentioned
- documents: documents mentioned
- important_dates: dates mentioned

Return JSON format:
{{
  "user_info": {{"name": "...", "location": "...", "profession": "..."}},
  "procedures": ["..."],
  "documents": ["..."],
  "important_dates": ["..."]
}}

Examples:
"My name is Juan, I live in Buenos Aires. I am an engineer."
→ {{"user_info": {{"name": "Juan", "location": "Buenos Aires", "profession": "engineer"}}}}

"How do I vote in New York?"
→ {{"procedures": ["voting in New York"]}}

"I need my ID and passport. Elections are March 15."
→ {{"procedures": ["voting"], "documents": ["ID", "passport"], "important_dates": ["March 15"]}}

Return only JSON, no explanation:"""
        
        try:
            # Use AI to analyze message
            deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-deployment")
            response = await self.ai_client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            # Parse AI response
            if not response.choices or len(response.choices) == 0:
                return
            
            ai_response = response.choices[0].message.content
            
            if not ai_response:
                return
            
            ai_response = ai_response.strip()
            
            # Try to extract JSON
            if "{" in ai_response and "}" in ai_response:
                start = ai_response.index("{")
                end = ai_response.rindex("}") + 1
                json_str = ai_response[start:end]
                
                extracted = json.loads(json_str)
                
                # Update user_info
                if 'user_info' in extracted:
                    user_info = extracted['user_info']
                    if user_info.get('name'):
                        self.profile['user_info']['name'] = user_info['name']
                    if user_info.get('location'):
                        self.profile['user_info']['location'] = user_info['location']
                    if user_info.get('profession'):
                        self.profile['user_info']['profession'] = user_info['profession']
                
                # Update procedures (avoid duplicates)
                if 'procedures' in extracted and extracted['procedures']:
                    for proc in extracted['procedures']:
                        if proc and proc not in self.profile['extracted_data']['procedures']:
                            self.profile['extracted_data']['procedures'].append(proc)
                
                # Update documents (avoid duplicates)
                if 'documents' in extracted and extracted['documents']:
                    for doc in extracted['documents']:
                        if doc and doc not in self.profile['extracted_data']['documents']:
                            self.profile['extracted_data']['documents'].append(doc)
                
                # Update important_dates (avoid duplicates)
                if 'important_dates' in extracted and extracted['important_dates']:
                    for date in extracted['important_dates']:
                        if date and date not in self.profile['extracted_data']['important_dates']:
                            self.profile['extracted_data']['important_dates'].append(date)
        
        except json.JSONDecodeError:
            pass
        except Exception:
            pass
    
    def update_profile(self, key: str, value: str):
        """
        Actualiza un campo del perfil de usuario.
        
        Args:
            key: Clave del campo (ej: "name", "location")
            value: Valor del campo
        """
        self.profile[key] = value
    
    def get_profile(self) -> dict:
        """
        Obtiene el perfil completo del usuario.
        
        Returns:
            dict: Perfil de usuario con user_info y extracted_data
        """
        return self.profile.copy()
    
    def get_user_info(self) -> dict:
        """
        Obtiene solo la información del usuario (nombre, ubicación, profesión).
        
        Returns:
            dict: Información del usuario
        """
        return self.profile.get('user_info', {}).copy()
    
    def get_extracted_data(self) -> dict:
        """
        Obtiene el contexto extraído (procedimientos, documentos, fechas).
        
        Returns:
            dict: Datos extraídos de conversaciones
        """
        return self.profile.get('extracted_data', {}).copy()
    
    def clear_profile(self):
        """Limpia el perfil de usuario."""
        self.profile = {
            "user_info": {
                "name": None,
                "location": None,
                "profession": None,
                "last_updated": None
            },
            "extracted_data": {
                "procedures": [],
                "documents": [],
                "important_dates": []
            }
        }
    
    def clear_all(self):
        """Limpia todo: perfil y estadísticas."""
        self.profile = {
            "user_info": {
                "name": None,
                "location": None,
                "profession": None,
                "last_updated": None
            },
            "extracted_data": {
                "procedures": [],
                "documents": [],
                "important_dates": []
            }
        }
        self.session_data = {
            "interaction_count": 0,
            "last_agent": None
        }
    
    def get_session_stats(self) -> dict:
        """
        Obtiene estadísticas de la sesión.
        
        Returns:
            dict: Estadísticas de la sesión
        """
        user_info = self.profile.get('user_info', {})
        extracted = self.profile.get('extracted_data', {})
        
        return {
            "user_id": self.user_id,
            "interaction_count": self.session_data["interaction_count"],
            "last_agent": self.session_data["last_agent"],
            "has_name": bool(user_info.get('name')),
            "has_location": bool(user_info.get('location')),
            "has_profession": bool(user_info.get('profession')),
            "procedures_count": len(extracted.get('procedures', [])),
            "documents_count": len(extracted.get('documents', [])),
            "dates_count": len(extracted.get('important_dates', []))
        }
