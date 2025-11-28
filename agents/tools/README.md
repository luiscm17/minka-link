# Tools para Agentes de Minka Link

Este directorio contiene las herramientas (tools) que los agentes pueden usar para acceder a información externa y realizar acciones específicas.

## Tools Disponibles

### 1. NYC Services (`nyc_services.py`)

Herramientas para acceder a servicios gubernamentales de NYC:

- `find_polling_location()`: Encuentra lugares de votación
- `check_voter_registration()`: Verifica registro de votantes
- `search_311_services()`: Busca servicios 311
- `find_government_office()`: Encuentra oficinas gubernamentales
- `get_document_requirements()`: Lista documentos necesarios para trámites

### 2. Bing Search (`bing_search_tools.py`)

Herramientas para búsqueda web usando Bing:

- `create_bing_search_tool()`: Búsqueda web general
- `create_gov_sources_search_tool()`: Búsqueda en fuentes oficiales .gov
- `create_news_search_tool()`: Búsqueda de noticias

**Configuración requerida**: `BING_CONNECTION_ID` en `.env`

### 3. Azure AI Search RAG (`azure_search_rag.py`) ⭐ NUEVO

Herramientas para búsqueda en documentos oficiales indexados (PDFs, normativas, leyes):

- `search_official_documents()`: Búsqueda general en documentos oficiales
- `search_electoral_regulations()`: Búsqueda específica en normativas electorales
- `search_housing_regulations()`: Búsqueda en regulaciones de vivienda
- `get_document_citation()`: Obtiene citaciones formales de documentos

**Configuración requerida**:
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_INDEX_NAME`
- `AZURE_SEARCH_KEY` (opcional si usas Azure CLI auth)

**Ver**: `RAG_SETUP.md` para guía completa de configuración

## Indexación de Documentos

### Script de Indexación (`index_documents.py`)

Script para indexar PDFs desde Azure Storage en Azure AI Search:

```bash
# Instalar dependencias opcionales
pip install -e ".[indexing]"

# Ejecutar script
python agents/tools/index_documents.py
```

**Opciones**:
1. Crear/actualizar índice
2. Indexar documentos desde Storage
3. Verificar índice
4. Todo (crear + indexar + verificar)

## Cómo Agregar Nuevas Tools

1. Crea una nueva función con el decorador `@ai_function`
2. Usa `Annotated` y `Field` para describir los parámetros
3. Retorna un diccionario con los resultados
4. Agrega la tool al agente correspondiente en `civic_orchestration.py`

Ejemplo:

```python
from typing import Annotated
from pydantic import Field
from agent_framework import ai_function

@ai_function(
    name="my_tool",
    description="Descripción clara de qué hace la tool"
)
def my_tool(
    param: Annotated[str, Field(description="Descripción del parámetro")]
) -> dict:
    """Docstring explicando la función."""
    # Tu lógica aquí
    return {"result": "valor"}
```

## Mejores Prácticas

1. **Descripciones claras**: El LLM usa las descripciones para decidir cuándo usar la tool
2. **Manejo de errores**: Siempre retorna un diccionario, incluso en caso de error
3. **Validación**: Valida los parámetros de entrada
4. **Documentación**: Incluye docstrings y ejemplos
5. **Testing**: Prueba cada tool individualmente antes de integrarla

## Recursos

- [Agent Framework - Function Tools](https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/function-tools)
- [Pydantic Field](https://docs.pydantic.dev/latest/concepts/fields/)
- [Azure AI Search RAG Setup](./RAG_SETUP.md)
