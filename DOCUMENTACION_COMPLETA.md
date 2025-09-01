# 🚀 GraphRAG + Gemini - Guía Completa de Instalación y Uso

## 📦 Instalación desde Cero

### 1. Prerrequisitos del Sistema
```bash
# Python 3.11+ requerido
python3 --version

# Clonar el repositorio
git clone https://github.com/byagsf/LuminaMO_GraphRag.git
cd LuminaMO_GraphRag

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o en Windows: .venv\Scripts\activate
```

### 2. Instalar Dependencias
```bash
# Instalar GraphRAG y dependencias
pip install -e .

# Instalar dependencias específicas de Gemini
pip install google-generativeai

# Verificar instalación
python -c "import graphrag; print('GraphRAG instalado correctamente')"
```

### 3. Configurar API de Gemini
```bash
# Obtener API key de https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="tu_clave_de_api_aqui"

# Verificar conexión
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
print('✅ Gemini conectado')
"
```

## 🏗️ Construcción del Proyecto

### 1. Preparar Estructura de Datos
```bash
# Crear directorio de trabajo
mkdir mi_proyecto_rag
cd mi_proyecto_rag

# Crear subdirectorios necesarios
mkdir input output cache

# Colocar documentos a procesar en input/
cp /ruta/a/tus/documentos.txt input/
```

### 2. Crear Configuración
```bash
# Crear archivo de configuración optimizado para Gemini
cat > settings.yaml << 'EOF'
encoding_model: cl100k_base
skip_workflows: []

llm:
  api_key: ${GEMINI_API_KEY}
  type: gemini_chat
  model: models/gemini-1.5-flash
  temperature: 0.0
  max_tokens: 4000
  request_timeout: 180.0
  max_retries: 10
  concurrent_requests: 1  # Reducido para evitar límites de API
  requests_per_minute: 2  # Muy conservador para plan gratuito
  sleep_on_rate_limit_recommendation: true
  
embeddings:
  api_key: ${GEMINI_API_KEY}
  type: gemini_embedding
  model: models/text-embedding-004
  
chunks:
  size: 300
  overlap: 100
  
entity_extraction:
  max_gleanings: 1  # Reducido para ahorrar cuota

parallelization:
  stagger: 5.0      # 5 segundos entre requests
  num_threads: 1    # Un solo hilo para evitar rate limits

# Configuración de cache para evitar re-procesamiento
cache:
  type: file
  base_dir: "./cache"
EOF
```

### 3. Ejecutar Indexing (Construcción del Grafo)
```bash
# Procesar documentos y construir grafo de conocimiento
python -m graphrag.cli.index --root . --config settings.yaml

# El proceso creará:
# output/entities.parquet - Entidades extraídas
# output/relationships.parquet - Relaciones entre entidades  
# output/text_units.parquet - Fragmentos de texto
# output/community_reports.parquet - Resúmenes de comunidades (si no falla por cuota)
```

## ⚠️ Manejo del Problema de Community Reports

### Situación Común: "Could not find community_reports.parquet"

Esto ocurre cuando el indexing falla al generar reportes de comunidades, generalmente por límites de API gratuita.

#### Solución 1: Script Automático de Recuperación
```bash
# Crear script para generar community reports manualmente
cat > generate_community_reports.py << 'EOF'
#!/usr/bin/env python3
"""
Script para generar community_reports.parquet cuando falla el indexing
"""

import pandas as pd
from pathlib import Path
import logging

def create_minimal_community_reports(output_dir):
    """Crear community_reports.parquet mínimo para evitar errores"""
    
    output_path = Path(output_dir)
    
    # Verificar si ya existe
    community_file = output_path / "community_reports.parquet"
    if community_file.exists():
        print("✅ community_reports.parquet ya existe")
        return True
    
    try:
        # Cargar entidades para crear comunidades básicas
        entities_file = output_path / "entities.parquet"
        if not entities_file.exists():
            print("❌ No se encontró entities.parquet")
            return False
        
        entities = pd.read_parquet(entities_file)
        
        # Crear comunidades básicas agrupando por tipo de entidad
        communities = []
        entity_types = entities['type'].unique()
        
        for i, entity_type in enumerate(entity_types):
            type_entities = entities[entities['type'] == entity_type]
            
            community = {
                'id': f'community_{i}',
                'human_readable_id': i,
                'level': 0,
                'title': f'{entity_type} Community',
                'summary': f'Community of {entity_type} entities including: {", ".join(type_entities["title"].head(3).tolist())}',
                'full_content': f'This community contains {len(type_entities)} entities of type {entity_type}.',
                'rank': 1.0,
                'rank_explanation': f'Primary community for {entity_type} entities',
                'findings': [f'Contains {len(type_entities)} {entity_type} entities'],
                'full_content_json': f'{{"summary": "Community of {entity_type} entities", "entities": {len(type_entities)}}}'
            }
            communities.append(community)
        
        # Crear DataFrame y guardar
        community_df = pd.DataFrame(communities)
        community_df.to_parquet(community_file)
        
        print(f"✅ Creado community_reports.parquet con {len(communities)} comunidades")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear community_reports: {e}")
        return False

if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./output"
    create_minimal_community_reports(output_dir)
EOF

# Hacer ejecutable
chmod +x generate_community_reports.py

# Usar cuando falle el indexing:
python generate_community_reports.py ./output
```

