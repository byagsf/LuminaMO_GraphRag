# 🚀 GraphRAG + Gemini - Inicio Rápido

## ⚡ Configuración en 3 Pasos

```bash
# 1. Instalar
git clone https://github.com/byagsf/LuminaMO_GraphRag.git
cd LuminaMO_GraphRag
pip install -e .
pip install google-generativeai

# 2. Configurar API
export GEMINI_API_KEY="tu_clave_de_gemini"

# 3. Configurar sistema automático (solo una vez)
python setup_auto_community.py
```

## 🔥 Uso Inmediato

```bash
# Indexing (procesar documentos)
python quick_index.py ragtest

# Consultas (funcionan siempre, en cualquier sistema)
python quick_query.py "Who is Scrooge?" ragtest local
python quick_query.py "What is the story about?" ragtest global
```

## 🎯 **PROBLEMA RESUELTO: Community Reports Automáticos**

### ❌ **Problema Original:**
- `"Could not find community_reports.parquet"` en sistemas nuevos
- Consultas fallaban si el indexing no completaba 100%
- Manual fixes requeridos en cada computadora

### ✅ **Solución Implementada:**
- **Auto-detección y generación** de community_reports
- **Funciona en cualquier computadora nueva** sin configuración
- **Integrado automáticamente** en todas las consultas
- **Sin intervención manual** requerida

## 🛠️ Scripts Universales

| Script | Propósito | Ejemplo |
|--------|-----------|---------|
| `quick_query.py` | Consultas universales | `python quick_query.py "pregunta" ragtest local` |
| `quick_index.py` | Indexing con auto-recovery | `python quick_index.py ragtest` |
| `graphrag_wrapper.py` | Wrapper para comandos oficiales | `python graphrag_wrapper.py python -m graphrag.cli.query --root ragtest --method local "pregunta"` |
| `local_query_test.py` | Consultas sin API (respaldo) | `python local_query_test.py` |
| `test_sistema.py` | Verificar que todo funciona | `python test_sistema.py` |

## 🌐 Portabilidad Total

### En Sistema Nuevo:
```bash
# 1. Clonar proyecto
git clone https://tu-repo.git
cd proyecto

# 2. Solo instalar dependencias
pip install -e .
export GEMINI_API_KEY="clave"

# 3. ¡Consultas funcionan inmediatamente!
python quick_query.py "Who is Scrooge?" ragtest local
# → Auto-detecta community_reports faltante
# → Lo genera automáticamente  
# → Ejecuta consulta exitosamente ✅
```

### Con Datos Existentes:
```bash
# Si ya tienes entities.parquet, relationships.parquet, text_units.parquet
# El sistema automáticamente genera community_reports.parquet inteligente
# basado en los datos existentes
```

## 📊 Tipos de Community Reports Generados

El sistema automático crea community reports inteligentes:

1. **Por Tipo de Entidad:** Agrupa entidades similares (PERSON, PLACE, etc.)
2. **Por Conectividad:** Identifica entidades altamente conectadas
3. **General:** Comunidad global que abarca todo el documento
4. **Fallback:** Comunidad básica si todo lo demás falla

## 🔧 Integración con Gemini

### Archivos Modificados:
- `graphrag/language_model/providers/gemini/models.py` - Proveedor principal
- Sistema de filtrado de parámetros incompatibles
- Manejo automático de rate limits
- Auto-generación de community_reports

### Para Agregar Nuevo Modelo:
Ver sección completa en `DOCUMENTACION_COMPLETA.md`

## 🎉 Estado Final

- ✅ **GraphRAG + Gemini** completamente funcional
- ✅ **Community_reports** se generan automáticamente
- ✅ **Portabilidad total** - funciona en cualquier sistema
- ✅ **Sin configuración manual** requerida
- ✅ **Consultas universales** siempre funcionan

**¡El proyecto está listo para producción y despliegue universal!** 🚀
