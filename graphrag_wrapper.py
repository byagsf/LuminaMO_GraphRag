#!/usr/bin/env python3
"""
Wrapper universal para GraphRAG que asegura community_reports en cualquier sistema
"""

import sys
import os
import subprocess
from pathlib import Path
import argparse

# Asegurar que el directorio actual esté en el path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from auto_community_generator import ensure_community_reports

def run_graphrag_with_auto_community(command_args):
    """Ejecutar comando de GraphRAG asegurando community_reports"""
    
    # Detectar directorio root del comando
    root_dir = "."
    if "--root" in command_args:
        root_index = command_args.index("--root")
        if root_index + 1 < len(command_args):
            root_dir = command_args[root_index + 1]
    
    output_dir = Path(root_dir) / "output"
    
    print(f"🚀 Ejecutando GraphRAG con auto-community en: {root_dir}")
    
    try:
        # Ejecutar comando original
        result = subprocess.run(command_args, capture_output=False, text=True)
        
        # Después de cualquier comando, asegurar community_reports
        if output_dir.exists():
            print("\n🔧 Verificando/generando community_reports...")
            success = ensure_community_reports(str(output_dir))
            if success:
                print("✅ Community reports disponibles")
            else:
                print("⚠️  Advertencia: No se pudieron generar community_reports")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error ejecutando GraphRAG: {e}")
        
        # Incluso si falla, intentar generar community_reports
        if output_dir.exists():
            print("🛠️  Intentando generar community_reports después del error...")
            ensure_community_reports(str(output_dir))
        
        return 1

def main():
    """Función principal del wrapper"""
    
    if len(sys.argv) < 2:
        print("📖 Uso: python graphrag_wrapper.py <comando_graphrag> [argumentos...]")
        print("\nEjemplos:")
        print("  python graphrag_wrapper.py python -m graphrag.cli.index --root ragtest")
        print("  python graphrag_wrapper.py python -m graphrag.cli.query --root ragtest --method local 'pregunta'")
        print("\nEste wrapper asegura que community_reports.parquet esté siempre disponible.")
        return 1
    
    # Pasar todos los argumentos excepto el nombre del script
    command_args = sys.argv[1:]
    
    return run_graphrag_with_auto_community(command_args)

# Funciones de conveniencia
def index_with_auto_community(root_dir=".", config_file=None):
    """Ejecutar indexing con auto-generación de community_reports"""
    
    cmd = ["python", "-m", "graphrag.cli.index", "--root", root_dir]
    if config_file:
        cmd.extend(["--config", config_file])
    
    print(f"🔍 Ejecutando indexing en: {root_dir}")
    return run_graphrag_with_auto_community(cmd)

def query_with_auto_community(question, root_dir=".", method="local", config_file=None):
    """Ejecutar query con auto-generación de community_reports"""
    
    cmd = ["python", "-m", "graphrag.cli.query", "--root", root_dir, "--method", method, question]
    if config_file:
        cmd.extend(["--config", config_file])
    
    print(f"❓ Ejecutando query: '{question}'")
    return run_graphrag_with_auto_community(cmd)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