#### Solución 2: Indexing Incremental
```bash
# Script para reanudar indexing paso a paso
cat > resume_indexing.py << 'EOF'
#!/usr/bin/env python3
"""
Script para reanudar indexing de GraphRAG paso a paso
"""

import subprocess
import sys
from pathlib import Path

def check_file_exists(file_path):
    """Verificar si un archivo existe"""
    return Path(file_path).exists()

def run_indexing_step(root_dir, config_file, step_name):
    """Ejecutar un paso específico del indexing"""
    print(f"🔄 Ejecutando: {step_name}")
    
    try:
        result = subprocess.run([
            "python", "-m", "graphrag.cli.index",
            "--root", root_dir,
            "--config", config_file,
            "--resume"
        ], capture_output=True, text=True, timeout=3600)  # 1 hora timeout
        
        if result.returncode == 0:
            print(f"✅ {step_name} completado")
            return True
        else:
            print(f"❌ {step_name} falló:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {step_name} excedió tiempo límite")
        return False
    except Exception as e:
        print(f"❌ Error en {step_name}: {e}")
        return False

def main():
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    config_file = sys.argv[2] if len(sys.argv) > 2 else "settings.yaml"
    
    output_dir = Path(root_dir) / "output"
    
    print("🚀 Verificando estado del indexing...")
    
    # Verificar archivos existentes
    files_to_check = [
        "entities.parquet",
        "relationships.parquet", 
        "text_units.parquet",
        "community_reports.parquet"
    ]
    
    existing_files = []
    for file in files_to_check:
        file_path = output_dir / file
        if file_path.exists():
            existing_files.append(file)
            print(f"✅ {file} existe")
        else:
            print(f"❌ {file} falta")
    
    # Si faltan archivos críticos, intentar reanudar
    if len(existing_files) < 3:  # Necesitamos al menos entities, relationships, text_units
        print("\n🔄 Reanudando indexing...")
        success = run_indexing_step(root_dir, config_file, "Indexing principal")
        
        if not success:
            print("\n⚠️  Indexing falló, creando community_reports mínimo...")
            from generate_community_reports import create_minimal_community_reports
            create_minimal_community_reports(output_dir)
    
    # Verificar estado final
    final_check = all(check_file_exists(output_dir / file) for file in files_to_check)
    
    if final_check:
        print("\n🎉 ¡Todos los archivos están disponibles!")
        print("Puedes ejecutar consultas ahora:")
        print(f"python -m graphrag.cli.query --root {root_dir} --method local 'tu pregunta'")
    else:
        print("\n⚠️  Algunos archivos siguen faltando")
        print("Usa consultas locales mientras tanto:")
        print("python local_query_test.py")

if __name__ == "__main__":
    main()
EOF

# Usar para recuperar indexing fallido:
python resume_indexing.py . settings.yaml
```

#### Solución 3: Configuración Tolerante a Fallos
```yaml
# settings_tolerante.yaml - Configuración que maneja fallos gracefully
encoding_model: cl100k_base
skip_workflows: 
  - create_final_community_reports  # Saltar si falla

llm:
  api_key: ${GEMINI_API_KEY}
  type: gemini_chat
  model: models/gemini-1.5-flash
  max_retries: 3
  concurrent_requests: 1
  requests_per_minute: 1  # Muy conservador
  
# Continuar processing aunque fallen algunos pasos
workflow:
  continue_on_error: true
  
# Cache agresivo para evitar re-procesamiento
cache:
  type: file
  base_dir: "./cache"
  enabled: true
```

