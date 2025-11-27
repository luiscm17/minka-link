# src/civic_chat/agents/memory/memory_manager.py
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from agent_framework import ContextProvider, Context
from openai import AsyncAzureOpenAI

class CivicMemoryManager(ContextProvider):
    """
    AI-powered memory manager for Civic Chat - Structured for civic procedures.
    """
    
    def __init__(self, user_id: str, ai_client: AsyncAzureOpenAI):
        self.user_id = user_id
        self.ai_client = ai_client
        self.memory_file = f"user_data/{user_id}_memory.json"
        self.user_profile = self._initialize_profile()
        
        # Ensure user_data directory exists
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        # Load existing profile from file
        self._load_profile()
    
    def _initialize_profile(self) -> Dict[str, Any]:
        """Initialize the user profile with the correct structure."""
        return {
            'user_info': {
                'name': None,
                'location': None,
                'profession': None,
                'last_updated': None
            },
            'extracted_data': {
                'procedures': [],
                'documents': [],
                'important_dates': []
            }
        }
    
    def _load_profile(self):
        """Load user profile from JSON file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    saved_profile = data.get('profile', {})
                    # Merge with initialized structure
                    self._merge_profiles(saved_profile)
            except Exception as e:
                pass
    
    def _merge_profiles(self, saved_profile: Dict[str, Any]) -> None:
        """Merge saved profile with current structure."""
        if 'user_info' in saved_profile:
            self.user_profile['user_info'].update(
                {k: v for k, v in saved_profile['user_info'].items() if v}
            )
        if 'extracted_data' in saved_profile:
            for key in self.user_profile['extracted_data']:
                if key in saved_profile['extracted_data']:
                    # Avoid duplicates
                    new_items = [
                        item for item in saved_profile['extracted_data'][key] 
                        if item not in self.user_profile['extracted_data'][key]
                    ]
                    self.user_profile['extracted_data'][key].extend(new_items)
    
    def _save_profile(self):
        """Save user profile to JSON file."""
        try:
            data = {
                'user_id': self.user_id,
                'last_updated': datetime.now().isoformat(),
                'profile': self.user_profile
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Silent fail for production
            pass
    
    def _add_unique_item(self, category: str, item: Any) -> None:
        """Add an item to a category if it doesn't exist."""
        if item and item not in self.user_profile['extracted_data'][category]:
            self.user_profile['extracted_data'][category].append(item)
    
    async def invoking(self, messages, **kwargs) -> Context:
        """Inject profile BEFORE agent processes request."""
        
        # Only inject information if we have relevant data
        if any(self.user_profile['user_info'].values()):
            context = Context()
            context.instructions = self._build_context_instructions()
            return context
            
        return Context()

    def _build_context_instructions(self) -> str:
        """Build context instructions for the agent."""
        instructions = ["[INFORMACIÓN DEL USUARIO]"]
        
        # Basic information
        if self.user_profile['user_info']['name']:
            instructions.append(f"Nombre: {self.user_profile['user_info']['name']}")
        if self.user_profile['user_info']['location']:
            instructions.append(f"Ubicación: {self.user_profile['user_info']['location']}")
        if self.user_profile['user_info']['profession']:
            instructions.append(f"Profesión: {self.user_profile['user_info']['profession']}")
        
        # Extracted data
        if any(self.user_profile['extracted_data'].values()):
            instructions.append("\\nInformación relevante:")
            for category, items in self.user_profile['extracted_data'].items():
                if items:
                    items_str = ", ".join(str(i) for i in items if i)
                    instructions.append(f"- {category.capitalize()}: {items_str}")
        
        instructions.append("\\nUsa esta información para personalizar tus respuestas cuando sea relevante.")
        return "\\n".join(instructions)
    
    async def invoked(self, request_messages, response_messages, **kwargs) -> None:
        """Let AI extract important information AFTER conversation."""
        
        # Get the FIRST user message (original input), not the classifier output
        user_message = ""
        if isinstance(request_messages, (list, tuple)):
            for msg in request_messages:  # Don't reverse, get the first one
                if hasattr(msg, 'contents') and isinstance(msg.contents, list):
                    if len(msg.contents) > 0 and hasattr(msg.contents[0], 'text'):
                        text = str(msg.contents[0].text)
                        # Skip classifier outputs (single words like "GENERAL", "COMPLAINT", etc.)
                        if len(text) > 3 and not text.isupper():
                            user_message = text
                            break
                elif hasattr(msg, 'content') and msg.content:
                    text = str(msg.content)
                    # Skip classifier outputs
                    if len(text) > 3 and not text.isupper():
                        user_message = text
                        break
                elif hasattr(msg, 'text'):
                    text = str(msg.text)
                    # Skip classifier outputs
                    if len(text) > 3 and not text.isupper():
                        user_message = text
                        break
        
        if not user_message or len(user_message) < 3:
            return
        

        
        # Ask AI to extract important information
        analysis_prompt = f"""Analyze this user message and extract any personal information worth remembering for future conversations.

User message: "{user_message}"

Current profile: {self.user_profile if self.user_profile else "Empty"}

Extract ONLY factual information about the user (name, location, profession, civic procedures, documents, dates).
Return as JSON format: {{"key": "value", "key2": "value2"}}
If nothing important, return empty: {{}}

Examples:
- "My name is Alice" → {{"name": "Alice"}}
- "I live in Boston" → {{"location": "Boston"}}
- "I work as a teacher" → {{"profession": "teacher"}}
- "I need to renew my passport" → {{"procedure": "passport renewal", "documents": ["passport"]}}
- "como puedo votar en new york?" → {{"procedure": "voting in New York"}}
- "y si quiero hacer una denuncia?" → {{"procedure": "filing complaints"}}
- "How are you?" → {{}}

Extract only NEW or UPDATED information. Be concise with values.
JSON only, no explanation:"""

        try:
            # Use AI to analyze the message
            response = await self.ai_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini"),
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=200,
                timeout=30
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Try to extract JSON
            if "{" in ai_response and "}" in ai_response:
                start = ai_response.index("{")
                end = ai_response.rindex("}") + 1
                json_str = ai_response[start:end]
                
                extracted = json.loads(json_str)
                
                # Update profile with extracted information
                if extracted:
                    updated = False
                    for key, value in extracted.items():
                        if key in ['name', 'location', 'profession']:
                            # Handle basic user info
                            if value and self.user_profile['user_info'].get(key) != value:
                                self.user_profile['user_info'][key] = value
                                updated = True
                        elif key == 'procedure' and value:
                            # Handle procedures
                            self._add_unique_item('procedures', value)
                            updated = True
                        elif key == 'documents' and value:
                            # Handle documents
                            for doc in value if isinstance(value, list) else [value]:
                                self._add_unique_item('documents', doc)
                                updated = True
                        elif key == 'important_dates' and value:
                            # Handle dates
                            for date in value if isinstance(value, list) else [value]:
                                self._add_unique_item('important_dates', date)
                                updated = True

                    if updated:
                        # Update timestamp
                        self.user_profile['user_info']['last_updated'] = datetime.now().isoformat()
                        self._save_profile()
        
        except Exception as e:
            # Silent fail for production
            pass