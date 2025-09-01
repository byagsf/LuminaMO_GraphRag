# 🔧 CONFIGURACIÓN Y COMANDOS - GraphRAG + Gemini

## 📋 Variables de Entorno Necesarias

```bash
# Gemini API (actual)
export GEMINI_API_KEY="AIzaSy..."

# OpenAI API (alternativa)
export OPENAI_API_KEY="sk-..."

# Verificar configuración
echo $GEMINI_API_KEY
```

## 🎛️ Configuraciones de settings.yaml

### Configuración Actual (Gemini)
```yaml
# ragtest/settings_gemini.yaml
encoding_model: cl100k_base
skip_workflows: []

llm:
  api_key: ${GEMINI_API_KEY}
  type: gemini_chat
  model: models/gemini-1.5-flash
  temperature: 0.0
  top_p: 1.0
  max_tokens: 4000
  request_timeout: 180.0
  api_base: null
  api_version: null
  proxy: null
  cognitive_services_endpoint: null
  deployment_name: null
  model_supports_json: true
  tokens_per_minute: 0
  requests_per_minute: 0
  max_retries: 10
  max_retry_wait: 10.0
  sleep_on_rate_limit_recommendation: true
  concurrent_requests: 25

parallelization:
  stagger: 0.3
  num_threads: 50

async_mode: threaded

embeddings:
  api_key: ${GEMINI_API_KEY}
  type: gemini_embedding
  model: models/text-embedding-004
  # ... resto de configuración
```

### Configuración OpenAI (Alternativa)
```yaml
# Para cambiar a OpenAI, modificar:
llm:
  api_key: ${OPENAI_API_KEY}
  type: openai_chat
  model: gpt-4o-mini  # Más económico
  # o model: gpt-4o    # Más potente

embeddings:
  api_key: ${OPENAI_API_KEY}
  type: openai_embedding
  model: text-embedding-3-small
```

### Configuración Local (Ollama)
```yaml
# Para modelo local:
llm:
  api_base: http://localhost:11434/v1
  type: openai_chat  # Compatible con Ollama
  model: llama3.2
  api_key: "not-needed"
```

## 🚀 Comandos de Ejecución

### Indexing (Procesamiento)
```bash
# Indexing completo desde cero
python -m graphrag.cli.index --root ragtest

# Reanudar indexing interrumpido
python -m graphrag.cli.index --root ragtest --resume

# Indexing con configuración específica
python -m graphrag.cli.index --root ragtest --config settings_gemini.yaml

# Indexing con verbosidad
python -m graphrag.cli.index --root ragtest --verbose

# Limpiar y empezar de nuevo
rm -rf ragtest/output/*
python -m graphrag.cli.index --root ragtest
```

### Consultas Oficiales
```bash
# Búsqueda local (contexto específico)
python -m graphrag.cli.query \
  --root ragtest \
  --method local \
  "Who is Scrooge and what is his personality?"

# Búsqueda global (vista general)
python -m graphrag.cli.query \
  --root ragtest \
  --method global \
  "Summarize the main themes of the story"

# Con configuración específica
python -m graphrag.cli.query \
  --root ragtest \
  --config settings_gemini.yaml \
  --method local \
  "What is Marley's role in the story?"
```

### Scripts Personalizados
```bash
# Verificar datos disponibles
python test_local_data.py

# Consultas automatizadas sin API
python local_query_test.py

# Consultas interactivas
python interactive_query.py

# Probar conexión con Gemini
python query_gemini_test.py
```

## 🔍 Comandos de Diagnóstico

### Verificar Estado del Sistema
```bash
# Ver archivos generados
ls -la ragtest/output/

# Verificar tamaños de archivos
du -h ragtest/output/*.parquet

# Contar registros en datos
python -c "
import pandas as pd
from pathlib import Path
output_dir = Path('ragtest/output')
for file in ['entities.parquet', 'relationships.parquet', 'text_units.parquet']:
    if (output_dir / file).exists():
        df = pd.read_parquet(output_dir / file)
        print(f'{file}: {len(df)} registros')
"

# Ver logs de indexing
tail -n 50 ragtest/output/indexing-engine.log

# Verificar configuración
cat ragtest/settings_gemini.yaml | head -20
```

### Monitoreo de API
```bash
# Probar conexión a Gemini (fuera de GraphRAG)
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Hello, world!')
print('✅ Gemini conectado:', response.text[:50])
"

# Verificar cuota restante (no directo, pero probar request)
python -c "
try:
    import google.generativeai as genai
    import os
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content('Test')
    print('✅ Cuota disponible')
except Exception as e:
    if '429' in str(e):
        print('❌ Cuota agotada')
    else:
        print(f'❌ Error: {e}')
"
```

## 🔧 Comandos de Mantenimiento

### Limpiar y Reiniciar
```bash
# Limpiar solo outputs (mantener cache)
rm -rf ragtest/output/*.parquet

# Limpiar todo (incluir cache)
rm -rf ragtest/output/*
rm -rf ragtest/cache/*

# Backup de datos
cp -r ragtest/output/ ragtest/backup_$(date +%Y%m%d)/

# Restaurar backup
cp -r ragtest/backup_20250901/* ragtest/output/
```

### Optimización
```bash
# Verificar uso de memoria durante indexing
htop

# Limitar threads si hay problemas de memoria
# Editar settings.yaml:
# parallelization:
#   num_threads: 10  # Reducir de 50

# Monitorear requests por minuto
# Ver logs en tiempo real:
tail -f ragtest/output/indexing-engine.log | grep -i "request\|error\|rate"
```

## 📊 Análisis de Resultados

### Explorar Datos Generados
```bash
# Entidades más frecuentes
python -c "
import pandas as pd
df = pd.read_parquet('ragtest/output/entities.parquet')
print(df[['title', 'type', 'frequency']].sort_values('frequency', ascending=False))
"

# Relaciones por peso
python -c "
import pandas as pd
df = pd.read_parquet('ragtest/output/relationships.parquet')
print(df[['source', 'target', 'weight']].sort_values('weight', ascending=False))
"

# Estadísticas de texto
python -c "
import pandas as pd
df = pd.read_parquet('ragtest/output/text_units.parquet')
print(f'Fragmentos: {len(df)}')
print(f'Tokens promedio: {df[\"n_tokens\"].mean():.1f}')
print(f'Tokens total: {df[\"n_tokens\"].sum()}')
"
```

## 🎯 Configuraciones Recomendadas

### Para Desarrollo (Rápido)
```yaml
chunks:
  size: 200
  overlap: 50
entity_extraction:
  max_gleanings: 1
parallelization:
  num_threads: 10
```

### Para Producción (Calidad)
```yaml
chunks:
  size: 400
  overlap: 100
entity_extraction:
  max_gleanings: 3
parallelization:
  num_threads: 25
```

### Para API Limitada (Gemini Free)
```yaml
llm:
  requests_per_minute: 2  # Muy conservador
  sleep_on_rate_limit_recommendation: true
  max_retries: 5
parallelization:
  num_threads: 1
  stagger: 30  # 30 segundos entre requests
```

---

**📝 Nota:** Este archivo contiene todos los comandos y configuraciones utilizados en el proyecto. Usar como referencia rápida para futuras ejecuciones.
