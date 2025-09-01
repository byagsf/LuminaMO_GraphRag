#!/usr/bin/env python3
"""
Script para realizar consultas locales con datos GraphRAG sin usar API
"""

import pandas as pd
from pathlib import Path
import json

def load_graphrag_data():
    """Cargar todos los datos GraphRAG disponibles"""
    root_dir = Path("/home/charizardbellako/Documentos/GraphRAG/LuminaMO_GraphRag/ragtest")
    output_dir = root_dir / "output"
    
    data = {}
    
    # Cargar entidades
    entities_path = output_dir / "entities.parquet"
    if entities_path.exists():
        data['entities'] = pd.read_parquet(entities_path)
        print(f"✅ Entidades cargadas: {len(data['entities'])} registros")
    
    # Cargar relaciones
    relationships_path = output_dir / "relationships.parquet"
    if relationships_path.exists():
        data['relationships'] = pd.read_parquet(relationships_path)
        print(f"✅ Relaciones cargadas: {len(data['relationships'])} registros")
    
    # Cargar unidades de texto
    text_units_path = output_dir / "text_units.parquet"
    if text_units_path.exists():
        data['text_units'] = pd.read_parquet(text_units_path)
        print(f"✅ Unidades de texto cargadas: {len(data['text_units'])} registros")
    
    return data

def search_entities(data, query):
    """Buscar entidades que contengan el término de búsqueda"""
    if 'entities' not in data:
        return pd.DataFrame()
    
    entities = data['entities']
    
    # Buscar en título y descripción
    mask = (
        entities['title'].str.contains(query, case=False, na=False) |
        entities['description'].str.contains(query, case=False, na=False)
    )
    
    return entities[mask]

def get_entity_relationships(data, entity_name):
    """Obtener todas las relaciones de una entidad específica"""
    if 'relationships' not in data:
        return pd.DataFrame()
    
    relationships = data['relationships']
    
    # Buscar relaciones donde la entidad sea source o target
    mask = (
        relationships['source'].str.contains(entity_name, case=False, na=False) |
        relationships['target'].str.contains(entity_name, case=False, na=False)
    )
    
    return relationships[mask]

def get_related_text(data, entity_id):
    """Obtener texto relacionado con una entidad"""
    if 'text_units' not in data or 'entities' not in data:
        return []
    
    entities = data['entities']
    text_units = data['text_units']
    
    # Encontrar la entidad
    entity_row = entities[entities['id'] == entity_id]
    if entity_row.empty:
        return []
    
    # Obtener IDs de unidades de texto
    text_unit_ids = entity_row['text_unit_ids'].iloc[0]
    if isinstance(text_unit_ids, str):
        try:
            text_unit_ids = json.loads(text_unit_ids)
        except:
            text_unit_ids = []
    
    # Obtener textos
    texts = []
    for unit_id in text_unit_ids:
        unit_row = text_units[text_units['id'] == unit_id]
        if not unit_row.empty:
            texts.append(unit_row['text'].iloc[0])
    
    return texts

def local_query(data, question):
    """Realizar una consulta local basada en los datos disponibles"""
    print(f"\n🔍 Consultando: '{question}'")
    print("=" * 50)
    
    # Extraer palabras clave de la pregunta
    keywords = [word.lower() for word in question.split() if len(word) > 2]
    
    results = {
        'entities': pd.DataFrame(),
        'relationships': pd.DataFrame(),
        'relevant_texts': []
    }
    
    # Buscar entidades relevantes
    for keyword in keywords:
        matching_entities = search_entities(data, keyword)
        if not matching_entities.empty:
            if results['entities'].empty:
                results['entities'] = matching_entities.copy()
            else:
                results['entities'] = pd.concat([results['entities'], matching_entities]).drop_duplicates(subset=['id'])
    
    # Si encontramos entidades, buscar sus relaciones
    if not results['entities'].empty:
        for _, entity in results['entities'].iterrows():
            entity_rels = get_entity_relationships(data, entity['title'])
            if not entity_rels.empty:
                if results['relationships'].empty:
                    results['relationships'] = entity_rels.copy()
                else:
                    results['relationships'] = pd.concat([results['relationships'], entity_rels]).drop_duplicates(subset=['id'])
            
            # Obtener texto relacionado
            related_texts = get_related_text(data, entity['id'])
            results['relevant_texts'].extend(related_texts)
    
    return results

def display_results(results):
    """Mostrar los resultados de la consulta"""
    
    # Mostrar entidades encontradas
    if not results['entities'].empty:
        print("\n📍 ENTIDADES ENCONTRADAS:")
        for _, entity in results['entities'].iterrows():
            print(f"• {entity['title']} ({entity['type']})")
            print(f"  {entity['description']}")
            print()
    
    # Mostrar relaciones encontradas
    if not results['relationships'].empty:
        print("🔗 RELACIONES ENCONTRADAS:")
        for _, rel in results['relationships'].iterrows():
            print(f"• {rel['source']} ↔ {rel['target']}")
            print(f"  {rel['description']}")
            print()
    
    # Mostrar texto relevante (limitado)
    if results['relevant_texts']:
        print("📄 TEXTO RELEVANTE:")
        for i, text in enumerate(results['relevant_texts'][:2]):  # Solo los primeros 2
            print(f"Fragmento {i+1}:")
            print(f"{text[:300]}...")
            print()
    
    # Resumen
    print("📊 RESUMEN:")
    print(f"• Entidades encontradas: {len(results['entities'])}")
    print(f"• Relaciones encontradas: {len(results['relationships'])}")
    print(f"• Fragmentos de texto: {len(results['relevant_texts'])}")

def main():
    """Función principal"""
    print("🚀 Iniciando consultas locales GraphRAG")
    print("=" * 50)
    
    # Cargar datos
    data = load_graphrag_data()
    
    if not data:
        print("❌ No se pudieron cargar los datos")
        return
    
    # Consultas de ejemplo
    example_queries = [
        "Who is Scrooge?",
        "What is the relationship between Scrooge and Marley?",
        "Tell me about the main characters",
        "What happens in the story?"
    ]
    
    print(f"\n🎯 Realizando {len(example_queries)} consultas de ejemplo:")
    
    for query in example_queries:
        results = local_query(data, query)
        display_results(results)
        print("\n" + "="*50)
    
    print("\n💡 NOTA:")
    print("Estas consultas usan solo los datos locales generados por GraphRAG.")
    print("Para obtener respuestas más elaboradas, necesitarías usar la API de Gemini")
    print("pero los límites de cuota actual (50/día) lo impiden.")
    print("\nAlternativas:")
    print("1. Esperar hasta mañana para reset de cuota")
    print("2. Usar OpenAI API (con créditos)")
    print("3. Configurar un modelo local (Ollama, etc.)")

if __name__ == "__main__":
    main()
