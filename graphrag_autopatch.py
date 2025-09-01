#!/usr/bin/env python3
"""
Parche automático para GraphRAG que asegura community_reports siempre disponibles
"""

import os
import sys
from pathlib import Path
import logging

# Agregar el directorio actual al path para importar auto_community_generator
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from auto_community_generator import ensure_community_reports

logger = logging.getLogger(__name__)

def patch_graphrag_query():
    """Parchar las consultas de GraphRAG para auto-generar community_reports"""
    
    try:
        # Importar módulos de GraphRAG
        from graphrag.cli import query
        from graphrag.query.factories import get_global_search_engine, get_local_search_engine
        
        # Guardar funciones originales
        original_get_global_search_engine = get_global_search_engine
        original_get_local_search_engine = get_local_search_engine
        
        def patched_get_global_search_engine(*args, **kwargs):
            """Versión parcheada que asegura community_reports antes de ejecutar"""
            # Detectar directorio de output desde argumentos
            config = args[0] if args else None
            if config and hasattr(config, 'storage') and hasattr(config.storage, 'base_dir'):
                output_dir = config.storage.base_dir
                logger.info(f"🔍 Verificando community_reports en: {output_dir}")
                ensure_community_reports(output_dir)
            
            return original_get_global_search_engine(*args, **kwargs)
        
        def patched_get_local_search_engine(*args, **kwargs):
            """Versión parcheada que asegura community_reports antes de ejecutar"""
            # Detectar directorio de output desde argumentos
            config = args[0] if args else None
            if config and hasattr(config, 'storage') and hasattr(config.storage, 'base_dir'):
                output_dir = config.storage.base_dir
                logger.info(f"🔍 Verificando community_reports en: {output_dir}")
                ensure_community_reports(output_dir)
            
            return original_get_local_search_engine(*args, **kwargs)
        
        # Aplicar parches
        query.get_global_search_engine = patched_get_global_search_engine
        query.get_local_search_engine = patched_get_local_search_engine
        
        # También parchar en factories directamente
        import graphrag.query.factories as factories
        factories.get_global_search_engine = patched_get_global_search_engine
        factories.get_local_search_engine = patched_get_local_search_engine
        
        logger.info("✅ GraphRAG parcheado para auto-generar community_reports")
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️  No se pudo parchar GraphRAG: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error aplicando parche: {e}")
        return False

def patch_graphrag_indexing():
    """Parchar el indexing para generar community_reports al final si falla"""
    
    try:
        from graphrag.cli import index
        
        # Guardar función original
        original_index_cli = index.index_cli
        
        def patched_index_cli(*args, **kwargs):
            """Versión parcheada que genera community_reports al final si falta"""
            try:
                # Ejecutar indexing original
                result = original_index_cli(*args, **kwargs)
                
                # Intentar detectar directorio de output
                root_dir = kwargs.get('root', '.')
                output_dir = Path(root_dir) / "output"
                
                if output_dir.exists():
                    logger.info("🔍 Verificando community_reports post-indexing...")
                    ensure_community_reports(str(output_dir))
                
                return result
                
            except Exception as e:
                logger.error(f"Error en indexing: {e}")
                
                # Intentar generar community_reports incluso si falla
                root_dir = kwargs.get('root', '.')
                output_dir = Path(root_dir) / "output"
                
                if output_dir.exists():
                    logger.info("🛠️  Intentando generar community_reports después de fallo...")
                    ensure_community_reports(str(output_dir))
                
                raise
        
        # Aplicar parche
        index.index_cli = patched_index_cli
        
        logger.info("✅ GraphRAG indexing parcheado para auto-generar community_reports")
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️  No se pudo parchar indexing: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error aplicando parche de indexing: {e}")
        return False

def apply_all_patches():
    """Aplicar todos los parches automáticos"""
    logger.info("🔧 Aplicando parches automáticos para community_reports...")
    
    query_patched = patch_graphrag_query()
    index_patched = patch_graphrag_indexing()
    
    if query_patched or index_patched:
        logger.info("✅ Parches aplicados exitosamente")
        return True
    else:
        logger.warning("⚠️  No se pudieron aplicar parches")
        return False

# Auto-aplicar parches al importar este módulo
if __name__ != "__main__":
    apply_all_patches()

if __name__ == "__main__":
    # Prueba manual del sistema de parches
    print("🧪 Probando sistema de parches...")
    
    success = apply_all_patches()
    
    if success:
        print("✅ Sistema de parches funcionando")
        
        # Probar con directorio de ejemplo
        test_dir = "./ragtest/output"
        if Path(test_dir).exists():
            print(f"🔍 Probando auto-generación en {test_dir}")
            result = ensure_community_reports(test_dir)
            if result:
                print("✅ Auto-generación funcionando")
            else:
                print("❌ Error en auto-generación")
    else:
        print("❌ Error en sistema de parches")
