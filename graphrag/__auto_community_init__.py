# Auto-inicialización de community_reports
# Este archivo se ejecuta automáticamente al importar GraphRAG

import sys
from pathlib import Path

# Agregar directorio del proyecto al path
project_dir = Path("/home/charizardbellako/Documentos/GraphRAG/LuminaMO_GraphRag")
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

try:
    from graphrag_init import init_graphrag_auto_community
    init_graphrag_auto_community()
except Exception as e:
    print(f"Advertencia: No se pudo inicializar auto-community: {e}")
