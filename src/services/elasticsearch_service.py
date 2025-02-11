from elasticsearch import Elasticsearch
from typing import Dict, List
import os
from datetime import datetime
import logging
from elasticsearch.exceptions import ConnectionError

logger = logging.getLogger(__name__)

class ElasticsearchService:
    def __init__(self):
        elasticsearch_url = os.getenv('ELASTICSEARCH_URL')
        if not elasticsearch_url:
            raise ValueError("ELASTICSEARCH_URL n'est pas définie dans les variables d'environnement. Format attendu: http://localhost:9200")
        
        try:
            self.es = Elasticsearch(elasticsearch_url)
            # Vérifier la connexion
            if not self.es.ping():
                raise ConnectionError("Impossible de se connecter à Elasticsearch")
        except Exception as e:
            logger.error(f"Erreur de connexion à Elasticsearch: {str(e)}")
            raise ConnectionError(f"Erreur de connexion à Elasticsearch: {str(e)}")
            
        self.index_name = 'youtube_content'
        self._create_index_if_not_exists()

    def _create_index_if_not_exists(self):
        """Crée l'index avec le mapping approprié s'il n'existe pas."""
        try:
            if not self.es.indices.exists(index=self.index_name):
                mapping = {
                    "mappings": {
                        "properties": {
                            "channel_id": {"type": "keyword"},
                            "video_id": {"type": "keyword"},
                            "title": {
                                "type": "text",
                                "analyzer": "french",
                                "fields": {
                                    "keyword": {"type": "keyword"}
                                }
                            },
                            "description": {
                                "type": "text",
                                "analyzer": "french"
                            },
                            "published_at": {"type": "date"},
                            "view_count": {"type": "long"},
                            "like_count": {"type": "long"},
                            "comment_count": {"type": "long"},
                            "engagement_rate": {"type": "float"},
                            "keywords": {"type": "keyword"},
                            "topics": {"type": "keyword"},
                            "content_gaps": {"type": "keyword"},
                            "ai_suggestions": {
                                "type": "nested",
                                "properties": {
                                    "topic": {"type": "keyword"},
                                    "confidence": {"type": "float"},
                                    "potential_views": {"type": "long"}
                                }
                            }
                        }
                    }
                }
                self.es.indices.create(index=self.index_name, body=mapping)
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'index: {str(e)}")
            raise

    def index_video(self, video_data: Dict):
        """Indexe une vidéo dans Elasticsearch."""
        try:
            # Vérifier et nettoyer les données
            if 'id' in video_data and 'video_id' not in video_data:
                video_data['video_id'] = video_data['id']
            
            if 'video_id' not in video_data:
                raise ValueError("L'ID de la vidéo est manquant")

            # S'assurer que les champs numériques sont des nombres
            for field in ['view_count', 'like_count', 'comment_count']:
                if field in video_data and not isinstance(video_data[field], (int, float)):
                    video_data[field] = int(video_data[field])

            # Formater la date si présente
            if 'published_at' in video_data:
                try:
                    video_data['published_at'] = datetime.fromisoformat(
                        video_data['published_at'].replace('Z', '+00:00')
                    ).isoformat()
                except Exception as e:
                    logger.warning(f"Erreur de conversion de la date: {e}")

            self.es.index(
                index=self.index_name,
                id=video_data['video_id'],
                document=video_data
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation: {e}")
            raise

    def find_content_gaps(self, channel_id: str) -> List[Dict]:
        """Trouve les opportunités de contenu basées sur les données existantes."""
        try:
            # Rechercher les vidéos les plus performantes
            query = {
                "bool": {
                    "must": [
                        {"term": {"channel_id": channel_id}}
                    ]
                }
            }
            
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": query,
                    "size": 50,
                    "sort": [{"view_count": "desc"}]
                }
            )
            
            hits = response.get('hits', {}).get('hits', [])
            return [hit['_source'] for hit in hits]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des content gaps: {e}")
            return []