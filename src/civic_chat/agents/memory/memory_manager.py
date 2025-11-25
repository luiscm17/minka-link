# src/civic_chat/agents/memory/memory_manager.py
import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional
from agent_framework import ContextProvider, Context, ChatMessage

class CivicMemoryManager(ContextProvider):
    """
    Gestiona la memoria a largo plazo para el asistente cívico.
    Almacena preferencias e información importante en un archivo JSON.
    """
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.memory_file = f"user_data/{user_id}_memory.json"
        self.user_profile = {}
        self._ensure_user_data_dir()
        self._load_memory()
    
    def _ensure_user_data_dir(self):
        """Asegura que el directorio user_data exista."""
        os.makedirs("user_data", exist_ok=True)
    
    def _load_memory(self) -> None:
        """Carga la memoria del usuario desde el archivo."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_profile = data.get('profile', {})
                    print(f"[MEMORY] Perfil cargado para {self.user_id}")
        except Exception as e:
            print(f"[ERROR] Error cargando memoria: {e}")
            self.user_profile = {}
    
    def _save_memory(self) -> None:
        """Guarda la memoria del usuario en el archivo."""
        try:
            data = {
                'user_id': self.user_id,
                'last_updated': datetime.now().isoformat(),
                'profile': self.user_profile
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Error guardando memoria: {e}")
    
    async def invoking(self, messages, **kwargs) -> Context:
        """Inyecta el perfil ANTES de procesar la solicitud."""
        if not self.user_profile:
            return Context()
            
        profile_text = "\n".join([f"- {k}: {v}" for k, v in self.user_profile.items()])
        return Context(instructions=f"""
[INFORMACIÓN DEL USUARIO - MEMORIA A LARGO PLAZO]:
{profile_text}

IMPORTANTE: Esta información persiste entre conversaciones.
Úsala para personalizar respuestas cuando sea relevante.
""")
    
    async def invoked(self, request_messages, response_messages, **kwargs) -> None:
        """Extrae y guarda información importante de la conversación."""
        if not request_messages:
            return
            
        # Obtener el último mensaje del usuario
        user_message = ""
        if isinstance(request_messages, (list, tuple)):
            for msg in reversed(list(request_messages)):
                if hasattr(msg, 'content') and msg.content:
                    user_message = str(msg.content)
                    break
                elif hasattr(msg, 'text'):
                    user_message = str(msg.text)
                    break
        
        if not user_message or len(user_message) < 3:
            return
        
        # Actualizar memoria con información relevante
        self._update_memory_from_message(user_message)
        self._save_memory()  # Asegurarse de guardar después de actualizar
    
    def _update_memory_from_message(self, message: str) -> None:
        """Actualiza la memoria con el mensaje del usuario."""
        if not message or len(message) < 3:
            return
    
    # Guardar el mensaje completo en el historial
        if 'conversation_history' not in self.user_profile:
            self.user_profile['conversation_history'] = []
    
    # Mantener solo los últimos 50 mensajes para evitar archivos muy grandes
        self.user_profile['conversation_history'].append({
            'timestamp': datetime.now().isoformat(),
            'message': message
        })
    
        if len(self.user_profile['conversation_history']) > 50:
            self.user_profile['conversation_history'] = self.user_profile['conversation_history'][-50:]
    
        print(f"[MEMORY] Conversación actualizada")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Obtiene una preferencia específica del usuario."""
        return self.user_profile.get(key, default)
    
    def update_preference(self, key: str, value: Any) -> None:
        """Actualiza una preferencia del usuario."""
        self.user_profile[key] = value
        self._save_memory()