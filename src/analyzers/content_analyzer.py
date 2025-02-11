from typing import List, Dict
import pandas as pd
from collections import Counter
import re
from datetime import datetime
import numpy as np
from src.utils.text_processor import extract_keywords
import logging

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self):
        self.common_words = set(['le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais'])

    def analyze_channel_content(self, videos: List[Dict]) -> Dict:
        """Analyse complète du contenu d'une chaîne."""
        if not videos:
            return {
                'performance_metrics': {},
                'content_patterns': {},
                'temporal_patterns': {},
                'engagement_analysis': {}
            }
            
        df = pd.DataFrame(videos)
        
        # Convertir les colonnes numériques
        numeric_columns = ['view_count', 'like_count', 'comment_count']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        return {
            'performance_metrics': self._analyze_performance(df),
            'content_patterns': self._analyze_content_patterns(df),
            'temporal_patterns': self._analyze_temporal_patterns(df),
            'engagement_analysis': self._analyze_engagement(df)
        }

    def _analyze_performance(self, df: pd.DataFrame) -> Dict:
        """Analyse les métriques de performance."""
        try:
            return {
                'average_views': int(df['view_count'].mean()),
                'median_views': int(df['view_count'].median()),
                'average_likes': int(df['like_count'].mean()),
                'average_comments': int(df['comment_count'].mean()),
                'top_performing_videos': self._get_top_performing(df)
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des performances: {e}")
            return {
                'average_views': 0,
                'median_views': 0,
                'average_likes': 0,
                'average_comments': 0,
                'top_performing_videos': []
            }

    def _analyze_content_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyse les patterns dans les titres et descriptions."""
        try:
            titles = ' '.join(df['title'].fillna('').tolist())
            keywords = extract_keywords(titles)
            
            return {
                'common_keywords': keywords[:10],
                'title_patterns': self._analyze_titles(df['title'].fillna('').tolist()),
                'video_categories': self._categorize_content(df)
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des patterns de contenu: {e}")
            return {
                'common_keywords': [],
                'title_patterns': {},
                'video_categories': []
            }

    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyse les patterns temporels de publication."""
        try:
            df['published_at'] = pd.to_datetime(df['published_at'])
            
            publication_days = df['published_at'].dt.day_name().value_counts()
            publication_hours = df['published_at'].dt.hour.value_counts()
            
            return {
                'best_days': publication_days.index[0] if not publication_days.empty else "N/A",
                'best_hours': int(publication_hours.index[0]) if not publication_hours.empty else 0,
                'posting_frequency': self._calculate_posting_frequency(df)
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des patterns temporels: {e}")
            return {
                'best_days': "N/A",
                'best_hours': 0,
                'posting_frequency': "N/A"
            }

    def _analyze_engagement(self, df: pd.DataFrame) -> Dict:
        """Analyse l'engagement des vidéos."""
        try:
            df['engagement_rate'] = ((df['like_count'] + df['comment_count']) / 
                                   df['view_count'].clip(lower=1))
            
            return {
                'average_engagement_rate': float(df['engagement_rate'].mean()),
                'high_engagement_topics': self._find_high_engagement_topics(df),
                'engagement_trend': self._calculate_engagement_trend(df)
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de l'engagement: {e}")
            return {
                'average_engagement_rate': 0.0,
                'high_engagement_topics': [],
                'engagement_trend': "stable"
            }

    def _get_top_performing(self, df: pd.DataFrame, n: int = 5) -> List[Dict]:
        """Identifie les vidéos les plus performantes."""
        try:
            top_videos = df.nlargest(n, 'view_count')
            return top_videos[['title', 'view_count', 'like_count']].to_dict('records')
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des meilleures vidéos: {e}")
            return []

    def _analyze_titles(self, titles: List[str]) -> Dict:
        """Analyse les patterns dans les titres."""
        try:
            lengths = [len(title.split()) for title in titles]
            formats = self._identify_title_formats(titles)
            questions = self._count_question_titles(titles)
            
            return {
                'average_length': float(np.mean(lengths)),
                'common_formats': formats,
                'question_percentage': questions
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des titres: {e}")
            return {
                'average_length': 0.0,
                'common_formats': {},
                'question_percentage': 0.0
            }

    def _identify_title_formats(self, titles: List[str]) -> Dict[str, int]:
        """Identifie les formats courants dans les titres."""
        try:
            formats = {
                'questions': 0,
                'numbers': 0,
                'brackets': 0,
                'emojis': 0,
                'caps': 0
            }
            
            emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "]+", flags=re.UNICODE)
            
            for title in titles:
                if any(q in title.lower() for q in ['quoi', 'comment', 'pourquoi', 'qui', 'où', 'quand', '?']):
                    formats['questions'] += 1
                if any(c.isdigit() for c in title):
                    formats['numbers'] += 1
                if '[' in title or ']' in title or '(' in title or ')' in title:
                    formats['brackets'] += 1
                if emoji_pattern.search(title):
                    formats['emojis'] += 1
                if title.isupper() or sum(1 for c in title if c.isupper()) > len(title) * 0.5:
                    formats['caps'] += 1
            
            total = len(titles) or 1
            return {k: (v / total) * 100 for k, v in formats.items()}
            
        except Exception as e:
            logger.error(f"Erreur lors de l'identification des formats de titre: {e}")
            return {}

    def _count_question_titles(self, titles: List[str]) -> float:
        """Compte le pourcentage de titres qui sont des questions."""
        try:
            question_count = sum(1 for title in titles if '?' in title)
            return (question_count / len(titles)) * 100 if titles else 0
        except Exception as e:
            logger.error(f"Erreur lors du comptage des titres questions: {e}")
            return 0.0

    def _categorize_content(self, df: pd.DataFrame) -> List[Dict]:
        """Catégorise le contenu en thèmes."""
        try:
            all_keywords = []
            for title in df['title']:
                keywords = extract_keywords(title)
                all_keywords.extend(keywords)
            
            keyword_counts = Counter(all_keywords)
            total = sum(keyword_counts.values())
            
            return [
                {
                    'theme': kw,
                    'percentage': (count / total) * 100
                }
                for kw, count in keyword_counts.most_common(5)
            ]
        except Exception as e:
            logger.error(f"Erreur lors de la catégorisation du contenu: {e}")
            return []

    def _calculate_posting_frequency(self, df: pd.DataFrame) -> str:
        """Calcule la fréquence moyenne de publication."""
        try:
            df = df.sort_values('published_at')
            if len(df) < 2:
                return "Données insuffisantes"
                
            dates = pd.to_datetime(df['published_at'])
            intervals = dates.diff()[1:]  # Ignorer la première différence qui sera NaT
            avg_days = intervals.mean().days
            
            if avg_days <= 1:
                return "Quotidienne"
            elif avg_days <= 7:
                return f"{avg_days:.1f} jours"
            elif avg_days <= 30:
                return f"{(avg_days/7):.1f} semaines"
            else:
                return f"{(avg_days/30):.1f} mois"
                
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la fréquence de publication: {e}")
            return "Non déterminé"

    def _find_high_engagement_topics(self, df: pd.DataFrame) -> List[Dict]:
        """Trouve les sujets qui génèrent le plus d'engagement."""
        try:
            df['total_engagement'] = df['like_count'] + df['comment_count']
            high_engagement = df.nlargest(5, 'total_engagement')
            
            topics = []
            for _, video in high_engagement.iterrows():
                keywords = extract_keywords(video['title'])
                topics.append({
                    'topic': ' '.join(keywords[:3]),
                    'engagement': int(video['total_engagement']),
                    'views': int(video['view_count'])
                })
            return topics
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des sujets à fort engagement: {e}")
            return []

    def _calculate_engagement_trend(self, df: pd.DataFrame) -> str:
        """Calcule la tendance de l'engagement au fil du temps."""
        try:
            df = df.sort_values('published_at')
            df['engagement_rate'] = (df['like_count'] + df['comment_count']) / df['view_count'].clip(lower=1)
            
            if len(df) < 5:
                return "stable"
                
            # Calculer la tendance
            x = np.arange(len(df))
            y = df['engagement_rate'].values
            z = np.polyfit(x, y, 1)
            slope = z[0]
            
            if slope > 0.001:
                return "en hausse"
            elif slope < -0.001:
                return "en baisse"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la tendance d'engagement: {e}")
            return "stable"