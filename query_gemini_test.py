#!/usr/bin/env python3
"""
Script de prueba para consultas GraphRAG con Gemini
"""

import pandas as pd
import asyncio
from pathlib import Path
from graphrag.language_model.providers.gemini.models import GeminiChatProvider
from graphrag.config.load_config import load_config

async def test_basic_gemini_query():
    """Prueba básica de consulta con Gemini"""
    
    # Cargar configuración
    root_dir = Path("/home/charizardbellako/Documentos/GraphRAG/LuminaMO_GraphRag/ragtest")
    config_path = root_dir / "settings_gemini.yaml"
    config = load_config(root_dir, config_path, {})
    
    # Crear instancia del modelo Gemini usando la configuración
    from graphrag.config.models.language_model_config import LanguageModelConfig
    
    model_config = LanguageModelConfig(
        api_key=config.models["default_chat_model"].api_key,
        model=config.models["default_chat_model"].model,
        type="gemini_chat",
        encoding_model="cl100k_base"
    )
    
    gemini_model = GeminiChatProvider(
        name="test_gemini",
        config=model_config
    )
    
    # Cargar datos disponibles
    output_dir = root_dir / "output"
    
    print("=== Cargando datos disponibles ===")
    
    # Cargar entidades
    try:
        entities = pd.read_parquet(output_dir / "entities.parquet")
        print(f"✅ Entidades cargadas: {len(entities)} registros")
        print("Entidades encontradas:")
        for _, entity in entities.head(5).iterrows():
            print(f"  - {entity['title']} ({entity['type']})")
    except FileNotFoundError:
        entities = None
        print("❌ No se encontraron entidades")
    
    # Cargar relaciones
    try:
        relationships = pd.read_parquet(output_dir / "relationships.parquet")
        print(f"✅ Relaciones cargadas: {len(relationships)} registros")
    except FileNotFoundError:
        relationships = None
        print("❌ No se encontraron relaciones")
    
    # Cargar unidades de texto
    try:
        text_units = pd.read_parquet(output_dir / "text_units.parquet")
        print(f"✅ Unidades de texto cargadas: {len(text_units)} registros")
    except FileNotFoundError:
        text_units = None
        print("❌ No se encontraron unidades de texto")
    
    print("\n=== Probando consulta con Gemini ===")
    
    # Crear contexto básico para la consulta
    context_parts = []
    
    if entities is not None:
        entities_text = "Entidades identificadas:\n"
        for _, entity in entities.iterrows():
            entities_text += f"- {entity['title']} ({entity['type']}): {entity.get('description', 'Sin descripción')}\n"
        context_parts.append(entities_text)
    
    if relationships is not None and len(relationships) > 0:
        relationships_text = "\nRelaciones identificadas:\n"
        for _, rel in relationships.head(5).iterrows():
            relationships_text += f"- {rel['source']} → {rel['target']}: {rel.get('description', 'Sin descripción')}\n"
        context_parts.append(relationships_text)
    
    if text_units is not None:
        sample_text = text_units['text'].iloc[0] if len(text_units) > 0 else ""
        if sample_text:
            context_parts.append(f"\nTexto de muestra:\n{sample_text[:500]}...")
    
    context = "\n".join(context_parts)
    
    # Crear prompt para Gemini
    query = "¿Cuáles son los temas principales mencionados en el texto?"
    prompt = f"""
Basándote en la siguiente información extraída de documentos:

{context}

Pregunta: {query}

Por favor, proporciona un resumen de los temas principales identificados en el contenido.
"""

    try:
        print("Enviando consulta a Gemini...")
        response = await gemini_model.achat(prompt)
        
        print("\n=== Respuesta de Gemini ===")
        print(response.content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error al consultar Gemini: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando prueba de consulta GraphRAG con Gemini")
    
    success = asyncio.run(test_basic_gemini_query())
    
    if success:
        print("\n✅ ¡Prueba completada exitosamente!")
        print("La integración de Gemini con GraphRAG está funcionando.")
    else:
        print("\n❌ La prueba falló.")
        print("Revisa la configuración de Gemini y tu clave de API.")

if __name__ == "__main__":
    main()
