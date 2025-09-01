#!/usr/bin/env python3
"""
Consultas interactivas con datos GraphRAG locales
"""

import pandas as pd
from pathlib import Path
import json

def load_graphrag_data():
    """Cargar datos GraphRAG"""
    root_dir = Path("/home/charizardbellako/Documentos/GraphRAG/LuminaMO_GraphRag/ragtest")
    output_dir = root_dir / "output"
    
    data = {}
    entities_path = output_dir / "entities.parquet"
    if entities_path.exists():
        data['entities'] = pd.read_parquet(entities_path)
    
    relationships_path = output_dir / "relationships.parquet"
    if relationships_path.exists():
        data['relationships'] = pd.read_parquet(relationships_path)
    
    text_units_path = output_dir / "text_units.parquet"
    if text_units_path.exists():
        data['text_units'] = pd.read_parquet(text_units_path)
    
    return data

def interactive_query():
    """Consultas interactivas"""
    print("🚀 Sistema de Consultas GraphRAG Interactivo")
    print("=" * 50)
    
    data = load_graphrag_data()
    if not data:
        print("❌ No se pudieron cargar los datos")
        return
    
    print(f"✅ Datos cargados:")
    print(f"   • Entidades: {len(data.get('entities', []))}")
    print(f"   • Relaciones: {len(data.get('relationships', []))}")
    print(f"   • Unidades de texto: {len(data.get('text_units', []))}")
    
    # Mostrar entidades disponibles
    if 'entities' in data:
        print(f"\n📍 Entidades disponibles:")
        for _, entity in data['entities'].iterrows():
            print(f"   • {entity['title']} ({entity['type']})")
    
    print(f"\n🔍 Consultas sugeridas:")
    print("   1. 'scrooge' - Información sobre Scrooge")
    print("   2. 'marley' - Información sobre Marley")
    print("   3. 'relationship' - Ver relaciones")
    print("   4. 'text' - Ver fragmentos de texto")
    print("   5. 'quit' - Salir")
    
    while True:
        query = input(f"\n➤ Tu consulta: ").strip().lower()
        
        if query in ['quit', 'exit', 'salir']:
            print("👋 ¡Hasta luego!")
            break
        
        if query == 'scrooge':
            entity = data['entities'][data['entities']['title'] == 'SCROOGE'].iloc[0]
            print(f"\n📍 SCROOGE:")
            print(f"   Tipo: {entity['type']}")
            print(f"   Descripción: {entity['description']}")
        
        elif query == 'marley':
            entity = data['entities'][data['entities']['title'] == 'MARLEY'].iloc[0]
            print(f"\n📍 MARLEY:")
            print(f"   Tipo: {entity['type']}")
            print(f"   Descripción: {entity['description']}")
        
        elif query == 'relationship':
            rel = data['relationships'].iloc[0]
            print(f"\n🔗 RELACIÓN:")
            print(f"   {rel['source']} ↔ {rel['target']}")
            print(f"   Descripción: {rel['description']}")
        
        elif query == 'text':
            sample_text = data['text_units']['text'].iloc[0]
            print(f"\n📄 FRAGMENTO DE TEXTO:")
            print(f"   {sample_text[:300]}...")
        
        else:
            # Búsqueda simple
            found = False
            if 'entities' in data:
                for _, entity in data['entities'].iterrows():
                    if query in entity['title'].lower() or query in entity['description'].lower():
                        print(f"\n📍 Encontrado: {entity['title']}")
                        print(f"   {entity['description']}")
                        found = True
            
            if not found:
                print(f"\n❌ No se encontró información para '{query}'")
                print("   Prueba con: scrooge, marley, relationship, text")

if __name__ == "__main__":
    interactive_query()
