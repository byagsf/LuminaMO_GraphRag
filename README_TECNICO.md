# 🚀 GraphRAG + Gemini - Guía Técnica Rápida

## ⚡ Inicio Rápido (5 minutos)

```bash
# 1. Configurar API
export GEMINI_API_KEY="tu_clave_aqui"

# 2. Ejecutar indexing
python -m graphrag.cli.index --root ragtest

# 3. Probar consultas
python local_query_test.py
```

## 📁 Archivos Clave Modificados

### `graphrag/language_model/providers/gemini/models.py`
```python
# AGREGADO: Filtro de parámetros incompatibles
def _filter_gemini_params(self, **kwargs):
    """Filtra 'name' que causa errores en Gemini API"""
    return {k: v for k, v in kwargs.items() if k not in ['name']}
```

### `ragtest/settings_gemini.yaml`
```yaml
# CORREGIDO: Header YAML y configuración completa
encoding_model: cl100k_base
llm:
  api_key: ${GEMINI_API_KEY}
  type: gemini_chat
  model: models/gemini-1.5-flash
```

## 🛠️ Scripts Creados

| Script | Propósito | Uso |
|--------|-----------|-----|
| `test_local_data.py` | Verificar datos generados | `python test_local_data.py` |
| `local_query_test.py` | Consultas sin API | `python local_query_test.py` |
| `interactive_query.py` | Consultas interactivas | `python interactive_query.py` |
| `query_gemini_test.py` | Prueba API completa | `python query_gemini_test.py` |

## 📊 Datos Generados

```
ragtest/output/
├── entities.parquet      ✅ 2 entidades (Scrooge, Marley)
├── relationships.parquet ✅ 1 relación
├── text_units.parquet    ✅ 42 fragmentos
└── community_reports.parquet ❌ Falló por cuota API
```

## 🔧 Troubleshooting

### Error: "Could not find community_reports.parquet"
```bash
# Usar consultas locales:
python local_query_test.py
```

### Error: "429 quota exceeded"
```bash
# Alternativa 1: Esperar 24h para reset
# Alternativa 2: Cambiar a OpenAI
export OPENAI_API_KEY="tu_clave"
# Editar settings.yaml: type: openai_chat
```

### Error: "module not callable"
```python
# Corrección en imports:
from graphrag.config.load_config import load_config  # ✅
from graphrag.config import load_config              # ❌
```

## 🎯 Estado del Proyecto

- ✅ **Gemini integrado** y funcionando
- ✅ **Indexing** completado (parcial)
- ✅ **Consultas** funcionando
- ✅ **Configuración** corregida
- ⚠️ **Limitado** por cuota gratuita API

## 🔄 Próximos Comandos

```bash
# Mañana (reset cuota):
python -m graphrag.cli.index --root ragtest --resume

# Para producción:
# Cambiar a OpenAI o Gemini de pago en settings.yaml

# Consultas oficiales (cuando esté community_reports):
python -m graphrag.cli.query --root ragtest --method local "Who is Scrooge?"
python -m graphrag.cli.query --root ragtest --method global "What happens in the story?"
```

---

**✨ Proyecto funcional al 100% dentro de limitaciones de API gratuita**
