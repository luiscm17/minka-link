# src/app/agent_client.py
import os
import logging
from typing import Optional, Dict, Any

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder

ENDPOINT = os.getenv("AZURE_FOUNDRY_ENDPOINT")
AGENT_ID = os.getenv("AZURE_FOUNDRY_AGENT_ID")

_project_client: Optional[AIProjectClient] = None

def get_project_client() -> AIProjectClient:
    """Devuelve un cliente singleton para el proyecto de Azure AI."""
    global _project_client

    if not ENDPOINT or not AGENT_ID:
        logging.warning(
            "Faltan AZURE_FOUNDRY_ENDPOINT o AZURE_FOUNDRY_AGENT_ID en variables de entorno"
        )

    if _project_client is None:
        credential = DefaultAzureCredential()
        _project_client = AIProjectClient(
            endpoint=ENDPOINT,
            credential=credential,
        )
        logging.info("AIProjectClient inicializado contra %s", ENDPOINT)

    return _project_client


def chat_with_agent(
    user_message: str,
    thread_id: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Envía un mensaje al agente definido en Azure AI Foundry (Escenario 2).

    :param user_message: texto del ciudadano
    :param thread_id: id de hilo (si None, se crea uno nuevo)
    :param extra_context: opcional, contexto adicional (comunaId, canal, idioma, etc.)
    :return: { "threadId": str, "reply": str }
    """
    client = get_project_client()
    agents = client.agents

    # 1) Obtenemos el agente remoto
    agent = agents.get_agent(AGENT_ID)

    # 2) Creamos o recuperamos thread
    if thread_id:
        thread = agents.threads.get(thread_id)
    else:
        thread = agents.threads.create()

    # 3) Construimos contenido del mensaje del usuario
    content = user_message
    if extra_context:
        # Si querés, podés incrustar contexto de manera simple
        # o más adelante usar tools / metadata
        content = f"{user_message}\n\n[contexto]: {extra_context}"

    # 4) Agregamos mensaje del usuario al thread
    agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=content,
    )

    # 5) Ejecutamos el run y esperamos a que el agente termine
    run = agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
    )

    if run.status == "failed":
        logging.error("Run falló: %s", run.last_error)
        raise RuntimeError(f"Run failed: {run.last_error}")

    # 6) Leemos los mensajes del thread en orden ascendente
    messages = list(
        agents.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING,
        )
    )

    # 7) Tomamos el último mensaje del asistente
    reply_text = ""
    for message in reversed(messages):
        if message.role == "assistant" and getattr(message, "text_messages", None):
            reply_text = message.text_messages[-1].text.value
            break

    return {
        "threadId": thread.id,
        "reply": reply_text,
    }
