#!/usr/bin/env python3
"""
Script de configuración post-instalación para GraphRAG + Gemini
"""

import os
import sys
import shutil
from pathlib import Path

def setup_auto_community_system():
    """Configurar el sistema automático de community_reports"""
    
    print("🔧 Configurando sistema automático de community_reports...")
    
    current_dir = Path(__file__).parent
    
    # Archivos del sistema automático
    auto_files = [
        "auto_community_generator.py",
        "graphrag_autopatch.py", 
        "graphrag_init.py",
        "graphrag_wrapper.py"
    ]
    
    # Verificar que existen todos los archivos
    missing_files = []
    for file in auto_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Faltan archivos: {missing_files}")
        return False
    
    # Hacer ejecutables los scripts principales
    executable_files = [
        "graphrag_wrapper.py",
        "auto_community_generator.py",
        "generate_community_reports.py",
        "resume_indexing.py",
        "local_query_test.py",
        "interactive_query.py",
        "test_sistema.py"
    ]
    
    for file in executable_files:
        file_path = current_dir / file
        if file_path.exists():
            os.chmod(file_path, 0o755)
            print(f"✅ {file} hecho ejecutable")
    
    # Crear alias convenientes
    create_convenience_scripts()
    
    print("✅ Sistema automático configurado correctamente")
    return True

def create_convenience_scripts():
    """Crear scripts de conveniencia para uso fácil"""
    
    current_dir = Path(__file__).parent
    
    # Script para indexing rápido
    index_script = current_dir / "quick_index.py"
    with open(index_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
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
''')
    os.chmod(index_script, 0o755)
    
    # Script para query rápido
    query_script = current_dir / "quick_query.py"
    with open(query_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
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
''')
    os.chmod(query_script, 0o755)
    
    print("✅ Scripts de conveniencia creados")

def create_startup_file():
    """Crear archivo que se ejecute al importar GraphRAG"""
    
    current_dir = Path(__file__).parent
    
    # Crear archivo de inicialización en el directorio de GraphRAG
    try:
        import graphrag
        graphrag_dir = Path(graphrag.__file__).parent
        
        startup_file = graphrag_dir / "__auto_community_init__.py"
        
        with open(startup_file, 'w') as f:
            f.write(f'''# Auto-inicialización de community_reports
# Este archivo se ejecuta automáticamente al importar GraphRAG

import sys
from pathlib import Path

# Agregar directorio del proyecto al path
project_dir = Path("{current_dir}")
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

try:
    from graphrag_init import init_graphrag_auto_community
    init_graphrag_auto_community()
except Exception as e:
    print(f"Advertencia: No se pudo inicializar auto-community: {{e}}")
''')
        
        # Agregar import en __init__.py de GraphRAG
        init_file = graphrag_dir / "__init__.py"
        if init_file.exists():
            with open(init_file, 'r') as f:
                content = f.read()
            
            if "__auto_community_init__" not in content:
                with open(init_file, 'a') as f:
                    f.write('\n# Auto-community initialization\n')
                    f.write('try:\n')
                    f.write('    from . import __auto_community_init__\n')
                    f.write('except:\n')
                    f.write('    pass\n')
                
                print("✅ Auto-inicialización integrada en GraphRAG")
            else:
                print("✅ Auto-inicialización ya integrada")
        
        return True
        
    except Exception as e:
        print(f"⚠️  No se pudo integrar en GraphRAG: {e}")
        print("El sistema funcionará manualmente")
        return False

def main():
    """Configuración principal"""
    
    print("🚀 Configurando GraphRAG + Gemini con Auto-Community")
    print("=" * 60)
    
    # Configurar sistema básico
    if not setup_auto_community_system():
        print("❌ Error en configuración básica")
        return False
    
    # Intentar integración automática
    auto_integrated = create_startup_file()
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    
    print("\n📖 CÓMO USAR:")
    print("1. Indexing rápido:")
    print("   python quick_index.py [directorio] [config]")
    print("   python quick_index.py ragtest settings_gemini.yaml")
    
    print("\n2. Query rápido:")
    print("   python quick_query.py 'tu pregunta' [directorio] [método]")
    print("   python quick_query.py 'Who is Scrooge?' ragtest local")
    
    print("\n3. Wrapper universal:")
    print("   python graphrag_wrapper.py python -m graphrag.cli.index --root ragtest")
    print("   python graphrag_wrapper.py python -m graphrag.cli.query --root ragtest --method local 'pregunta'")
    
    print("\n4. Scripts originales (ahora con auto-community):")
    print("   python local_query_test.py")
    print("   python interactive_query.py")
    print("   python test_sistema.py")
    
    if auto_integrated:
        print("\n🎉 INTEGRACIÓN AUTOMÁTICA ACTIVADA")
        print("Los comandos normales de GraphRAG ahora incluyen auto-community:")
        print("python -m graphrag.cli.query --root ragtest --method local 'pregunta'")
    else:
        print("\n⚠️  MODO MANUAL")
        print("Usa los scripts wrapper para asegurar community_reports")
    
    print("\n💡 El sistema automáticamente generará community_reports.parquet")
    print("   cuando sea necesario, en cualquier computadora nueva.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
