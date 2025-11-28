"""
Bing Search Tools - Herramientas de búsqueda web para verificación y contexto

Estas tools proporcionan capacidades de búsqueda web usando Bing Search,
especialmente útiles para verificar información y buscar fuentes oficiales.

Prerequisites:
1. Conexión de "Grounding with Bing Search" en Azure AI Foundry
2. Variable de entorno BING_CONNECTION_ID configurada

Para configurar:
1. Ve a Azure AI Foundry portal (https://ai.azure.com)
2. Navega a "Connected resources" de tu proyecto
3. Agrega conexión "Grounding with Bing Search"
4. Copia el connection ID y configúralo en .env
"""

import sys
from pathlib import Path
from typing import Annotated, Optional
from pydantic import Field
from agent_framework import ai_function, HostedWebSearchTool

# Importar configuración centralizada
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from config.settings import settings


# ============================================================================
# BING WEB SEARCH TOOL (Hosted)
# ============================================================================

def create_bing_search_tool(
    name: str = "Bing Web Search",
    description: str = "Search the web for current information using Bing"
) -> HostedWebSearchTool:
    """
    Crea una herramienta de búsqueda web usando Bing Grounding.
    
    Esta es una "hosted tool" proporcionada por Azure AI que no requiere
    implementación personalizada. El connection ID se toma de settings.
    
    Args:
        name: Nombre de la tool
        description: Descripción de qué hace la tool
    
    Returns:
        HostedWebSearchTool: Tool configurada para búsqueda web
    
    Raises:
        ValueError: Si BING_CONNECTION_ID no está configurado
    """
    if not settings.BING_SEARCH.CONNECTION_ID:
        raise ValueError(
            "BING_CONNECTION_ID no está configurado. "
            "Por favor, configura esta variable de entorno con tu Bing connection ID "
            "desde Azure AI Foundry portal."
        )
    
    return HostedWebSearchTool(
        name=name,
        description=description
    )


def create_gov_sources_search_tool() -> HostedWebSearchTool:
    """
    Crea una herramienta de búsqueda especializada en fuentes gubernamentales.
    
    Esta tool está optimizada para buscar información en sitios .gov,
    ideal para el Fact Checker agent.
    
    Returns:
        HostedWebSearchTool: Tool configurada para búsqueda en fuentes oficiales
    """
    return HostedWebSearchTool(
        name="Official Sources Search",
        description=(
            "Search official government sources (.gov domains) for verified civic information. "
            "Use this to verify facts, find official policies, and cite authoritative sources. "
            "Prioritizes results from nyc.gov, ny.gov, and other government websites."
        )
    )


def create_news_search_tool() -> HostedWebSearchTool:
    """
    Crea una herramienta de búsqueda de noticias actuales.
    
    Útil para obtener información sobre eventos recientes, cambios en políticas,
    o noticias relacionadas con temas cívicos.
    
    Returns:
        HostedWebSearchTool: Tool configurada para búsqueda de noticias
    """
    return HostedWebSearchTool(
        name="News Search",
        description=(
            "Search recent news articles for current events and updates. "
            "Use this to find information about recent policy changes, elections, "
            "or civic events in NYC."
        )
    )


# ============================================================================
# CUSTOM SEARCH FUNCTIONS (Alternativa si no tienes Bing connection)
# ============================================================================

@ai_function(
    name="search_nyc_gov_sites",
    description="Busca información específicamente en sitios .gov de NYC"
)
def search_nyc_gov_sites(
    query: Annotated[str, Field(description="Consulta de búsqueda")],
    site: Annotated[str, Field(description="Sitio específico: nyc.gov, vote.nyc, etc.")] = "nyc.gov"
) -> dict:
    """
    Búsqueda simulada en sitios gubernamentales de NYC.
    
    NOTA: Esta es una implementación de respaldo. En producción, usa
    create_gov_sources_search_tool() con Bing connection real.
    
    Args:
        query: Término de búsqueda
        site: Sitio gubernamental específico
    
    Returns:
        dict: Resultados de búsqueda simulados
    """
    # Datos simulados - en producción usar Bing Custom Search API
    simulated_results = {
        "query": query,
        "site": site,
        "results": [
            {
                "title": f"Información oficial sobre {query}",
                "url": f"https://{site}/search?q={query.replace(' ', '+')}",
                "snippet": f"Información verificada sobre {query} en el sitio oficial de NYC.",
                "source": site,
                "verified": True
            }
        ],
        "note": "Estos son resultados simulados. Para información actualizada, visita directamente el sitio oficial.",
        "direct_links": {
            "nyc.gov": "https://www.nyc.gov/",
            "vote.nyc": "https://vote.nyc/",
            "portal.311.nyc.gov": "https://portal.311.nyc.gov/"
        }
    }
    
    return simulated_results


