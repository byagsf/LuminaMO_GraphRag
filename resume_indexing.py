#!/usr/bin/env python3
"""
Script para reanudar indexing de GraphRAG paso a paso y manejar fallos
"""

import subprocess
import sys
import time
from pathlib import Path
import pandas as pd

def check_file_exists(file_path):
    """Verificar si un archivo existe y se puede leer"""
    path = Path(file_path)
    if not path.exists():
        return False
    try:
        # Intentar leer para verificar integridad
        if path.suffix == '.parquet':
            pd.read_parquet(path)
        return True
    except:
        return False

def get_file_status(output_dir):
    """Obtener estado de todos los archivos de salida"""
    output_path = Path(output_dir)
    
    files_status = {
        "entities.parquet": check_file_exists(output_path / "entities.parquet"),
        "relationships.parquet": check_file_exists(output_path / "relationships.parquet"), 
        "text_units.parquet": check_file_exists(output_path / "text_units.parquet"),
        "community_reports.parquet": check_file_exists(output_path / "community_reports.parquet")
    }
    
    return files_status

def run_indexing_with_retry(root_dir, config_file, max_retries=2):
    """Ejecutar indexing con reintentos"""
    
    for attempt in range(max_retries + 1):
        print(f"🔄 Intento {attempt + 1}/{max_retries + 1} de indexing...")
        
        try:
            # Comando de indexing
            cmd = [
                "python", "-m", "graphrag.cli.index",
                "--root", root_dir,
                "--config", config_file
            ]
            
            # Agregar --resume si no es el primer intento
            if attempt > 0:
                cmd.append("--resume")
            
            print(f"Ejecutando: {' '.join(cmd)}")
            
            # Ejecutar con timeout extendido
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=7200  # 2 horas timeout
            )
            
            if result.returncode == 0:
                print(f"✅ Indexing completado en intento {attempt + 1}")
                return True
            else:
                print(f"❌ Indexing falló en intento {attempt + 1}:")
                print("STDOUT:", result.stdout[-1000:])  # Últimas 1000 chars
                print("STDERR:", result.stderr[-1000:])
                
                # Si no es el último intento, esperar antes de reintentar
                if attempt < max_retries:
                    print("⏳ Esperando 30 segundos antes del siguiente intento...")
                    time.sleep(30)
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Indexing excedió tiempo límite en intento {attempt + 1}")
            if attempt < max_retries:
                print("⏳ Esperando 60 segundos antes del siguiente intento...")
                time.sleep(60)
        except Exception as e:
            print(f"❌ Error inesperado en intento {attempt + 1}: {e}")
            if attempt < max_retries:
                time.sleep(30)
    
    return False

def create_fallback_community_reports(output_dir):
    """Crear community_reports de respaldo si el indexing falla"""
    print("\n🛠️  Creando community_reports de respaldo...")
    
    try:
        # Importar y usar el generador
        import sys
        sys.path.append('.')
        
        # Ejecutar script de generación
        result = subprocess.run([
            "python", "generate_community_reports.py", output_dir
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Community reports de respaldo creado")
            return True
        else:
            print(f"❌ Error creando respaldo: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error al crear respaldo: {e}")
        return False

def main():
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    config_file = sys.argv[2] if len(sys.argv) > 2 else "settings.yaml"
    
    output_dir = Path(root_dir) / "output"
    
    print("🚀 Script de Recuperación de Indexing GraphRAG")
    print("=" * 50)
    print(f"Directorio de trabajo: {root_dir}")
    print(f"Archivo de configuración: {config_file}")
    print(f"Directorio de salida: {output_dir}")
    
    # Verificar estado inicial
    print("\n🔍 Verificando estado actual...")
    initial_status = get_file_status(output_dir)
    
    missing_files = [file for file, exists in initial_status.items() if not exists]
    existing_files = [file for file, exists in initial_status.items() if exists]
    
    print(f"✅ Archivos existentes: {len(existing_files)}")
    for file in existing_files:
        print(f"   • {file}")
    
    print(f"❌ Archivos faltantes: {len(missing_files)}")
    for file in missing_files:
        print(f"   • {file}")
    
    # Decidir estrategia basada en archivos existentes
    if len(existing_files) == 4:
        print("\n🎉 ¡Todos los archivos están disponibles!")
        print("No es necesario ejecutar indexing.")
        print("Puedes ejecutar consultas directamente:")
        print(f"python -m graphrag.cli.query --root {root_dir} --method local 'tu pregunta'")
        return
    
    elif len(existing_files) >= 3 and "community_reports.parquet" in missing_files:
        print("\n⚠️  Solo falta community_reports.parquet")
        print("Intentando crear de forma manual...")
        
        if create_fallback_community_reports(output_dir):
            print("\n🎉 ¡Problema resuelto! Todos los archivos disponibles.")
            return
        else:
            print("\n🔄 Fallback falló, intentando indexing completo...")
    
    elif len(existing_files) > 0:
        print(f"\n🔄 Faltan {len(missing_files)} archivos, intentando reanudar indexing...")
    else:
        print("\n🔄 No hay archivos, ejecutando indexing completo...")
    
    # Ejecutar indexing con reintentos
    success = run_indexing_with_retry(root_dir, config_file)
    
    # Verificar resultado final
    print("\n📊 Verificando resultado final...")
    final_status = get_file_status(output_dir)
    final_existing = [file for file, exists in final_status.items() if exists]
    final_missing = [file for file, exists in final_status.items() if not exists]
    
    print(f"✅ Archivos finales: {len(final_existing)}/4")
    
    if len(final_existing) == 4:
        print("\n🎉 ¡Indexing completamente exitoso!")
        print("Puedes ejecutar consultas:")
        print(f"python -m graphrag.cli.query --root {root_dir} --method local 'tu pregunta'")
        print(f"python -m graphrag.cli.query --root {root_dir} --method global 'tu pregunta'")
        
    elif len(final_existing) >= 3:
        print(f"\n⚠️  Indexing parcialmente exitoso (faltan: {final_missing})")
        
        # Intentar crear community_reports si es lo único que falta
        if "community_reports.parquet" in final_missing and len(final_missing) == 1:
            print("Intentando crear community_reports faltante...")
            if create_fallback_community_reports(output_dir):
                print("🎉 ¡Problema resuelto!")
            else:
                print("⚠️  Usa consultas locales mientras tanto:")
                print("python local_query_test.py")
                print("python interactive_query.py")
        else:
            print("⚠️  Usa consultas locales:")
            print("python local_query_test.py")
    else:
        print("\n❌ Indexing falló")
        print("Posibles soluciones:")
        print("1. Verificar API key de Gemini")
        print("2. Verificar cuota de API disponible") 
        print("3. Cambiar a OpenAI en settings.yaml")
        print("4. Usar modelo local (Ollama)")
        print("\nMientras tanto, si hay algunos archivos:")
        print("python local_query_test.py")

if __name__ == "__main__":
    main()
