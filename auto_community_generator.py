#!/usr/bin/env python3
"""
Auto-generador de community_reports integrado en GraphRAG
Se ejecuta automáticamente cuando faltan community_reports
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CommunityReportsAutoGenerator:
    """Generador automático de community_reports para GraphRAG"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        
    def check_and_generate_if_missing(self) -> bool:
        """Verificar si community_reports existe, si no, generarlo automáticamente"""
        community_file = self.output_dir / "community_reports.parquet"
        
        if community_file.exists():
            try:
                # Verificar que el archivo es válido
                df = pd.read_parquet(community_file)
                if len(df) > 0:
                    logger.info(f"✅ community_reports.parquet existe con {len(df)} registros")
                    return True
                else:
                    logger.warning("community_reports.parquet está vacío, regenerando...")
            except Exception as e:
                logger.warning(f"community_reports.parquet corrupto: {e}, regenerando...")
        
        # Si llegamos aquí, necesitamos generar el archivo
        logger.info("🔄 Generando community_reports.parquet automáticamente...")
        return self.generate_community_reports()
    
    def generate_community_reports(self) -> bool:
        """Generar community_reports basado en datos existentes"""
        try:
            # Cargar archivos necesarios
            entities_file = self.output_dir / "entities.parquet"
            relationships_file = self.output_dir / "relationships.parquet"
            text_units_file = self.output_dir / "text_units.parquet"
            
            if not entities_file.exists():
                logger.error("❌ No se puede generar community_reports: entities.parquet no existe")
                return False
                
            entities = pd.read_parquet(entities_file)
            logger.info(f"📊 Cargadas {len(entities)} entidades")
            
            # Cargar relaciones si existen
            relationships = None
            if relationships_file.exists():
                relationships = pd.read_parquet(relationships_file)
                logger.info(f"🔗 Cargadas {len(relationships)} relaciones")
            
            # Generar comunidades inteligentes
            communities = self._create_intelligent_communities(entities, relationships)
            
            # Guardar community_reports
            community_df = pd.DataFrame(communities)
            community_file = self.output_dir / "community_reports.parquet"
            community_df.to_parquet(community_file)
            
            logger.info(f"✅ Generado community_reports.parquet con {len(communities)} comunidades")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generando community_reports: {e}")
            return False
    
    def _create_intelligent_communities(self, entities: pd.DataFrame, relationships: Optional[pd.DataFrame] = None) -> list:
        """Crear comunidades inteligentes basadas en entidades y relaciones"""
        communities = []
        
        # Estrategia 1: Comunidades por tipo de entidad
        if 'type' in entities.columns:
            entity_types = entities['type'].unique()
            for i, entity_type in enumerate(entity_types):
                type_entities = entities[entities['type'] == entity_type]
                community = self._create_type_community(i, entity_type, type_entities, relationships)
                communities.append(community)
        
        # Estrategia 2: Si hay pocas comunidades por tipo, crear comunidad general
        if len(communities) <= 1:
            general_community = self._create_general_community(len(communities), entities, relationships)
            communities.append(general_community)
        
        # Estrategia 3: Comunidades por conectividad (si hay relaciones)
        if relationships is not None and len(relationships) > 0:
            connected_communities = self._create_connected_communities(len(communities), entities, relationships)
            communities.extend(connected_communities)
        
        # Asegurar que tenemos al menos una comunidad
        if not communities:
            communities.append(self._create_fallback_community(entities))
        
        return communities
    
    def _create_type_community(self, index: int, entity_type: str, type_entities: pd.DataFrame, relationships: Optional[pd.DataFrame]) -> dict:
        """Crear comunidad basada en tipo de entidad"""
        
        # Obtener muestra de entidades
        entity_sample = type_entities['title'].head(5).tolist() if 'title' in type_entities.columns else []
        entity_names = ", ".join(entity_sample[:3])
        if len(type_entities) > 3:
            entity_names += f" y {len(type_entities) - 3} más"
        
        # Calcular estadísticas
        total_entities = len(type_entities)
        avg_frequency = type_entities['frequency'].mean() if 'frequency' in type_entities.columns else 1.0
        
        # Buscar relaciones relacionadas
        related_relationships = []
        if relationships is not None and 'title' in type_entities.columns:
            entity_titles = set(type_entities['title'].tolist())
            if 'source' in relationships.columns and 'target' in relationships.columns:
                related_relationships = relationships[
                    relationships['source'].isin(entity_titles) | 
                    relationships['target'].isin(entity_titles)
                ]
        
        # Crear resumen inteligente
        summary = f"Comunidad de {total_entities} entidades de tipo {entity_type}"
        if entity_names:
            summary += f", incluyendo: {entity_names}"
        if len(related_relationships) > 0:
            summary += f". Esta comunidad tiene {len(related_relationships)} relaciones internas"
        
        # Crear contenido detallado
        full_content = f"""Esta comunidad representa un grupo cohesivo de {total_entities} entidades clasificadas como {entity_type}.

Entidades principales: {entity_names}

Características de la comunidad:
- Número total de entidades: {total_entities}
- Frecuencia promedio: {avg_frequency:.2f}
- Relaciones asociadas: {len(related_relationships)}

"""
        
        if len(related_relationships) > 0:
            full_content += "Relaciones principales:\n"
            for _, rel in related_relationships.head(3).iterrows():
                if 'description' in rel:
                    full_content += f"- {rel.get('source', '')} ↔ {rel.get('target', '')}: {rel.get('description', '')}\n"
        
        # Crear findings
        findings = [
            f"Contiene {total_entities} entidades de tipo {entity_type}",
            f"Frecuencia promedio de entidades: {avg_frequency:.2f}"
        ]
        
        if len(related_relationships) > 0:
            findings.append(f"Involucrada en {len(related_relationships)} relaciones")
        
        if entity_sample:
            findings.append(f"Entidades destacadas: {', '.join(entity_sample[:3])}")
        
        return {
            'id': f'community_{index}',
            'human_readable_id': index,
            'level': 0,
            'title': f'Comunidad {entity_type}',
            'summary': summary,
            'full_content': full_content,
            'rank': float(total_entities * avg_frequency),
            'rank_explanation': f'Ranking basado en {total_entities} entidades con frecuencia promedio {avg_frequency:.2f}',
            'findings': findings,
            'full_content_json': json.dumps({
                "community_type": "entity_type_based",
                "entity_type": entity_type,
                "total_entities": total_entities,
                "average_frequency": avg_frequency,
                "related_relationships": len(related_relationships),
                "main_entities": entity_sample[:5]
            })
        }
    
    def _create_general_community(self, index: int, entities: pd.DataFrame, relationships: Optional[pd.DataFrame]) -> dict:
        """Crear comunidad general que incluye todas las entidades"""
        
        total_entities = len(entities)
        entity_types = entities['type'].unique().tolist() if 'type' in entities.columns else ['Unknown']
        
        summary = f"Comunidad general que abarca {total_entities} entidades de {len(entity_types)} tipos diferentes"
        
        full_content = f"""Esta es una comunidad general que incluye todas las entidades del documento, 
proporcionando una vista holística del contenido.

Estadísticas generales:
- Total de entidades: {total_entities}
- Tipos de entidades: {', '.join(entity_types)}
"""
        
        if relationships is not None:
            total_relationships = len(relationships)
            full_content += f"- Total de relaciones: {total_relationships}\n"
        
        findings = [
            f"Comunidad comprehensiva con {total_entities} entidades",
            f"Abarca {len(entity_types)} tipos de entidades diferentes"
        ]
        
        if relationships is not None:
            findings.append(f"Conectada por {len(relationships)} relaciones")
        
        return {
            'id': f'community_{index}',
            'human_readable_id': index,
            'level': 1,  # Nivel superior
            'title': 'Comunidad General',
            'summary': summary,
            'full_content': full_content,
            'rank': float(total_entities),
            'rank_explanation': f'Comunidad de nivel superior con {total_entities} entidades',
            'findings': findings,
            'full_content_json': json.dumps({
                "community_type": "general",
                "total_entities": total_entities,
                "entity_types": entity_types,
                "total_relationships": len(relationships) if relationships is not None else 0
            })
        }
    
    def _create_connected_communities(self, start_index: int, entities: pd.DataFrame, relationships: pd.DataFrame) -> list:
        """Crear comunidades basadas en conectividad de relaciones"""
        # Esta es una versión simplificada - en producción se podría usar algoritmos de detección de comunidades
        communities = []
        
        if 'source' not in relationships.columns or 'target' not in relationships.columns:
            return communities
            
        # Encontrar entidades altamente conectadas
        all_nodes = set(relationships['source'].tolist() + relationships['target'].tolist())
        
        # Contar conexiones por entidad
        connection_counts = {}
        for _, rel in relationships.iterrows():
            source = rel['source']
            target = rel['target']
            connection_counts[source] = connection_counts.get(source, 0) + 1
            connection_counts[target] = connection_counts.get(target, 0) + 1
        
        # Crear comunidad de entidades altamente conectadas (top 20%)
        if connection_counts:
            sorted_entities = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)
            top_20_percent = max(1, len(sorted_entities) // 5)
            highly_connected = [entity for entity, count in sorted_entities[:top_20_percent]]
            
            if len(highly_connected) >= 2:
                community = self._create_connectivity_community(
                    start_index, 
                    highly_connected, 
                    relationships, 
                    "Alta Conectividad"
                )
                communities.append(community)
        
        return communities
    
    def _create_connectivity_community(self, index: int, entity_list: list, relationships: pd.DataFrame, community_type: str) -> dict:
        """Crear comunidad basada en conectividad"""
        
        # Encontrar relaciones entre estas entidades
        entity_set = set(entity_list)
        internal_relationships = relationships[
            relationships['source'].isin(entity_set) & 
            relationships['target'].isin(entity_set)
        ]
        
        summary = f"Comunidad de {community_type} con {len(entity_list)} entidades altamente interconectadas"
        
        full_content = f"""Esta comunidad se basa en la alta conectividad entre sus entidades.

Entidades principales: {', '.join(entity_list[:5])}
Relaciones internas: {len(internal_relationships)}

Esta comunidad muestra un alto grado de interconexión, sugiriendo temas o conceptos relacionados.
"""
        
        findings = [
            f"Comunidad de {len(entity_list)} entidades interconectadas",
            f"Contiene {len(internal_relationships)} relaciones internas",
            f"Tipo: {community_type}"
        ]
        
        return {
            'id': f'community_{index}',
            'human_readable_id': index,
            'level': 0,
            'title': f'Comunidad de {community_type}',
            'summary': summary,
            'full_content': full_content,
            'rank': float(len(internal_relationships)),
            'rank_explanation': f'Ranking basado en {len(internal_relationships)} conexiones internas',
            'findings': findings,
            'full_content_json': json.dumps({
                "community_type": "connectivity_based",
                "entities": entity_list[:10],  # Limitar para no sobrecargar JSON
                "internal_relationships": len(internal_relationships),
                "connectivity_type": community_type
            })
        }
    
    def _create_fallback_community(self, entities: pd.DataFrame) -> dict:
        """Crear comunidad de respaldo cuando todo lo demás falla"""
        
        return {
            'id': 'community_0',
            'human_readable_id': 0,
            'level': 0,
            'title': 'Comunidad Principal',
            'summary': f'Comunidad principal que contiene todas las {len(entities)} entidades del documento',
            'full_content': f'Esta comunidad fue generada automáticamente para incluir todas las entidades cuando no se pudieron crear comunidades más específicas.',
            'rank': float(len(entities)),
            'rank_explanation': f'Comunidad única con {len(entities)} entidades',
            'findings': [f'Contiene {len(entities)} entidades totales'],
            'full_content_json': json.dumps({
                "community_type": "fallback",
                "total_entities": len(entities)
            })
        }

# Función de utilidad para uso externo
def ensure_community_reports(output_dir: str) -> bool:
    """Asegurar que community_reports.parquet existe, generándolo si es necesario"""
    generator = CommunityReportsAutoGenerator(output_dir)
    return generator.check_and_generate_if_missing()

if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./output"
    
    generator = CommunityReportsAutoGenerator(output_dir)
    success = generator.check_and_generate_if_missing()
    
    if success:
        print("✅ community_reports.parquet está disponible")
    else:
        print("❌ No se pudo generar community_reports.parquet")