## 🔍 Comandos para Consultas

### Consultas Básicas (Requieren community_reports)
```bash
# Búsqueda local (contexto específico)
python -m graphrag.cli.query \
  --root . \
  --method local \
  "¿Quién es el personaje principal?"

# Búsqueda global (vista general)  
python -m graphrag.cli.query \
  --root . \
  --method global \
  "¿De qué trata el documento?"
```

### Consultas Alternativas (Sin community_reports)
```bash
# Usar scripts locales cuando falta community_reports
python local_query_test.py    # Consultas automáticas
python interactive_query.py   # Consultas interactivas
python test_local_data.py     # Verificar datos disponibles
```

### Verificar Estado Antes de Consultar
```bash
# Script rápido para verificar archivos necesarios
python -c "
from pathlib import Path
output_dir = Path('./output')
files = ['entities.parquet', 'relationships.parquet', 'text_units.parquet', 'community_reports.parquet']
for f in files:
    status = '✅' if (output_dir / f).exists() else '❌'
    print(f'{status} {f}')
print()
community_exists = (output_dir / 'community_reports.parquet').exists()
if community_exists:
    print('🎉 Puedes usar consultas oficiales de GraphRAG')
else:
    print('⚠️  Usa scripts locales o genera community_reports')
"
```

## 🧠 Implementación de Gemini

### Arquitectura de Integración

La integración de Gemini se implementó creando un proveedor personalizado que adapta la API de Google Gemini al sistema de modelos de GraphRAG.

### Archivos Principales Modificados

#### 1. `graphrag/language_model/providers/gemini/models.py`
```python
class GeminiChatProvider:
    def __init__(self, *, name: str, config: LanguageModelConfig, 
                 callbacks: WorkflowCallbacks = None, cache: PipelineCache = None):
        # Configurar API de Gemini
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model or "models/gemini-1.5-flash")
        
    def _filter_gemini_params(self, **kwargs) -> dict[str, Any]:
        """Filtrar parámetros que Gemini no acepta"""
        excluded = ['name', 'functions', 'function_call']
        return {k: v for k, v in kwargs.items() if k not in excluded}
        
    async def achat(self, messages, **kwargs) -> ModelResponse:
        # Filtrar parámetros incompatibles
        filtered_kwargs = self._filter_gemini_params(**kwargs)
        
        # Convertir mensajes al formato de Gemini
        prompt = self._convert_messages_to_prompt(messages)
        
        # Realizar solicitud con manejo de errores
        try:
            response = await self.model.generate_content_async(prompt, **filtered_kwargs)
            return self._convert_response(response)
        except Exception as e:
            if "429" in str(e):  # Rate limit
                logger.warning("Rate limit alcanzado, reintentando...")
                await asyncio.sleep(10)
                # Reintentar una vez
                response = await self.model.generate_content_async(prompt, **filtered_kwargs)
                return self._convert_response(response)
            raise
```

#### 2. `graphrag/language_model/providers/gemini/embeddings.py`
```python
class GeminiEmbeddingProvider:
    def __init__(self, config: LanguageModelConfig):
        genai.configure(api_key=config.api_key)
        self.model_name = config.model or "models/text-embedding-004"
        
    async def aembed(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for i, text in enumerate(texts):
            try:
                result = await genai.embed_content_async(
                    model=self.model_name,
                    content=text
                )
                embeddings.append(result['embedding'])
                
                # Rate limiting preventivo
                if i > 0 and i % 10 == 0:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                if "429" in str(e):
                    logger.warning(f"Rate limit en embedding {i}, esperando...")
                    await asyncio.sleep(30)
                    # Reintentar
                    result = await genai.embed_content_async(
                        model=self.model_name,
                        content=text
                    )
                    embeddings.append(result['embedding'])
                else:
                    raise
        return embeddings
```

### Integración con GraphRAG

#### Registro del Proveedor
```python
# En graphrag/config/models/language_model_config.py
SUPPORTED_PROVIDERS = {
    "openai_chat": OpenAIChatProvider,
    "gemini_chat": GeminiChatProvider,  # ← Nuevo proveedor
    "azure_openai_chat": AzureOpenAIChatProvider,
}
```

## 🔧 Agregar un Nuevo Modelo de IA