@ai_function(
    name="verify_with_official_source",
    description="Verifica una afirmación buscando en fuentes oficiales"
)
def verify_with_official_source(
    claim: Annotated[str, Field(description="Afirmación a verificar")],
    topic: Annotated[str, Field(description="Tema: voting, housing, transportation, etc.")] = "general"
) -> dict:
    """
    Verifica una afirmación contra fuentes oficiales conocidas.
    
    NOTA: Esta es una implementación de respaldo. En producción, usa
    create_gov_sources_search_tool() con Bing connection real.
    
    Args:
        claim: Afirmación a verificar
        topic: Tema de la afirmación
    
    Returns:
        dict: Resultado de verificación con fuentes
    """
    # Mapeo de temas a fuentes oficiales
    official_sources = {
        "voting": {
            "primary": "https://vote.nyc/",
            "secondary": "https://www.elections.ny.gov/",
            "description": "NYC Board of Elections y NY State Board of Elections"
        },
        "housing": {
            "primary": "https://www1.nyc.gov/site/hpd/",
            "secondary": "https://www1.nyc.gov/site/rentguidelinesboard/",
            "description": "NYC Housing Preservation & Development"
        },
        "transportation": {
            "primary": "https://www.nyc.gov/html/dot/",
            "secondary": "https://new.mta.info/",
            "description": "NYC DOT y MTA"
        },
        "311": {
            "primary": "https://portal.311.nyc.gov/",
            "secondary": "https://www.nyc.gov/311/",
            "description": "NYC 311 Services"
        },
        "general": {
            "primary": "https://www.nyc.gov/",
            "secondary": "https://www.ny.gov/",
            "description": "NYC.gov y NY.gov"
        }
    }
    
    source_info = official_sources.get(topic.lower(), official_sources["general"])
    
    return {
        "claim": claim,
        "topic": topic,
        "verification_status": "requires_manual_check",
        "recommended_sources": source_info,
        "instructions": [
            f"Visita {source_info['primary']} para verificar esta información",
            "Busca en la sección relevante del sitio oficial",
            "Verifica la fecha de la información para asegurar que esté actualizada"
        ],
        "note": (
            "Esta es una guía de verificación. Para verificación automática en tiempo real, "
            "configura BING_CONNECTION_ID en tu entorno."
        )
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_bing_search_configured() -> bool:
    """
    Verifica si Bing Search está configurado.
    
    Returns:
        bool: True si BING_CONNECTION_ID está configurado
    """
    return settings.is_bing_configured()


def get_search_tools_for_agent(agent_type: str) -> list:
    """
    Obtiene las tools de búsqueda apropiadas para un tipo de agente.
    
    Args:
        agent_type: Tipo de agente: "fact_checker", "educator", "general"
    
    Returns:
        list: Lista de tools apropiadas para el agente
    """
    if not is_bing_search_configured():
        # Usar funciones de respaldo si Bing no está configurado
        if agent_type == "fact_checker":
            return [search_nyc_gov_sites, verify_with_official_source]
        elif agent_type == "educator":
            return [search_nyc_gov_sites]
        else:
            return []
    
    # Usar Bing Search si está configurado
    if agent_type == "fact_checker":
        return [
            create_gov_sources_search_tool(),
            create_bing_search_tool(
                name="General Web Search",
                description="Search the web for additional context and information"
            )
        ]
    elif agent_type == "educator":
        return [
            create_gov_sources_search_tool(),
            create_news_search_tool()
        ]
    else:
        return [create_bing_search_tool()]

