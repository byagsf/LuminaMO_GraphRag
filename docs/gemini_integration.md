# Guía de Integración de Gemini con GraphRAG

## Descripción

Esta guía explica cómo usar Google Gemini como proveedor de modelos de lenguaje en GraphRAG. La integración permite usar tanto modelos de chat como de embeddings de Gemini.

## Características

- ✅ Soporte para chat con modelos Gemini (gemini-pro, gemini-1.5-pro)
- ✅ Soporte para embeddings con modelos de Gemini (text-embedding-004)
- ✅ Integración completa con el pipeline de GraphRAG
- ✅ Soporte para operaciones asíncronas y síncronas
- ✅ Manejo de historial de conversación
- ✅ Streaming de respuestas (chat)

## Prerequisitos

1. **API Key de Google Gemini**: Obtén tu clave desde [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Dependencias**: 
   ```bash
   pip install google-generativeai
   ```

## Configuración

### 1. Variables de Entorno

Configura tu API key en el archivo `.env`:

```bash
GRAPHRAG_API_KEY=tu_api_key_de_gemini_aqui
```

### 2. Configuración en settings.yaml

Ejemplo básico para usar solo Gemini:

```yaml
models:
  default_chat_model:
    type: gemini_chat
    api_key: ${GRAPHRAG_API_KEY}
    model: gemini-pro
    encoding_model: cl100k_base  # Importante: evita problemas con tiktoken
    temperature: 0.7
    max_tokens: 2048
    concurrent_requests: 10

  default_embedding_model:
    type: gemini_embedding
    api_key: ${GRAPHRAG_API_KEY}
    model: models/text-embedding-004
    encoding_model: cl100k_base  # Importante: evita problemas con tiktoken
    concurrent_requests: 10
```

### 3. Configuración Mixta (Gemini + OpenAI)

También puedes usar Gemini para chat y OpenAI para embeddings (o viceversa):

```yaml
models:
  default_chat_model:
    type: gemini_chat
    api_key: ${GEMINI_API_KEY}
    model: gemini-pro
    encoding_model: cl100k_base

  default_embedding_model:
    type: openai_embedding
    api_key: ${OPENAI_API_KEY}
    model: text-embedding-3-small
```

## Modelos Disponibles

### Modelos de Chat
- `gemini-pro`: Modelo base, buena relación costo-beneficio
- `gemini-1.5-pro`: Modelo avanzado con mejor rendimiento y contexto más largo
- `gemini-1.5-flash`: Modelo optimizado para velocidad

### Modelos de Embeddings
- `models/text-embedding-004`: Modelo principal de embeddings de Google
- `models/embedding-001`: Modelo anterior (no recomendado para nuevos proyectos)

## Uso Básico

### 1. Ejecutar el Indexado

```bash
graphrag index --root ./ragtest
```

### 2. Realizar Consultas

**Búsqueda Global:**
```bash
graphrag query \
--root ./ragtest \
--method global \
--query "¿Cuáles son los temas principales en este documento?"
```

**Búsqueda Local:**
```bash
graphrag query \
--root ./ragtest \
--method local \
--query "¿Quién es el personaje principal y cuáles son sus relaciones?"
```

## Uso Programático

### Ejemplo de Chat

```python
from graphrag.config.models.language_model_config import LanguageModelConfig
from graphrag.language_model.providers.gemini.models import GeminiChatProvider

# Configuración
config = LanguageModelConfig(
    type="gemini_chat",
    api_key="tu_api_key_aqui",
    model="gemini-pro",
    encoding_model="cl100k_base",
    temperature=0.7,
)

# Crear provider
chat_provider = GeminiChatProvider(name="mi_chat", config=config)

# Usar asíncronamente
response = await chat_provider.achat("Explica qué es GraphRAG")
print(response.output.content)

# Usar síncronamente
response = chat_provider.chat("Explica qué es GraphRAG")
print(response.output.content)
```

### Ejemplo de Embeddings

```python
from graphrag.language_model.providers.gemini.models import GeminiEmbeddingProvider

# Configuración
config = LanguageModelConfig(
    type="gemini_embedding",
    api_key="tu_api_key_aqui",
    model="models/text-embedding-004",
    encoding_model="cl100k_base",
)

# Crear provider
embedding_provider = GeminiEmbeddingProvider(name="mi_embedding", config=config)

# Generar embeddings
embedding = await embedding_provider.aembed("Texto de ejemplo")
print(f"Dimensiones: {len(embedding)}")
```

## Limitaciones y Consideraciones

### Límites de Rate
- Gemini tiene límites más conservadores que OpenAI
- Recomendación: `concurrent_requests: 10` o menos
- Monitorea tu uso en [Google AI Studio](https://makersuite.google.com/)

### Diferencias con OpenAI
- Formato de respuesta ligeramente diferente
- Nombres de modelos específicos de Google
- Límites de contexto pueden variar

### Manejo de Errores
- Errores de autenticación: Verifica tu API key
- Errores de quota: Revisa tus límites en Google Cloud
- Errores de modelo: Asegúrate de usar nombres de modelo válidos

## Troubleshooting

### Error: "Could not automatically map to tokeniser"
**Solución**: Asegúrate de incluir `encoding_model: cl100k_base` en tu configuración.

### Error: "API key missing"
**Solución**: Verifica que tu API key esté correctamente configurada en el archivo `.env`.

### Error: "Model not found"
**Solución**: Verifica que estés usando nombres de modelo válidos de Gemini.

### Performance lento
**Solución**: 
- Reduce `concurrent_requests` a 5-10
- Usa `gemini-1.5-flash` para respuestas más rápidas
- Considera usar modelos mixtos (Gemini chat + OpenAI embeddings)

## Pruebas

Para verificar que todo funciona correctamente:

```bash
python test_gemini_integration.py
```

Este script realizará pruebas de:
- ✅ Registro en factory
- ✅ Chat básico
- ✅ Generación de embeddings
- ✅ Integración completa

## Soporte

Si encuentras problemas:

1. Revisa los logs de GraphRAG para errores específicos
2. Verifica tu configuración contra los ejemplos
3. Asegúrate de tener la versión correcta de `google-generativeai`
4. Consulta la documentación oficial de Gemini

## Changelog

### v1.0.0
- ✅ Soporte inicial para Gemini chat y embeddings
- ✅ Integración con GraphRAG factory
- ✅ Documentación y ejemplos
- ✅ Scripts de prueba
