# Civic Chat - Chatbot Multi-Agente para Información Cívica

## Descripción

Civic Chat es un asistente cívico multi-agente desarrollado con Microsoft Agent Framework y servicios de Azure que proporciona información cívica neutral, accesible y multilingüe para todos los ciudadanos.

### Características Principales

- 🤖 **Arquitectura Multi-Agente**: Agentes especializados que colaboran mediante HandoffBuilder
- 🌍 **Soporte Multilingüe**: Traducción automática con Azure Translator
- 🧠 **Memoria Persistente**: Recuerda información del usuario entre sesiones
- ⚖️ **Neutralidad Política**: Validación automática para mantener imparcialidad
- 📚 **Información Oficial**: Respuestas basadas en fuentes gubernamentales verificadas

## Estado del Proyecto

✅ **Fase 1 Completada**: Refactorización de código y memoria persistente
🚧 **Fase 2 En Progreso**: Implementación de Router Agent

Ver [tasks.md](.kiro/specs/civic-chat-multi-agent/tasks.md) para el plan completo de implementación.

## Arquitectura

El proyecto sigue una arquitectura multi-agente con componentes especializados:

```
src/civic_chat/
├── agents/          # Agentes especializados (Router, Knowledge, Validator)
├── tools/           # Funciones AI (@ai_function)
├── models/          # Modelos de datos
├── workflows/       # Orquestación HandoffBuilder
└── agents/memory/   # Gestión de memoria persistente
```

Ver [ARCHITECTURE.md](ARCHITECTURE.md) para detalles completos de la arquitectura.

## Documentación

### Documentación Principal

- � [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura y estructura del proyecto
- 📋 [Requirements](.kiro/specs/civic-chat-multi-agent/requirements.md) - Requisitos del sistema
- 🎨 [Design](.kiro/specs/civic-chat-multi-agent/design.md) - Documento de diseño
- ✅ [Tasks](.kiro/specs/civic-chat-multi-agent/tasks.md) - Plan de implementación

### Documentación Fase 1

- 🚀 [RUNNING_THE_APP.md](docs/phase1/RUNNING_THE_APP.md) - Guía de ejecución
- 🔧 [REFACTORING_COMPLETE.md](docs/phase1/REFACTORING_COMPLETE.md) - Detalles de refactorización
- 💾 [MEMORY_FIX_COMPLETE.md](docs/phase1/MEMORY_FIX_COMPLETE.md) - Implementación de memoria
- 📝 [RESUMEN_TAREA_1.md](docs/phase1/RESUMEN_TAREA_1.md) - Resumen en español
- 🎉 [FINAL_SUMMARY.md](docs/phase1/FINAL_SUMMARY.md) - Resumen final

## Instalación

### Requisitos Previos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) - Gestor de paquetes Python
- Azure CLI (para autenticación)
- Cuenta de Azure con:
  - Azure OpenAI Service
  - Azure Translator

### Configuración

1. **Clonar el repositorio**:

```bash
git clone <repository-url>
cd chatbot-civic
```

2. **Instalar dependencias**:

```bash
uv sync
```

3. **Configurar variables de entorno**:

```bash
cp src/civic_chat/.env.example src/civic_chat/.env
# Editar .env con tus credenciales de Azure
```

4. **Autenticarse con Azure CLI**:

```bash
az login
```

## Uso

### Ejecutar la Aplicación

**Método 1: Como módulo Python (Recomendado)**

```bash
uv run python -m civic_chat.main
```

**Método 2: Ejecución directa**

```bash
uv run python src/civic_chat/main.py
```

**Método 3: Script wrapper**

```bash
./scripts/run_civic_chat.sh
```

### Ejemplos de Uso

```bash
# Preguntas en inglés
Tú: How do I register to vote?

# Preguntas en español
Tú: ¿Cuáles son los requisitos para votar?

# Salir
Tú: exit
```

## Estructura del Proyecto

```
chatbot-civic/
├── src/civic_chat/              # Código fuente principal
│   ├── agents/                  # Implementaciones de agentes
│   │   └── memory/             # Gestión de memoria
│   ├── tools/                   # Funciones AI
│   ├── models/                  # Modelos de datos
│   ├── workflows/               # Orquestación
│   └── main.py                  # Punto de entrada
├── .kiro/specs/                 # Especificaciones del proyecto
│   └── civic-chat-multi-agent/
│       ├── requirements.md      # Requisitos
│       ├── design.md           # Diseño
│       └── tasks.md            # Tareas
├── scripts/                     # Scripts de utilidad
│   ├── run_civic_chat.sh       # Ejecutar aplicación
│   ├── demo_memory.sh          # Demo de memoria
│   ├── setup-resource.sh       # Setup Azure
│   └── cleanup-resources.sh    # Cleanup Azure
├── docs/                        # Documentación
│   ├── phase1/                 # Documentación Fase 1
│   │   ├── REFACTORING_COMPLETE.md
│   │   ├── MEMORY_FIX_COMPLETE.md
│   │   ├── RESUMEN_TAREA_1.md
│   │   ├── RUNNING_THE_APP.md
│   │   └── FINAL_SUMMARY.md
│   └── img/                    # Imágenes y diagramas
├── user_data/                   # Datos de usuario persistentes
├── ARCHITECTURE.md              # Arquitectura del proyecto
└── README.md                    # Este archivo
```

## Tecnologías

- **Microsoft Agent Framework**: Framework para agentes AI
- **Azure OpenAI**: GPT-4o-mini para procesamiento de lenguaje
- **Azure Translator**: Traducción multilingüe
- **Python 3.12**: Lenguaje de programación
- **uv**: Gestor de paquetes y entornos virtuales

## Contribuir

Este proyecto sigue un proceso de desarrollo basado en especificaciones:

1. Revisar [requirements.md](.kiro/specs/civic-chat-multi-agent/requirements.md)
2. Consultar [design.md](.kiro/specs/civic-chat-multi-agent/design.md)
3. Seguir [tasks.md](.kiro/specs/civic-chat-multi-agent/tasks.md)
4. Leer [ARCHITECTURE.md](ARCHITECTURE.md) para entender la estructura

## Licencia

[Especificar licencia]

## Contacto

[Información de contacto]

---

**Estado**: ✅ Fase 1 Completada - Refactorización y Memoria Persistente  
**Próximo**: 🚧 Fase 2 - Implementación de Router Agent
