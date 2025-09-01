#!/usr/bin/env python3
"""
Script de prueba para el provider de Gemini en GraphRAG.
Este script verifica que la integración con Gemini funcione correctamente.
"""

import asyncio
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importar GraphRAG
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from graphrag.config.enums import ModelType
from graphrag.config.models.language_model_config import LanguageModelConfig
from graphrag.language_model.providers.gemini.models import (
    GeminiChatProvider,
    GeminiEmbeddingProvider,
)
from graphrag.language_model.factory import ModelFactory


async def test_gemini_chat():
    """Prueba el modelo de chat de Gemini."""
    print("🧪 Probando Gemini Chat...")
    
    try:
        # Configuración del modelo
        config = LanguageModelConfig(
            type="gemini_chat",
            api_key="AIzaSyD2emQC2huUXTcykYTM2uSgVxZPuAH_dqc",
            model="models/gemini-1.5-flash",  # Modelo estable y disponible
            temperature=0.7,
            max_tokens=1000,
            encoding_model="cl100k_base",  # Evitar problemas con tiktoken
        )
        
        # Crear instancia directa
        chat_provider = GeminiChatProvider(
            name="test_gemini_chat",
            config=config,
        )
        
        # Prueba de chat simple
        prompt = "Hola, ¿puedes explicarme brevemente qué es GraphRAG?"
        print(f"📝 Prompt: {prompt}")
        
        response = await chat_provider.achat(prompt)
        print(f"✅ Respuesta: {response.output.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en chat de Gemini: {e}")
        return False


async def test_gemini_embedding():
    """Prueba el modelo de embeddings de Gemini."""
    print("\n🧪 Probando Gemini Embeddings...")
    
    try:
        # Configuración del modelo
        config = LanguageModelConfig(
            type="gemini_embedding",
            api_key="AIzaSyD2emQC2huUXTcykYTM2uSgVxZPuAH_dqc",
            model="models/text-embedding-004",
            encoding_model="cl100k_base",  # Evitar problemas con tiktoken
        )
        
        # Crear instancia directa
        embedding_provider = GeminiEmbeddingProvider(
            name="test_gemini_embedding",
            config=config,
        )
        
        # Prueba de embedding simple
        text = "GraphRAG es una técnica que combina grafos de conocimiento con generación aumentada por recuperación."
        print(f"📝 Texto: {text}")
        
        embedding = await embedding_provider.aembed(text)
        print(f"✅ Embedding generado: dimensiones = {len(embedding)}")
        print(f"✅ Primeros 5 valores: {embedding[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en embeddings de Gemini: {e}")
        return False


def test_model_factory():
    """Prueba que la factory puede crear modelos de Gemini."""
    print("\n🧪 Probando Model Factory...")
    
    try:
        # Verificar que los modelos están registrados
        chat_models = ModelFactory.get_chat_models()
        embedding_models = ModelFactory.get_embedding_models()
        
        print(f"✅ Modelos de chat disponibles: {chat_models}")
        print(f"✅ Modelos de embedding disponibles: {embedding_models}")
        
        # Verificar que Gemini está incluido
        assert ModelType.GeminiChat.value in chat_models
        assert ModelType.GeminiEmbedding.value in embedding_models
        
        print("✅ Gemini está correctamente registrado en la factory")
        return True
        
    except Exception as e:
        print(f"❌ Error en factory: {e}")
        return False


async def test_full_integration():
    """Prueba la integración completa usando la factory."""
    print("\n🧪 Probando integración completa...")
    
    try:
        # Crear modelo de chat usando la factory
        chat_model = ModelFactory.create_chat_model(
            ModelType.GeminiChat.value,
            name="test_chat",
            config=LanguageModelConfig(
                type="gemini_chat",
                api_key="AIzaSyD2emQC2huUXTcykYTM2uSgVxZPuAH_dqc",
                model="models/gemini-1.5-flash",  # Modelo estable y disponible
                encoding_model="cl100k_base",
            ),
        )
        
        # Crear modelo de embedding usando la factory
        embedding_model = ModelFactory.create_embedding_model(
            ModelType.GeminiEmbedding.value,
            name="test_embedding",
            config=LanguageModelConfig(
                type="gemini_embedding",
                api_key="AIzaSyD2emQC2huUXTcykYTM2uSgVxZPuAH_dqc",
                model="models/text-embedding-004",
                encoding_model="cl100k_base",
            ),
        )
        
        # Prueba rápida
        response = await chat_model.achat("¿Qué es IA?")
        embedding = await embedding_model.aembed("Inteligencia Artificial")
        
        print("✅ Integración completa funcionando correctamente")
        print(f"✅ Chat respuesta: {response.output.content[:100]}...")
        print(f"✅ Embedding dimensiones: {len(embedding)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración completa: {e}")
        return False


async def main():
    """Función principal que ejecuta todas las pruebas."""
    print("🚀 Iniciando pruebas del provider de Gemini para GraphRAG\n")
    
    results = []
    
    # Ejecutar todas las pruebas
    results.append(test_model_factory())
    results.append(await test_gemini_chat())
    results.append(await test_gemini_embedding())
    results.append(await test_full_integration())
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Pruebas exitosas: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! Gemini está correctamente integrado.")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores anteriores.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