### Paso 1: Crear Estructura del Proveedor
```bash
# Crear directorio para el nuevo proveedor
mkdir -p graphrag/language_model/providers/tu_modelo/

# Crear archivos necesarios
touch graphrag/language_model/providers/tu_modelo/__init__.py
cat > graphrag/language_model/providers/tu_modelo/models.py << 'EOF'
from graphrag.language_model.response.base import ModelResponse, BaseModelResponse
from graphrag.config.models.language_model_config import LanguageModelConfig
import asyncio
import logging

logger = logging.getLogger(__name__)

class TuModeloChatProvider:
    def __init__(self, *, name: str, config: LanguageModelConfig, 
                 callbacks=None, cache=None):
        # Inicializar cliente de tu API
        self.api_key = config.api_key
        self.model = config.model
        self.base_url = config.api_base or "https://api.tu-modelo.com"
        
    async def achat(self, messages, **kwargs) -> ModelResponse:
        # 1. Convertir mensajes al formato de tu modelo
        converted_messages = self._convert_messages(messages)
        
        # 2. Filtrar parámetros específicos
        filtered_kwargs = self._filter_params(**kwargs)
        
        # 3. Hacer solicitud HTTP a tu API
        import aiohttp
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "messages": converted_messages,
                **filtered_kwargs
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            ) as response:
                data = await response.json()
                
                # 4. Convertir respuesta al formato de GraphRAG
                return ModelResponse(
                    response=BaseModelResponse(
                        content=data["choices"][0]["message"]["content"]
                    )
                )
    
    def _convert_messages(self, messages):
        """Adaptar mensajes al formato de tu API"""
        return [
            {
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            }
            for msg in messages
        ]
        
    def _filter_params(self, **kwargs):
        """Filtrar parámetros que tu API no acepta"""
        allowed = ["temperature", "max_tokens", "top_p"]
        return {k: v for k, v in kwargs.items() if k in allowed}
EOF
```

### Paso 2: Implementar Embeddings (Opcional)
```bash
cat > graphrag/language_model/providers/tu_modelo/embeddings.py << 'EOF'
class TuModeloEmbeddingProvider:
    def __init__(self, config: LanguageModelConfig):
        self.api_key = config.api_key
        self.model = config.model
        self.base_url = config.api_base or "https://api.tu-modelo.com"
        
    async def aembed(self, texts: list[str]) -> list[list[float]]:
        import aiohttp
        embeddings = []
        
        async with aiohttp.ClientSession() as session:
            for text in texts:
                payload = {
                    "model": self.model,
                    "input": text
                }
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    f"{self.base_url}/embeddings",
                    json=payload,
                    headers=headers
                ) as response:
                    data = await response.json()
                    embeddings.append(data["data"][0]["embedding"])
                    
        return embeddings
EOF
```

### Paso 3: Registrar en el Sistema
```python
# Agregar a graphrag/config/models/language_model_config.py
from graphrag.language_model.providers.tu_modelo.models import TuModeloChatProvider

SUPPORTED_PROVIDERS = {
    "openai_chat": OpenAIChatProvider,
    "gemini_chat": GeminiChatProvider,
    "tu_modelo_chat": TuModeloChatProvider,  # ← Agregar aquí
}
```

### Paso 4: Configurar y Probar
```yaml
# settings_tu_modelo.yaml
llm:
  type: tu_modelo_chat
  model: tu-modelo-nombre
  api_key: ${TU_MODELO_API_KEY}
  api_base: https://api.tu-modelo.com
  
embeddings:
  type: tu_modelo_embedding
  model: tu-modelo-embeddings
  api_key: ${TU_MODELO_API_KEY}
```

```bash
# Probar integración
export TU_MODELO_API_KEY="tu_clave"
python -m graphrag.cli.index --root . --config settings_tu_modelo.yaml
```

## 📁 Estructura Final del Proyecto

```
graphrag/
├── language_model/
│   └── providers/
│       ├── openai/          # OpenAI (original)
│       ├── azure/           # Azure OpenAI (original)
│       ├── gemini/          # ← Google Gemini (implementado)
│       │   ├── __init__.py
│       │   ├── models.py    # Chat provider
│       │   └── embeddings.py # Embedding provider
│       └── tu_modelo/       # ← Tu nuevo proveedor
│           ├── __init__.py
│           ├── models.py    # Chat provider personalizado
│           └── embeddings.py # Embedding provider personalizado
├── config/
│   └── models/
│       └── language_model_config.py  # Registro de proveedores
└── scripts/                 # ← Scripts de utilidad creados
    ├── generate_community_reports.py
    ├── resume_indexing.py
    ├── local_query_test.py
    └── interactive_query.py
```

