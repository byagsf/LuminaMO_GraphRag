#!/usr/bin/env python3
"""Script rápido para indexing con auto-community"""
import sys
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from graphrag_wrapper import index_with_auto_community

if __name__ == "__main__":
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "ragtest"
    config_file = sys.argv[2] if len(sys.argv) > 2 else "settings_gemini.yaml"
    
    print(f"🚀 Indexing rápido en: {root_dir}")
    exit_code = index_with_auto_community(root_dir, config_file)
    sys.exit(exit_code)
