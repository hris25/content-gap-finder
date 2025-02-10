from elasticsearch import Elasticsearch
from typing import Dict, List
import os
from datetime import datetime
import logging

class ElasticsearchService:
    def __init__(self):
        self.es = Elasticsearch(os.getenv('ELASTICSEARCH_URL'))
        self.index_name = 'youtube_content'
        self._create_index_if_not_exists()

    def _create_index_if_not_exists(self):
        """Crée l'index avec le mapping approprié s'il n'existe pas."""
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

    def index_video(self, video_data: Dict):
        """Indexe une vidéo dans Elasticsearch."""
        try:
            self.es.index(
                index=self.index_name,
                id=video_data['video_id'],
                document=video_data
            )
        except Exception as e:
            logging.error(f"Erreur lors de l'indexation: {e}")
            raise

    def find_content_gaps(self, channel_id: str) -> List[Dict]:
        """Trouve les opportunités de contenu basées sur les données existantes."""
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must_not": [
                        {"term": {"channel_id": channel_id}}
                    ]
                }
            },
            "aggs": {
                "successful_topics": {
                    "terms": {
                        "field": "topics",
                        "size": 20,
                        "order": {"avg_views": "desc"}
                    },
                    "aggs": {
                        "avg_views": {"avg": {"field": "view_count"}},
                        "avg_engagement": {"avg": {"field": "engagement_rate"}}
                    }
                }
            }
        }

        results = self.es.search(index=self.index_name, body=query)
        return self._process_content_gaps(results)

    def _process_content_gaps(self, results: Dict) -> List[Dict]:
        """Traite les résultats bruts pour identifier les opportunités."""
        gaps = []
        for bucket in results['aggregations']['successful_topics']['buckets']:
            gaps.append({
                'topic': bucket['key'],
                'average_views': int(bucket['avg_views']['value']),
                'average_engagement': float(bucket['avg_engagement']['value']),
                'opportunity_score': self._calculate_opportunity_score(
                    bucket['avg_views']['value'],
                    bucket['avg_engagement']['value']
                )
            })
        return sorted(gaps, key=lambda x: x['opportunity_score'], reverse=True)

    def _calculate_opportunity_score(self, views: float, engagement: float) -> float:
        """Calcule un score d'opportunité basé sur les vues et l'engagement."""
        return (views * 0.7 + (engagement * 10000) * 0.3) / 10000