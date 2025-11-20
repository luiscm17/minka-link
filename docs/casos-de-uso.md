# Casos de Uso - Civic Chat

## Documento de Casos de Uso Detallados

**Proyecto**: Civic Chat - Chatbot Multi-Agente para Información Política Inclusiva  
**Tecnología**: Semantic Kernel Python + Azure Services

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Actores del Sistema](#actores-del-sistema)
3. [Casos de Uso Principales](#casos-de-uso-principales)
4. [Casos de Uso Técnicos](#casos-de-uso-técnicos)
5. [Restricciones Éticas](#restricciones-éticas)
6. [Matriz de Trazabilidad](#matriz-de-trazabilidad)

---

## Introducción

Este documento describe los casos de uso del sistema Civic Chat, una herramienta de información política inclusiva diseñada para proporcionar acceso equitativo a información electoral para ciudadanos de diversos orígenes lingüísticos y socioeconómicos.

### Objetivos del Sistema

- Democratizar el acceso a información política
- Eliminar barreras lingüísticas (16+ idiomas)
- Mantener neutralidad política absoluta
- Empoderar a comunidades subrepresentadas
- Proporcionar información basada en fuentes oficiales

---

## Actores del Sistema

### Actores Primarios

| Actor | Descripción | Características |
|-------|-------------|-----------------|
| **Ciudadano Votante** | Usuario general que busca información electoral | Puede tener diferentes niveles de conocimiento político |
| **Ciudadano No Angloparlante** | Usuario que habla uno de los 16+ idiomas soportados | Requiere traducción automática |
| **Ciudadano con Limitaciones de Lectura** | Usuario que prefiere o necesita interacción por voz | Usa Speech-to-Text y Text-to-Speech |
| **Ciudadano de Comunidad Subrepresentada** | Usuario de grupos socioeconómicos vulnerables | Necesita análisis de impacto específico |

### Actores Secundarios

| Actor | Descripción |
|-------|-------------|
| **Sistema de Caché** | Componente que gestiona contenido pre-generado |
| **Administrador del Sistema** | Persona que configura y mantiene el sistema |

---

## Casos de Uso Principales

### CU-01: Consulta de Información sobre Candidatos

**Actor Principal**: Ciudadano Votante  
**Objetivo**: Obtener información objetiva sobre las posiciones de un candidato en temas específicos  
**Precondiciones**:

- El sistema tiene acceso a fuentes oficiales del candidato
- El candidato está registrado en la base de datos electoral

**Flujo Principal**:

1. Usuario inicia conversación con el sistema
2. Usuario pregunta sobre posición de candidato en tema específico (ej: "¿Cuál es la posición del candidato María López sobre educación pública?")
3. Sistema identifica el idioma del usuario
4. Sistema traduce la consulta al idioma de procesamiento (inglés) si es necesario
5. Agente de Búsqueda localiza información en fuentes oficiales (sitio web, redes sociales del candidato)
6. Agente de Síntesis genera respuesta neutral y objetiva
7. Sistema traduce respuesta al idioma del usuario
8. Sistema presenta información con citas de fuentes
9. Usuario puede hacer preguntas de seguimiento

**Flujos Alternativos**:

- **FA-01a**: Si no hay información disponible, el sistema informa que no encontró datos en fuentes oficiales
- **FA-01b**: Si la pregunta es ambigua, el sistema solicita clarificación
- **FA-01c**: Si el candidato no existe, el sistema sugiere candidatos similares

**Postcondiciones**:

- Usuario recibe información objetiva basada en fuentes oficiales
- Conversación queda registrada para contexto futuro

**Requisitos No Funcionales**:

- Tiempo de respuesta: < 5 segundos
- Neutralidad: 100% (sin sesgos detectables)
- Precisión de traducción: > 95%

---

### CU-02: Explicación de Propuestas en Papeletas

**Actor Principal**: Ciudadano Votante Confundido  
**Objetivo**: Comprender el significado y las implicaciones de preguntas confusas o retóricas en la papeleta electoral  
**Precondiciones**:

- La propuesta está registrada en el sistema
- Existe información oficial sobre la propuesta

**Flujo Principal**:

1. Usuario presenta pregunta de papeleta que no entiende (ej: "¿Qué significa la Propuesta 3 sobre bonos municipales?")
2. Sistema identifica la propuesta específica
3. Agente de Síntesis desglosa la propuesta en lenguaje claro y simple
4. Sistema explica:
   - Qué se está proponiendo
   - Qué significa votar "Sí"
   - Qué significa votar "No"
   - Implicaciones prácticas
5. Sistema presenta información sin recomendar voto
6. Usuario puede solicitar más detalles o ejemplos

**Flujos Alternativos**:

- **FA-02a**: Si la propuesta tiene lenguaje técnico legal, el sistema proporciona definiciones
- **FA-02b**: Si hay múltiples interpretaciones, el sistema presenta todas objetivamente

**Postcondiciones**:

- Usuario comprende la propuesta
- Usuario puede tomar decisión informada

**Requisitos No Funcionales**:

- Claridad: Lenguaje de nivel 8vo grado
- Neutralidad: Sin indicar preferencia de voto

---

### CU-03: Análisis Multi-Perspectiva de Impacto Socioeconómico

**Actor Principal**: Ciudadano de Comunidad Subrepresentada  
**Objetivo**: Entender cómo una política o propuesta afectará a diferentes grupos socioeconómicos  
**Precondiciones**:

- Existe información sobre la política/propuesta
- Sistema tiene capacidad de análisis multi-perspectiva

**Flujo Principal**:

1. Usuario pregunta sobre impacto de una propuesta (ej: "¿Cómo afectará esta propuesta de vivienda a personas que trabajan dos empleos?")
2. Sistema identifica la propuesta y el grupo socioeconómico de interés
3. Agente de Síntesis analiza impacto desde múltiples perspectivas:
   - Trabajadores de bajos ingresos
   - Familias con múltiples empleos
   - Propietarios de vivienda
   - Inquilinos
   - Pequeños negocios
   - Otros grupos relevantes
4. Sistema presenta análisis equilibrado de cada perspectiva
5. Sistema cita fuentes y datos oficiales
6. Usuario puede profundizar en perspectivas específicas

**Flujos Alternativos**:

- **FA-03a**: Si no hay datos específicos para un grupo, el sistema lo indica claramente
- **FA-03b**: Usuario puede solicitar comparación entre dos grupos específicos

**Postcondiciones**:

- Usuario comprende impacto diferenciado
- Usuario puede tomar decisión considerando su contexto

**Requisitos No Funcionales**:

- Equidad: Todas las perspectivas presentadas con igual peso
- Precisión: Basado en datos oficiales verificables

---

### CU-04: Acceso Multilingüe a Guía Electoral

**Actor Principal**: Ciudadano No Angloparlante  
**Objetivo**: Acceder a información electoral en su idioma nativo  
**Precondiciones**:

- Sistema soporta el idioma del usuario (16+ idiomas)
- Azure Translator está disponible

**Flujo Principal**:

1. Usuario inicia conversación en su idioma nativo (ej: bengalí, árabe, coreano)
2. Sistema detecta automáticamente el idioma
3. Sistema traduce consulta al idioma de procesamiento
4. Sistema procesa la consulta
5. Sistema traduce respuesta al idioma del usuario
6. Sistema presenta respuesta en idioma nativo del usuario
7. Conversación continúa en el idioma del usuario

**Flujos Alternativos**:

- **FA-04a**: Si detección automática falla, sistema solicita confirmación de idioma
- **FA-04b**: Usuario puede cambiar de idioma durante la conversación
- **FA-04c**: Si traducción es ambigua, sistema solicita clarificación

**Postcondiciones**:

- Usuario accede a información que normalmente solo está en inglés/español
- Barrera lingüística eliminada

**Requisitos No Funcionales**:

- Idiomas soportados: 16+ (inglés, español, ruso, bengalí, criollo haitiano, coreano, árabe, polaco, urdu, francés, yiddish, griego, italiano, tagalo, punjabi, vietnamita)
- Precisión de traducción: > 95%
- Independencia del dispositivo: 100%

---

### CU-05: Consulta por Voz para Accesibilidad

**Actor Principal**: Ciudadano con Limitaciones de Lectura  
**Objetivo**: Interactuar con el sistema mediante voz en lugar de texto  
**Precondiciones**:

- Azure Speech Services está disponible
- Usuario tiene micrófono y altavoces/audífonos

**Flujo Principal**:

1. Usuario activa modo de voz
2. Usuario hace pregunta hablada (ej: "¿Qué hace un Comptroller?")
3. Sistema transcribe audio a texto (Speech-to-Text)
4. Sistema procesa la consulta
5. Sistema genera respuesta
6. Sistema convierte respuesta a audio (Text-to-Speech) con voz neural
7. Sistema reproduce audio al usuario
8. Usuario puede continuar conversación por voz

**Flujos Alternativos**:

- **FA-05a**: Si audio no es claro, sistema solicita repetición
- **FA-05b**: Usuario puede alternar entre voz y texto
- **FA-05c**: Para contenido estático (descripciones de cargos), sistema usa audio pre-generado

**Postcondiciones**:

- Usuario accede a información sin necesidad de leer
- Accesibilidad mejorada

**Requisitos No Funcionales**:

- Calidad de voz: Voces neurales (no robóticas)
- Latencia: < 3 segundos para respuesta de audio
- Precisión de transcripción: > 90%

---

### CU-06: Exploración Abierta de Temas Políticos

**Actor Principal**: Ciudadano Investigando  
**Objetivo**: Explorar temas políticos sin dirección específica, sin encontrar callejones sin salida  
**Precondiciones**:

- Sistema tiene capacidad de conversación abierta
- Base de conocimiento electoral está disponible

**Flujo Principal**:

1. Usuario hace pregunta general (ej: "Cuéntame sobre las elecciones locales")
2. Sistema proporciona información general
3. Sistema sugiere áreas relacionadas que el usuario podría explorar
4. Usuario elige dirección de exploración
5. Sistema proporciona información sin limitar opciones
6. Conversación evoluciona naturalmente según interés del usuario
7. Sistema mantiene contexto de conversación

**Flujos Alternativos**:

- **FA-06a**: Usuario puede cambiar de tema en cualquier momento
- **FA-06b**: Sistema puede sugerir temas relacionados sin forzar dirección

**Postcondiciones**:

- Usuario explora libremente sin restricciones
- Usuario no encuentra "callejones sin salida"

**Requisitos No Funcionales**:

- Fluidez conversacional: Natural y sin restricciones
- Memoria de contexto: Últimas 10 interacciones

---

### CU-07: Comparación Neutral de Candidatos

**Actor Principal**: Ciudadano Indeciso  
**Objetivo**: Comparar candidatos sin recibir recomendaciones  
**Precondiciones**:

- Información de ambos candidatos está disponible
- Fuentes oficiales son accesibles

**Flujo Principal**:

1. Usuario solicita comparación (ej: "¿En qué se diferencian el candidato A y B sobre salud?")
2. Sistema identifica candidatos y tema
3. Agente de Búsqueda recopila posiciones de ambos candidatos
4. Agente de Síntesis presenta posiciones lado a lado
5. Sistema presenta información objetiva sin "mantener puntuación"
6. Sistema NO recomienda ni sugiere preferencia
7. Usuario puede profundizar en aspectos específicos

**Flujos Alternativos**:

- **FA-07a**: Si un candidato no tiene posición clara, sistema lo indica
- **FA-07b**: Usuario puede agregar más candidatos a la comparación
- **FA-07c**: Usuario puede cambiar el tema de comparación

**Postcondiciones**:

- Usuario tiene información comparativa objetiva
- Usuario decide por sí mismo sin influencia del sistema

**Requisitos No Funcionales**:

- Neutralidad: 100% (sin favorecer ningún candidato)
- Balance: Igual espacio/peso para cada candidato
- Objetividad: Solo hechos de fuentes oficiales

---

### CU-08: Consulta de Información sobre Cargos Electorales

**Actor Principal**: Ciudadano Desinformado sobre Estructura Gubernamental  
**Objetivo**: Entender qué hace cada cargo electoral y su importancia  
**Precondiciones**:

- Información sobre cargos está en la base de datos
- Audio pre-generado disponible (para optimización)

**Flujo Principal**:

1. Usuario pregunta sobre cargo específico (ej: "¿Qué hace un Comptroller?")
2. Sistema identifica el cargo
3. Sistema verifica si existe audio pre-generado en caché (Blob Storage)
4. Si existe caché:
   - Sistema reproduce audio pre-generado
5. Si no existe caché:
   - Sistema genera respuesta
   - Sistema convierte a audio (si modo voz está activo)
   - Sistema almacena en caché para futuras consultas
6. Sistema explica:
   - Responsabilidades del cargo
   - Alcance de autoridad
   - Importancia del voto para ese cargo
7. Usuario comprende el cargo

**Flujos Alternativos**:

- **FA-08a**: Usuario puede solicitar ejemplos de decisiones del cargo
- **FA-08b**: Usuario puede preguntar sobre múltiples cargos

**Postcondiciones**:

- Usuario comprende estructura gubernamental
- Usuario valora importancia de cada voto

**Requisitos No Funcionales**:

- Optimización de costos: Usar caché para contenido estático
- Claridad: Lenguaje accesible para todos los niveles educativos

---

## Casos de Uso Técnicos

### CU-09: Gestión de Caché de Contenido Estático

**Actor Principal**: Sistema de Caché  
**Objetivo**: Pre-generar y almacenar audio para contenido que no cambia  
**Precondiciones**:

- Azure Blob Storage está configurado
- Contenido estático está identificado

**Flujo Principal**:

1. Sistema identifica contenido estático (descripciones de cargos, definiciones)
2. Sistema genera audio en todos los idiomas soportados
3. Sistema almacena archivos MP3 en Azure Blob Storage
4. Sistema indexa archivos para recuperación rápida
5. En consultas futuras, sistema sirve desde caché

**Postcondiciones**:

- Costos de generación de audio reducidos
- Tiempo de respuesta mejorado

**Requisitos No Funcionales**:

- Reducción de costos: 80% para contenido estático
- Tiempo de recuperación: < 500ms

---

### CU-10: Detección Automática de Idioma

**Actor Principal**: Sistema  
**Objetivo**: Identificar idioma del usuario sin que lo especifique  
**Precondiciones**:

- Azure Translator está disponible
- Usuario inicia conversación

**Flujo Principal**:

1. Usuario envía primer mensaje
2. Sistema analiza texto/audio
3. Azure Translator detecta idioma
4. Sistema configura idioma de conversación
5. Sistema continúa en idioma detectado

**Flujos Alternativos**:

- **FA-10a**: Si confianza de detección < 80%, sistema solicita confirmación

**Postcondiciones**:

- Experiencia fluida sin fricción
- Usuario no necesita configurar idioma manualmente

**Requisitos No Funcionales**:

- Precisión de detección: > 95%
- Tiempo de detección: < 1 segundo

---

## Restricciones Éticas

### Restricciones Aplicables a TODOS los Casos de Uso

#### ❌ Prohibiciones Absolutas

1. **NO Recomendar Voto**
   - El sistema NUNCA debe decir por quién votar
   - El sistema NUNCA debe sugerir preferencias
   - El sistema NUNCA debe indicar "mejor" opción

2. **NO Expresar Opiniones Políticas**
   - El sistema NUNCA debe tomar posición política
   - El sistema NUNCA debe favorecer ideología
   - El sistema NUNCA debe "mantener puntuación"

3. **NO Usar Fuentes No Oficiales**
   - El sistema NUNCA debe citar medios de comunicación
   - El sistema NUNCA debe usar opiniones de "talking heads"
   - El sistema NUNCA debe basarse en rumores o especulación

4. **NO Crear Callejones Sin Salida**
   - El sistema NUNCA debe limitar exploración del usuario
   - El sistema NUNCA debe forzar dirección de conversación
   - El sistema NUNCA debe restringir preguntas

#### ✅ Obligaciones Absolutas

1. **SÍ Presentar Información Objetiva**
   - Basada en hechos verificables
   - De fuentes oficiales únicamente
   - Con contexto completo

2. **SÍ Citar Fuentes Oficiales**
   - Sitios web de candidatos
   - Redes sociales oficiales
   - Documentos gubernamentales
   - Declaraciones públicas registradas

3. **SÍ Mantener Neutralidad Absoluta**
   - Igual tratamiento para todos los candidatos
   - Sin sesgos detectables
   - Balance en presentación

4. **SÍ Empoderar al Usuario**
   - Proporcionar información para decisión informada
   - Respetar autonomía del usuario
   - Facilitar exploración libre

---

## Matriz de Trazabilidad

### Casos de Uso vs Desafíos del Documento Original

| Caso de Uso | Desafío Técnico | Desafío Ético | Servicios Azure |
|-------------|-----------------|---------------|-----------------|
| CU-01 | Independencia del dispositivo | Neutralidad | OpenAI, Translator |
| CU-02 | Arquitectura escalable | Evitar recomendaciones | OpenAI, Cognitive Search |
| CU-03 | - | Inclusividad y equidad | OpenAI |
| CU-04 | Soporte lingüístico | Acceso equitativo | Translator |
| CU-05 | Voces neurales, gestión de costos | Accesibilidad | Speech Services, Blob Storage |
| CU-06 | - | Evitar callejones sin salida | OpenAI |
| CU-07 | - | No mantener puntuación | OpenAI, Cognitive Search |
| CU-08 | Gestión de costos | - | Speech Services, Blob Storage |
| CU-09 | Gestión de costos | - | Blob Storage |
| CU-10 | Independencia del dispositivo | - | Translator |

### Casos de Uso vs Agentes del Sistema Multi-Agente

| Caso de Uso | Agente Orquestador | Agente Traducción | Agente Búsqueda | Agente Síntesis | Agente Conversación |
|-------------|-------------------|-------------------|-----------------|-----------------|---------------------|
| CU-01 | ✓ | ✓ | ✓ | ✓ | ✓ |
| CU-02 | ✓ | ✓ | ✓ | ✓ | ✓ |
| CU-03 | ✓ | ✓ | ✓ | ✓ | ✓ |
| CU-04 | ✓ | ✓ | - | - | ✓ |
| CU-05 | ✓ | ✓ | - | - | ✓ |
| CU-06 | ✓ | ✓ | ✓ | ✓ | ✓ |
| CU-07 | ✓ | ✓ | ✓ | ✓ | ✓ |
| CU-08 | ✓ | ✓ | ✓ | ✓ | ✓ |
| CU-09 | - | - | - | - | - |
| CU-10 | ✓ | ✓ | - | - | - |

---

## Notas de Implementación

### Priorización para MVP

**Fase 1 - Funcionalidad Core** (CU-01, CU-02, CU-04):

- Consulta básica de candidatos
- Explicación de propuestas
- Soporte multilingüe básico (inglés, español)

**Fase 2 - Accesibilidad** (CU-05, CU-08, CU-09):

- Interacción por voz
- Información sobre cargos
- Optimización de caché

**Fase 3 - Análisis Avanzado** (CU-03, CU-06, CU-07):

- Análisis multi-perspectiva
- Exploración abierta
- Comparación de candidatos

**Fase 4 - Optimización** (CU-10):

- Detección automática de idioma
- Expansión a 16+ idiomas

### Métricas de Éxito

- **Neutralidad**: 0 quejas de sesgo político
- **Accesibilidad**: 16+ idiomas soportados
- **Satisfacción**: > 80% de usuarios satisfechos
- **Precisión**: > 95% de información verificable
- **Rendimiento**: < 5 segundos tiempo de respuesta

---

**Fin del Documento**
