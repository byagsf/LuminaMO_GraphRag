#!/usr/bin/env python3
"""Script rápido para queries con auto-community"""
import sys
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from graphrag_wrapper import query_with_auto_community

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python quick_query.py 'tu pregunta' [root_dir] [method]")
        print("Ejemplo: python quick_query.py 'Who is Scrooge?' ragtest local")
        sys.exit(1)
    
    question = sys.argv[1]
    root_dir = sys.argv[2] if len(sys.argv) > 2 else "ragtest"
    method = sys.argv[3] if len(sys.argv) > 3 else "local"
    
    print(f"❓ Query rápido: '{question}'")
    exit_code = query_with_auto_community(question, root_dir, method)
    sys.exit(exit_code)
