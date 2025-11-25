# src/civic_chat/agents/memory/memory_manager.py
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from agent_framework import ContextProvider, Context
from openai import AsyncAzureOpenAI

class CivicMemoryManager(ContextProvider):
    """Gestiona la memoria a largo plazo del asistente cívico usando IA."""
    
    def __init__(self, user_id: str, ai_client: AsyncAzureOpenAI):
        self.user_id = user_id
        self.ai_client = ai_client
        self.memory_file = f"user_data/{user_id}_memory.json"
        self.user_profile = self._initialize_profile()
        self._ensure_user_data_dir()
        self._load_memory()

    def _initialize_profile(self) -> Dict[str, Any]:
        """Inicializa el perfil del usuario con la estructura correcta."""
        return {
            'user_info': {
                'name': None,
                'location': None,
                'last_updated': None
            },
            'extracted_data': {
                'procedures': [],
                'documents': [],
                'important_dates': []
            }
        }

    def _ensure_user_data_dir(self) -> None:
        """Asegura que el directorio user_data exista."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)

    def _load_memory(self) -> None:
        """Carga la memoria del usuario desde el archivo."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._merge_profiles(data.get('profile', {}))
                print(f"Memoria cargada: {self.memory_file}")
            else:
                print(f"Nueva memoria creada para usuario: {self.user_id}")
        except Exception as e:
            print(f"Error cargando memoria: {e}")

    def _merge_profiles(self, saved_profile: Dict[str, Any]) -> None:
        """Combina el perfil guardado con el actual."""
        if 'user_info' in saved_profile:
            self.user_profile['user_info'].update(
                {k: v for k, v in saved_profile['user_info'].items() if v}
            )
        if 'extracted_data' in saved_profile:
            for key in self.user_profile['extracted_data']:
                if key in saved_profile['extracted_data']:
                    # Evitar duplicados
                    new_items = [
                        item for item in saved_profile['extracted_data'][key] 
                        if item not in self.user_profile['extracted_data'][key]
                    ]
                    self.user_profile['extracted_data'][key].extend(new_items)

    async def _extract_relevant_info(self, message: str) -> Dict[str, Any]:
        """Extrae información relevante del mensaje usando IA."""
        if not message or len(message) < 3:
            return {}

        try:
            prompt = """Analiza este mensaje y extrae SOLO información relevante para un asistente cívico:
- Nombre de la persona (solo si se menciona explícitamente)
- Ubicación/ciudad (solo si se menciona explícitamente)
- Tipo de trámite o consulta
- Documentos mencionados
- Fechas importantes

Responde en formato JSON. Si no hay información para algún campo, déjalo vacío.
Ejemplo: {"name": "", "location": "Lima", "procedure": "renovación de DNI", "documents": ["DNI"], "important_dates": []}

JSON only, no explanation:"""
            
            response = await self.ai_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "Eres un asistente que extrae información relevante de mensajes."},
                    {"role": "user", "content": f"{prompt}\n\nMensaje: {message}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "{" in result and "}" in result:
                start = result.index("{")
                end = result.rindex("}") + 1
                json_str = result[start:end]
                extracted = json.loads(json_str)
                return extracted
            
            return {}
            
        except Exception as e:
            # Silent fail - no need to spam console
            return {}

    async def update_memory(self, message: str) -> None:
        """Actualiza la memoria con la información del mensaje."""
        if not message:
            return

        # Extraer información relevante
        extracted = await self._extract_relevant_info(message)
        if not extracted:
            return

        # Actualizar información básica
        if extracted.get('name'):
            self.user_profile['user_info']['name'] = extracted['name']
        if extracted.get('location'):
            self.user_profile['user_info']['location'] = extracted['location']

        # Actualizar datos extraídos
        if extracted.get('procedure'):
            self._add_unique_item('procedures', extracted['procedure'])
        if extracted.get('documents'):
            for doc in extracted['documents']:
                self._add_unique_item('documents', doc)
        if extracted.get('important_dates'):
            for date in extracted['important_dates']:
                self._add_unique_item('important_dates', date)

        # Actualizar timestamp
        self.user_profile['user_info']['last_updated'] = datetime.now().isoformat()
        self._save_memory()

    def _add_unique_item(self, category: str, item: Any) -> None:
        """Añade un ítem a una categoría si no existe."""
        if item and item not in self.user_profile['extracted_data'][category]:
            self.user_profile['extracted_data'][category].append(item)

    def _save_memory(self) -> None:
        """Guarda la memoria en el archivo."""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'user_id': self.user_id,
                    'last_updated': datetime.now().isoformat(),
                    'profile': self.user_profile
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando memoria: {e}")

    async def invoking(self, messages, **kwargs) -> Context:
        """Proporciona el contexto al agente."""
        context = Context()
        
        # Solo inyectar información si tenemos datos relevantes
        if any(self.user_profile['user_info'].values()):
            context.instructions = self._build_context_instructions()
            
        return context

    def _build_context_instructions(self) -> str:
        """Construye las instrucciones de contexto para el agente."""
        instructions = ["[INFORMACIÓN DEL USUARIO]"]
        
        # Información básica
        if self.user_profile['user_info']['name']:
            instructions.append(f"Nombre: {self.user_profile['user_info']['name']}")
        if self.user_profile['user_info']['location']:
            instructions.append(f"Ubicación: {self.user_profile['user_info']['location']}")
        
        # Datos extraídos
        if any(self.user_profile['extracted_data'].values()):
            instructions.append("\nInformación relevante:")
            for category, items in self.user_profile['extracted_data'].items():
                if items:
                    items_str = ", ".join(str(i) for i in items if i)
                    instructions.append(f"- {category.capitalize()}: {items_str}")
        
        instructions.append("\nUsa esta información para personalizar tus respuestas cuando sea relevante.")
        return "\n".join(instructions)

    async def invoked(self, request_messages, response_messages, **kwargs) -> None:
        """Procesa los mensajes después de la respuesta del agente."""
        if not request_messages:
            return

        # Obtener el último mensaje del usuario
        # Basado en el ejemplo funcional de new_12_long_term_memory_AI.py
        user_message = ""
        if isinstance(request_messages, (list, tuple)):
            for msg in reversed(list(request_messages)):
                # Intentar diferentes formas de extraer el texto del mensaje
                if hasattr(msg, 'contents') and isinstance(msg.contents, list):
                    if len(msg.contents) > 0 and hasattr(msg.contents[0], 'text'):
                        user_message = str(msg.contents[0].text)
                        break
                elif hasattr(msg, 'content') and msg.content:
                    user_message = str(msg.content)
                    break
                elif hasattr(msg, 'text'):
                    user_message = str(msg.text)
                    break

        if user_message and len(user_message) >= 3:
            await self.update_memory(user_message)