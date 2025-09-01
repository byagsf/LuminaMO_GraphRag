#!/usr/bin/env python3
"""
Script para verificar qué modelos de Gemini están disponibles con tu API key.
"""

import google.generativeai as genai

# Configurar la API key
genai.configure(api_key="AIzaSyD2emQC2huUXTcykYTM2uSgVxZPuAH_dqc")

print("🔍 Verificando modelos disponibles de Gemini...")
print("=" * 60)

try:
    # Listar todos los modelos disponibles
    models = genai.list_models()
    
    chat_models = []
    embedding_models = []
    
    for model in models:
        print(f"📋 Modelo: {model.name}")
        print(f"   Métodos soportados: {model.supported_generation_methods}")
        print(f"   Descripción: {model.display_name}")
        print()
        
        # Clasificar modelos
        if 'generateContent' in model.supported_generation_methods:
            chat_models.append(model.name)
        if 'embedContent' in model.supported_generation_methods:
            embedding_models.append(model.name)
    
    print("=" * 60)
    print("📝 RESUMEN:")
    print(f"✅ Modelos de Chat disponibles ({len(chat_models)}):")
    for model in chat_models:
        print(f"   - {model}")
    
    print(f"\n🧠 Modelos de Embedding disponibles ({len(embedding_models)}):")
    for model in embedding_models:
        print(f"   - {model}")
        
    print("\n💡 RECOMENDACIONES:")
    print("Para Chat: Usa uno de los modelos con 'generateContent'")
    print("Para Embeddings: Usa uno de los modelos con 'embedContent'")

except Exception as e:
    print(f"❌ Error al obtener modelos: {e}")
    print("\n🔧 Posibles soluciones:")
    print("1. Verifica que tu API key sea válida")
    print("2. Asegúrate de tener permisos para la API de Gemini")
    print("3. Revisa tu conexión a internet")
