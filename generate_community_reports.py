#!/usr/bin/env python3
"""
Script para generar community_reports.parquet cuando falla el indexing
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json

def create_minimal_community_reports(output_dir):
    """Crear community_reports.parquet mínimo para evitar errores"""
    
    output_path = Path(output_dir)
    
    # Verificar si ya existe
    community_file = output_path / "community_reports.parquet"
    if community_file.exists():
        print("✅ community_reports.parquet ya existe")
        return True
    
    try:
        # Cargar entidades para crear comunidades básicas
        entities_file = output_path / "entities.parquet"
        if not entities_file.exists():
            print("❌ No se encontró entities.parquet")
            return False
        
        entities = pd.read_parquet(entities_file)
        print(f"📊 Cargadas {len(entities)} entidades")
        
        # Crear comunidades básicas agrupando por tipo de entidad
        communities = []
        entity_types = entities['type'].unique() if 'type' in entities.columns else ['UNKNOWN']
        
        for i, entity_type in enumerate(entity_types):
            if 'type' in entities.columns:
                type_entities = entities[entities['type'] == entity_type]
            else:
                type_entities = entities
            
            # Obtener muestra de entidades para el resumen
            entity_sample = type_entities['title'].head(3).tolist() if 'title' in type_entities.columns else ['Entity']
            entity_names = ", ".join(entity_sample)
            
            community = {
                'id': f'community_{i}',
                'human_readable_id': i,
                'level': 0,
                'title': f'{entity_type} Community',
                'summary': f'Community of {entity_type} entities including: {entity_names}{"..." if len(type_entities) > 3 else ""}',
                'full_content': f'This community contains {len(type_entities)} entities of type {entity_type}. Main entities: {entity_names}',
                'rank': float(len(type_entities)),  # Usar cantidad como rank
                'rank_explanation': f'Community ranked by entity count: {len(type_entities)} entities',
                'findings': [f'Contains {len(type_entities)} {entity_type} entities'],
                'full_content_json': json.dumps({
                    "summary": f"Community of {entity_type} entities",
                    "entities": len(type_entities),
                    "main_entities": entity_sample
                })
            }
            communities.append(community)
        
        # Si no hay comunidades por tipo, crear una comunidad general
        if not communities:
            communities.append({
                'id': 'community_0',
                'human_readable_id': 0,
                'level': 0,
                'title': 'General Community',
                'summary': f'General community containing all {len(entities)} entities',
                'full_content': f'This is a general community containing all entities from the document.',
                'rank': float(len(entities)),
                'rank_explanation': f'General community with {len(entities)} entities',
                'findings': [f'Contains {len(entities)} total entities'],
                'full_content_json': json.dumps({
                    "summary": "General community of all entities",
                    "entities": len(entities)
                })
            })
        
        # Crear DataFrame y guardar
        community_df = pd.DataFrame(communities)
        community_df.to_parquet(community_file)
        
        print(f"✅ Creado community_reports.parquet con {len(communities)} comunidades")
        print("📋 Comunidades creadas:")
        for community in communities:
            print(f"   • {community['title']}: {community['summary']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear community_reports: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_all_files(output_dir):
    """Verificar que todos los archivos necesarios existen"""
    output_path = Path(output_dir)
    
    required_files = [
        "entities.parquet",
        "relationships.parquet", 
        "text_units.parquet",
        "community_reports.parquet"
    ]
    
    print("🔍 Verificando archivos necesarios:")
    all_exist = True
    
    for file in required_files:
        file_path = output_path / file
        if file_path.exists():
            try:
                df = pd.read_parquet(file_path)
                print(f"✅ {file} - {len(df)} registros")
            except Exception as e:
                print(f"⚠️  {file} - Existe pero error al leer: {e}")
                all_exist = False
        else:
            print(f"❌ {file} - No encontrado")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    import sys
    
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./output"
    
    print("🚀 Generador de Community Reports")
    print("=" * 50)
    
    # Verificar estado actual
    if not verify_all_files(output_dir):
        print("\n📝 Intentando generar community_reports faltante...")
        success = create_minimal_community_reports(output_dir)
        
        if success:
            print("\n🎉 ¡Community reports generado exitosamente!")
            print("Ahora puedes ejecutar consultas:")
            print("python -m graphrag.cli.query --root . --method local 'tu pregunta'")
        else:
            print("\n❌ No se pudo generar community_reports")
            print("Usa consultas locales mientras tanto:")
            print("python local_query_test.py")
    else:
        print("\n🎉 ¡Todos los archivos están disponibles!")
        print("Puedes ejecutar consultas normalmente.")
