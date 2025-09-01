#!/usr/bin/env python3
"""
Script para probar la carga de datos GraphRAG sin usar la API
"""

import pandas as pd
from pathlib import Path

def test_local_data():
    """Prueba de carga de datos locales sin API"""
    
    print("🚀 Probando carga de datos GraphRAG locales")
    
    # Directorio de datos
    root_dir = Path("/home/charizardbellako/Documentos/GraphRAG/LuminaMO_GraphRag/ragtest")
    output_dir = root_dir / "output"
    
    print(f"📁 Directorio de salida: {output_dir}")
    
    # Verificar archivos disponibles
    available_files = []
    parquet_files = ["entities.parquet", "relationships.parquet", "text_units.parquet", 
                    "community_reports.parquet", "create_final_nodes.parquet", 
                    "create_final_edges.parquet"]
    
    for file in parquet_files:
        file_path = output_dir / file
        if file_path.exists():
            available_files.append(file)
            print(f"✅ {file} - Existe")
        else:
            print(f"❌ {file} - No encontrado")
    
    print(f"\n📊 Archivos disponibles: {len(available_files)}/{len(parquet_files)}")
    
    # Cargar y mostrar estadísticas de archivos disponibles
    for file in available_files:
        try:
            file_path = output_dir / file
            df = pd.read_parquet(file_path)
            print(f"\n=== {file} ===")
            print(f"Registros: {len(df)}")
            print(f"Columnas: {list(df.columns)}")
            
            # Mostrar primeras filas para entidades
            if file == "entities.parquet" and len(df) > 0:
                print("\nPrimeras 3 entidades:")
                print(df[['title', 'type', 'description']].head(3).to_string())
            
            # Mostrar primeras filas para relaciones
            elif file == "relationships.parquet" and len(df) > 0:
                print("\nPrimeras 3 relaciones:")
                if 'source' in df.columns and 'target' in df.columns:
                    print(df[['source', 'target', 'description']].head(3).to_string())
                else:
                    print(df.head(3).to_string())
            
            # Mostrar estadísticas para text_units
            elif file == "text_units.parquet" and len(df) > 0:
                print("\nPrimeras 2 unidades de texto:")
                if 'text' in df.columns:
                    for i, text in enumerate(df['text'].head(2)):
                        print(f"Texto {i+1}: {text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error al cargar {file}: {e}")
    
    # Verificar configuración
    config_path = root_dir / "settings_gemini.yaml"
    if config_path.exists():
        print(f"\n✅ Configuración encontrada: {config_path}")
    else:
        print(f"\n❌ Configuración no encontrada: {config_path}")
    
    # Sugerencias
    print("\n💡 Sugerencias:")
    if len(available_files) > 0:
        print("- Los datos se han generado correctamente")
        print("- Puedes usar estos datos para consultas locales")
        if "community_reports.parquet" not in available_files:
            print("- community_reports.parquet falta (probablemente por límites de API)")
            print("- Esto no impide hacer consultas básicas con entidades y relaciones")
    else:
        print("- No se encontraron datos. Ejecuta primero el indexing:")
        print("  python -m graphrag.cli.index --root ragtest")
    
    print("- Para evitar límites de API, considera usar OpenAI o un modelo local")
    print("- La cuota gratuita de Gemini es de 50 requests/día")

if __name__ == "__main__":
    test_local_data()
