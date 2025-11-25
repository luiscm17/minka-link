import asyncio
import os
from dotenv import load_dotenv
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
# from azure.ai.projects.aio import AIProjectClient

from .agents.language_agent import detect_language, translate_text
from .agents.knowledge_agent import get_civic_knowledge
from .agents.memory.memory_manager import CivicMemoryManager

# En src/civic_chat/main.py (solo la parte relevante)
import hashlib
import getpass

# Load environment variables from .env file
load_dotenv()

def get_user_identifier() -> str:
    """Obtiene un identificador único para el usuario actual."""
    try:
        # En una aplicación real, esto vendría de la autenticación
        username = getpass.getuser()
        return f"usr_{hashlib.md5(username.encode()).hexdigest()[:8]}"
    except Exception:
        # Si falla, generar un ID aleatorio
        import random
        import string
        return f"anon_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

async def main():
    """Run the Civic Chat Assistant."""
    print("Asistente Cívico (escribe 'salir' para terminar)")

    try:
        # Obtener identificador único para el usuario
        user_id = get_user_identifier()
        print(f"ID de sesión: {user_id}")
        # Crear gestor de memoria
        memory_manager = CivicMemoryManager(user_id=user_id)  # En una app real, usa el ID del usuario autenticado
        
        # Create chat client with explicit parameters
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT no está configurado en las variables de entorno")
            
        # Inicializar el cliente con AzureCliCredential
        chat_client = AzureOpenAIChatClient(
            endpoint=endpoint,
            credential=AzureCliCredential(),
            api_version="2023-05-15"
        )
        
        agent = chat_client.create_agent(
            name="CivicAssistant",
            instructions=(
                "Eres un asistente útil que proporciona información sobre procesos cívicos. "
                "Puedes detectar idiomas, traducir texto y proporcionar información sobre requisitos de votación, "
                "registro y fechas electorales. Siempre responde en el idioma de la consulta del usuario.\n"
                "Herramientas disponibles:\n"
                "- detect_language: Detectar el idioma del texto\n"
                "- translate_text: Traducir texto entre idiomas\n"
                "- get_civic_knowledge: Obtener información sobre procesos cívicos\n"
                "\nUsa la información del perfil del usuario cuando sea relevante."
            ),
            tools=[detect_language, translate_text, get_civic_knowledge],
            context_providers=[memory_manager]  # Añadir el gestor de memoria
        )

        async with agent:
            while True:
                try:
                    user_input = input("\nTú: ").strip()
                    if user_input.lower() in ['salir', 'exit']:
                        break

                    # Obtener respuesta del agente
                    response = await agent.run(user_input)
                    print(f"\nAsistente: {response.text}")
                    
                except KeyboardInterrupt:
                    print("\nSaliendo...")
                    break
                except Exception as e:
                    print(f"\nError: {str(e)}")
                    continue

    except Exception as e:
        print(f"Failed to initialize the chat client: {str(e)}")
        print("Please check your Azure credentials and environment variables.")

if __name__ == "__main__":
    asyncio.run(main())