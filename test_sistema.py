#!/usr/bin/env python3
"""
Script de prueba para verificar que la integración de Gemini funciona correctamente
"""

import os
import sys
from pathlib import Path

def test_gemini_connection():
    """Probar conexión básica con Gemini"""
    print("🔍 Probando conexión con Gemini...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY no está configurado")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prueba simple
        response = model.generate_content("Responde solo: OK")
        if response.text:
            print("✅ Conexión con Gemini exitosa")
            return True
        else:
            print("❌ Gemini no respondió correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con Gemini: {e}")
        if "429" in str(e):
            print("⚠️  Cuota de API agotada - espera 24 horas o cambia a API de pago")
        return False

def test_graphrag_import():
    """Probar que GraphRAG se puede importar"""
    print("🔍 Probando importación de GraphRAG...")
    
    try:
        import graphrag
        from graphrag.config.load_config import load_config
        from graphrag.language_model.providers.gemini.models import GeminiChatProvider
        print("✅ GraphRAG importado correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando GraphRAG: {e}")
        print("Ejecuta: pip install -e .")
        return False

def test_project_structure():
    """Verificar estructura del proyecto"""
    print("🔍 Verificando estructura del proyecto...")
    
    # Verificar archivos principales
    required_files = [
        "ragtest/settings_gemini.yaml",
        "ragtest/input",
        "generate_community_reports.py", 
        "resume_indexing.py",
        "local_query_test.py"
    ]
    
    all_good = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} no encontrado")
            all_good = False
    
    return all_good

def run_quick_test():
    """Ejecutar una prueba rápida del sistema completo"""
    print("🔍 Ejecutando prueba rápida del sistema...")
    
    # Verificar datos existentes
    output_dir = Path("ragtest/output")
    if not output_dir.exists():
        print("⚠️  No hay datos procesados aún")
        print("Ejecuta: python resume_indexing.py ragtest settings_gemini.yaml")
        return False
    
    # Verificar archivos de datos
    data_files = ["entities.parquet", "relationships.parquet", "text_units.parquet"]
    existing_files = []
    
    for file in data_files:
        file_path = output_dir / file
        if file_path.exists():
            existing_files.append(file)
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
    
    if len(existing_files) >= 3:
        print("✅ Datos suficientes para consultas locales")
        
        # Probar consulta local
        try:
            import subprocess
            result = subprocess.run([
                "python", "local_query_test.py"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Consultas locales funcionando")
                return True
            else:
                print(f"⚠️  Error en consultas: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"⚠️  No se pudo probar consultas: {e}")
            return False
    else:
        print("❌ Datos insuficientes para consultas")
        return False

def main():
    print("🚀 Test de Verificación - GraphRAG + Gemini")
    print("=" * 50)
    
    tests = [
        ("Importación de GraphRAG", test_graphrag_import),
        ("Conexión con Gemini", test_gemini_connection), 
        ("Estructura del proyecto", test_project_structure),
        ("Prueba del sistema", run_quick_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas exitosas")
    
    if passed == len(results):
        print("\n🎉 ¡Todo funciona correctamente!")
        print("Puedes usar el sistema normalmente.")
    elif passed >= len(results) - 1:
        print("\n⚠️  Sistema mayormente funcional")
        print("Hay problemas menores que no impiden el uso básico.")
    else:
        print("\n❌ Sistema tiene problemas significativos")
        print("Revisa los errores arriba y corrígelos.")
    
    # Sugerencias finales
    print("\n💡 PRÓXIMOS PASOS:")
    if passed >= 2:  # Al menos GraphRAG y estructura funcionan
        print("1. Si no hay datos: python resume_indexing.py ragtest")
        print("2. Para consultas: python local_query_test.py")
        print("3. Interactive: python interactive_query.py")
    else:
        print("1. Instalar dependencias: pip install -e .")
        print("2. Configurar GEMINI_API_KEY")
        print("3. Volver a ejecutar este test")

if __name__ == "__main__":
    main()