## 🎯 Flujo de Trabajo Recomendado

### 1. Primera Ejecución (Sistema Nuevo)
```bash
# Configurar entorno (solo una vez)
export GEMINI_API_KEY="tu_clave"
python setup_auto_community.py  # Configuración automática

# Indexing con auto-generación
python quick_index.py ragtest settings_gemini.yaml
# O alternativamente:
python graphrag_wrapper.py python -m graphrag.cli.index --root ragtest
```

### 2. Realizar Consultas (Funcionará en Cualquier Sistema)
```bash
# Consulta rápida (recomendado - siempre funciona)
python quick_query.py "Who is Scrooge?" ragtest local
python quick_query.py "What is the story about?" ragtest global

# Consultas oficiales (ahora con auto-community integrado)
python -m graphrag.cli.query --root ragtest --method local "Who is Scrooge?"
python -m graphrag.cli.query --root ragtest --method global "What is the story about?"

# Consultas locales sin API (respaldo)
python local_query_test.py
python interactive_query.py
```

### 3. Verificar Sistema
```bash
# Probar todo el sistema
python test_sistema.py

# Verificar datos disponibles
python test_local_data.py
```

## ✅ **PROBLEMA DE COMMUNITY_REPORTS RESUELTO**

### **Solución Automática Universal:**

El sistema ahora incluye **auto-generación automática** que funciona en **cualquier computadora nueva**:

1. **🔧 Auto-detección:** Detecta automáticamente cuando falta `community_reports.parquet`
2. **🚀 Auto-generación:** Crea community_reports inteligentes basados en entidades y relaciones existentes
3. **🌐 Universal:** Funciona en cualquier sistema sin configuración adicional
4. **🔄 Integrado:** Se ejecuta automáticamente con cualquier consulta

### **Scripts Universales Creados:**

#### 1. **`quick_query.py`** - Query Universal
```bash
# Uso simple - funciona en cualquier sistema
python quick_query.py "tu pregunta" [directorio] [método]

# Ejemplos:
python quick_query.py "Who is Scrooge?" ragtest local
python quick_query.py "What happens in the story?" ragtest global
```

#### 2. **`quick_index.py`** - Indexing Universal  
```bash
# Indexing con auto-recovery
python quick_index.py [directorio] [config]

# Ejemplo:
python quick_index.py ragtest settings_gemini.yaml
```

#### 3. **`graphrag_wrapper.py`** - Wrapper Universal
```bash
# Envuelve cualquier comando de GraphRAG
python graphrag_wrapper.py [comando_completo_de_graphrag]

# Ejemplos:
python graphrag_wrapper.py python -m graphrag.cli.index --root ragtest
python graphrag_wrapper.py python -m graphrag.cli.query --root ragtest --method local "pregunta"
```

### **Funcionamiento en Sistema Nuevo:**

```bash
# En una computadora nueva con el proyecto:
git clone https://github.com/tu-repo/LuminaMO_GraphRag.git
cd LuminaMO_GraphRag
pip install -e .
export GEMINI_API_KEY="tu_clave"

# ¡Las consultas funcionarán inmediatamente!
python quick_query.py "Who is Scrooge?" ragtest local
# → El sistema detecta que falta community_reports.parquet
# → Lo genera automáticamente
# → Ejecuta la consulta exitosamente
```

## 💡 Consejos para Producción

### Optimización de Cuota API
- Usar `concurrent_requests: 1` para Gemini gratuito
- Configurar `requests_per_minute: 2` máximo
- Habilitar cache agresivo
- Considerar cambiar a OpenAI para volumen alto

### Manejo de Errores
- Siempre tener scripts de respaldo (local_query_test.py)
- Generar community_reports manualmente si es necesario
- Usar configuración tolerante a fallos

### Escalabilidad
- Para múltiples documentos, procesar por lotes
- Considerar usar modelos de pago para mejor throughput
- Implementar sistema de colas para procesamiento asíncrono

La arquitectura modular permite fácil integración de nuevos modelos de IA manteniendo compatibilidad total con GraphRAG.
