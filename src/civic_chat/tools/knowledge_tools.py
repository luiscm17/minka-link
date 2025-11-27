"""Civic knowledge search tools using Bing Search."""

import os
import logging
from typing import Annotated
from pydantic import Field
from agent_framework import ai_function

logger = logging.getLogger(__name__)


@ai_function(
    name="search_civic_info",
    description="Get U.S. civic and government information from official sources"
)
async def search_civic_info(
    query: Annotated[str, Field(description="The civic question to search for")],
    language: Annotated[str, Field(description="Language code (e.g., 'en', 'es')")] = "en"
) -> str:
    """Provide civic information and search guidance.
    
    Fallback tool when Bing Search is not available.
    
    Args:
        query: The user's civic question
        language: Language code for the response
    
    Returns:
        Civic information with official source citations
    """
    lang = language.split("-")[0].lower()
    query_lower = query.lower()
    
    # Basic knowledge base for common queries
    knowledge_base = {
        "voting": {
            "en": """**Voting Requirements:**
To vote in most U.S. elections, you must:
- Be a U.S. citizen
- Be at least 18 years old by Election Day
- Meet your state's residency requirements

**Registration:**
You can register to vote online, by mail, or in person at your local election office or DMV.

**Official Sources:**
- USA.gov Voting: https://www.usa.gov/how-to-vote
- Vote.gov: https://vote.gov
- Register to Vote: https://www.usa.gov/register-to-vote""",
            "es": """**Requisitos para Votar:**
Para votar en la mayoría de las elecciones en EE. UU., debe:
- Ser ciudadano estadounidense
- Tener al menos 18 años para el día de las elecciones
- Cumplir con los requisitos de residencia de su estado

**Registro:**
Puede registrarse para votar en línea, por correo o en persona en su oficina electoral local o DMV.

**Fuentes Oficiales:**
- USA.gov Votación: https://www.usa.gov/espanol/como-votar
- Vote.gov: https://vote.gov
- Registrarse: https://www.usa.gov/espanol/registrarse-para-votar"""
        },
        "government": {
            "en": """**U.S. Government Structure:**
The U.S. government has three branches:

1. **Legislative Branch (Congress)**
   - Makes laws
   - Senate and House of Representatives

2. **Executive Branch (President)**
   - Enforces laws
   - Includes federal agencies

3. **Judicial Branch (Supreme Court)**
   - Interprets laws
   - Federal court system

**Official Sources:**
- Branches of Government: https://www.usa.gov/branches-of-government
- Congress.gov: https://www.congress.gov""",
            "es": """**Estructura del Gobierno de EE. UU.:**
El gobierno de EE. UU. tiene tres poderes:

1. **Poder Legislativo (Congreso)**
   - Hace las leyes
   - Senado y Cámara de Representantes

2. **Poder Ejecutivo (Presidente)**
   - Ejecuta las leyes
   - Incluye agencias federales

3. **Poder Judicial (Corte Suprema)**
   - Interpreta las leyes
   - Sistema de cortes federales

**Fuentes Oficiales:**
- Ramas del Gobierno: https://www.usa.gov/espanol/ramas-del-gobierno
- Congress.gov: https://www.congress.gov"""
        }
    }
    
    # Detect topic
    if any(word in query_lower for word in ["vote", "voting", "voter", "votar", "registro", "register"]):
        topic = "voting"
    elif any(word in query_lower for word in ["government", "gobierno", "branch", "poder", "congress", "congreso"]):
        topic = "government"
    else:
        # General search guidance
        if lang == "es":
            return f"""Para responder "{query}", busca información en:

**Fuentes Oficiales Recomendadas:**
- USA.gov en español: https://www.usa.gov/espanol
- Vote.gov: https://vote.gov
- Congress.gov: https://www.congress.gov

**Estrategia de Búsqueda:**
1. Busca en sitios .gov oficiales
2. Verifica información de múltiples fuentes
3. Prioriza información reciente

Siempre cita las fuentes oficiales en tu respuesta."""
        else:
            return f"""To answer "{query}", search for information at:

**Recommended Official Sources:**
- USA.gov: https://www.usa.gov
- Vote.gov: https://vote.gov
- Congress.gov: https://www.congress.gov

**Search Strategy:**
1. Search official .gov sites
2. Verify information from multiple sources
3. Prioritize recent information

Always cite official sources in your response."""
    
    # Return knowledge base entry
    return knowledge_base.get(topic, {}).get(lang, knowledge_base.get(topic, {}).get("en", ""))
