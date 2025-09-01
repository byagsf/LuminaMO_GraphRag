#!/usr/bin/env python3
"""
Inicializador automático para GraphRAG + Gemini
Se ejecuta automáticamente al importar GraphRAG para asegurar community_reports
"""

import sys
import os
from pathlib import Path

# Asegurar que el directorio actual esté en el path
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def init_graphrag_auto_community():
    """Inicializar el sistema automático de community_reports"""
    
    try:
        # Importar y aplicar parches
        from graphrag_autopatch import apply_all_patches
        from auto_community_generator import ensure_community_reports
        
        # Aplicar parches automáticos
        apply_all_patches()
        
        # Definir función global para uso fácil
        def auto_ensure_community_reports(output_dir=None):
            """Función global para asegurar community_reports"""
            if output_dir is None:
                # Buscar directorios comunes
                common_dirs = ["./output", "./ragtest/output", "../output"]
                for dir_path in common_dirs:
                    if Path(dir_path).exists():
                        output_dir = dir_path
                        break
            
            if output_dir and Path(output_dir).exists():
                return ensure_community_reports(output_dir)
            return False
        
        # Hacer disponible globalmente
        import builtins
        builtins.auto_ensure_community_reports = auto_ensure_community_reports
        
        print("✅ Sistema automático de community_reports inicializado")
        return True
        
    except Exception as e:
        print(f"⚠️  Advertencia: No se pudo inicializar sistema automático: {e}")
        return False

# Auto-inicializar al importar
if __name__ != "__main__":
    init_graphrag_auto_community()

if __name__ == "__main__":
    # Prueba manual
    print("🧪 Probando inicializador automático...")
    success = init_graphrag_auto_community()
    
    if success:
        print("✅ Inicializador funcionando")
        
        # Probar función global
        try:
            result = auto_ensure_community_reports("./ragtest/output")
            print(f"✅ Función global funcionando: {result}")
        except NameError:
            print("❌ Función global no disponible")
    else:
        print("❌ Error en inicializador")
