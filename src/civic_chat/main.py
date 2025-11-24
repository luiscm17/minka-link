import asyncio
import os
from dotenv import load_dotenv
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
# from azure.ai.projects.aio import AIProjectClient

from .agents.language_agent import detect_language, translate_text
from .agents.knowledge_agent import get_civic_knowledge

# Load environment variables from .env file
load_dotenv()


async def main():
    """Run the Civic Chat Assistant."""
    print("Civic Chat Assistant (type 'exit' to quit)")

    try:
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
                "You are a helpful assistant that provides information about civic processes. "
                "Puedes detectar idiomas, traducir texto y proporcionar información sobre requisitos de votación, "
                "registro y fechas electorales. Siempre responde en el idioma de la consulta del usuario.\n"
                "Herramientas disponibles:\n"
                "- detect_language: Detect the language of the input text\n"
                "- translate_text: Translate text between languages\n"
                "- get_civic_knowledge: Get information about civic processes"
            ),
            tools=[detect_language, translate_text, get_civic_knowledge]
        )

        async with agent:
            while True:
                try:
                    user_input = input("\nYou: ").strip()
                    if user_input.lower() == 'exit':
                        break

                    # Get response from the agent
                    response = await agent.run(user_input)
                    print(f"\nAssistant: {response.text}")
                    
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
                except Exception as e:
                    print(f"\nError: {str(e)}")
                    continue

    except Exception as e:
        print(f"Failed to initialize the chat client: {str(e)}")
        print("Please check your Azure credentials and environment variables.")

if __name__ == "__main__":
    asyncio.run(main())