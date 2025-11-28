"""
Azure AI Foundry RAG Tools - Búsqueda usando Grounding with Data

Esta es una alternativa simplificada que usa la feature "Grounding with your data"
de Azure AI Foundry, que maneja automáticamente la indexación y búsqueda.

Ventajas vs azure_search_rag.py:
- ✅ No requiere script de indexación
- ✅ Configuración más simple
- ✅ Mantenimiento automático del índice
- ✅ Integración nativa con AI Foundry

Desventajas:
- ❌ Menos control sobre el índice
- ❌ Menos opciones de personalización

Prerequisites:
1. Azure AI Foundry project creado
2. Data source configurado en AI Foundry portal:
   - Ir a https://ai.azure.com
   - Tu proyecto → Data → Add data
   - Seleccionar Storage Account con PDFs
   - AI Foundry indexa automáticamente
3. Variable de entorno AZURE_AI_PROJECT_ENDPOINT configurada
"""

import sys
from pathlib import Path
from typing import Annotated, Optional
from pydantic import Field
from agent_framework import ai_function, HostedFileSearchTool

# Importar configuración centralizada
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from config.settings import settings


# ============================================================================
# AZURE AI FOUNDRY GROUNDING TOOLS
# ============================================================================

def create_foundry_file_search_tool() -> HostedFileSearchTool:
    """
    Crea una herramienta de búsqueda de archivos usando Azure AI Foundry.
    
    Esta tool usa el data source configurado en Azure AI Foundry portal.
    No requiere configuración adicional de Azure AI Search.
    
    Returns:
        HostedFileSearchTool: Tool configurada para búsqueda en documentos
    
    Raises:
        ValueError: Si AZURE_AI_PROJECT_ENDPOINT no está configurado
    
    Example:
        >>> tool = create_foundry_file_search_tool()
        >>> # El agente automáticamente usará esta tool cuando necesite
        >>> # buscar en documentos oficiales
    """
    if not settings.AZURE_AI_PROJECT.ENDPOINT:
        raise ValueError(
            "AZURE_AI_PROJECT_ENDPOINT no está configurado. "
            "Por favor, configura esta variable de entorno con tu project endpoint "
            "desde Azure AI Foundry portal."
        )
    
    # HostedFileSearchTool no acepta name ni description personalizados
    # Usa los valores por defecto del framework
    return HostedFileSearchTool()





# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_foundry_grounding_configured() -> bool:
    """
    Verifica si Azure AI Foundry está configurado.
    
    Returns:
        bool: True si AZURE_AI_PROJECT_ENDPOINT está configurado
    """
    return bool(settings.AZURE_AI_PROJECT.ENDPOINT)


def get_foundry_tools_for_agent(agent_type: str) -> list:
    """
    Obtiene las tools de file search apropiadas para un tipo de agente.
    
    Args:
        agent_type: Tipo de agente: "fact_checker", "educator", "guide"
    
    Returns:
        list: Lista de tools apropiadas para el agente
    
    Note:
        HostedFileSearchTool busca en todos los documentos indexados en AI Foundry.
        No se pueden crear tools especializadas por categoría con esta herramienta.
    """
    if not is_foundry_grounding_configured():
        return []
    
    # Una sola tool que busca en todos los documentos
    # AI Foundry maneja automáticamente qué documentos son relevantes
    return [create_foundry_file_search_tool()]


# ============================================================================
# USAGE EXAMPLES
# ============================================================================


