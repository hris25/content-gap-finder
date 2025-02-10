from typing import List, Dict
import pandas as pd
from collections import Counter
import re
from datetime import datetime
import numpy as np
from src.utils.text_processor import extract_keywords

class ContentAnalyzer:
    def __init__(self):
        self.common_words = set(['le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais'])

    def analyze_channel_content(self, videos: List[Dict]) -> Dict:
        """Analyse complète du contenu d'une chaîne."""
        df = pd.DataFrame(videos)
        
        return {
            'performance_metrics': self._analyze_performance(df),
            'content_patterns': self._analyze_content_patterns(df),
            'temporal_patterns': self._analyze_temporal_patterns(df),
            'engagement_analysis': self._analyze_engagement(df)
        }

    def _analyze_performance(self, df: pd.DataFrame) -> Dict:
        """Analyse les métriques de performance."""
        return {
            'average_views': int(df['view_count'].astype(int).mean()),
            'median_views': int(df['view_count'].astype(int).median()),
            'average_likes': int(df['like_count'].astype(int).mean()),
            'average_comments': int(df['comment_count'].astype(int).mean()),
            'top_performing_videos': self._get_top_performing(df)
        }

    def _analyze_content_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyse les patterns dans les titres et descriptions."""
        titles = ' '.join(df['title'].tolist())
        keywords = extract_keywords(titles)
        
        return {
            'common_keywords': keywords[:10],
            'title_patterns': self._analyze_titles(df['title'].tolist()),
            'video_categories': self._categorize_content(df)
        }

    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyse les patterns temporels de publication."""
        df['published_at'] = pd.to_datetime(df['published_at'])
        
        publication_days = df['published_at'].dt.day_name().value_counts()
        publication_hours = df['published_at'].dt.hour.value_counts()
        
        return {
            'best_days': publication_days.index[0],
            'best_hours': int(publication_hours.index[0]),
            'posting_frequency': self._calculate_posting_frequency(df)
        }

    def _analyze_engagement(self, df: pd.DataFrame) -> Dict:
        """Analyse l'engagement des vidéos."""
        df['engagement_rate'] = (df['like_count'].astype(int) + 
                               df['comment_count'].astype(int)) / df['view_count'].astype(int)
        
        return {
            'average_engagement_rate': float(df['engagement_rate'].mean()),
            'high_engagement_topics': self._find_high_engagement_topics(df),
            'engagement_trend': self._calculate_engagement_trend(df)
        }

    def _get_top_performing(self, df: pd.DataFrame, n: int = 5) -> List[Dict]:
        """Identifie les vidéos les plus performantes."""
        top_videos = df.nlargest(n, 'view_count')
        return top_videos[['title', 'view_count', 'like_count']].to_dict('records')

    def _analyze_titles(self, titles: List[str]) -> Dict:
        """Analyse les patterns dans les titres."""
        lengths = [len(title.split()) for title in titles]
        
        return {
            'average_length': np.mean(lengths),
            'common_formats': self._identify_title_formats(titles),
            'question_titles_percentage': self._count_question_titles(titles)
        }

    def _calculate_posting_frequency(self, df: pd.DataFrame) -> str:
        """Calcule la fréquence moyenne de publication."""
        dates = pd.to_datetime(df['published_at']).sort_values()
        diff_days = (dates.max() - dates.min()).days
        videos_count = len(df)
        
        avg_days_between = diff_days / videos_count
        
        if avg_days_between <= 1:
            return "Quotidienne"
        elif avg_days_between <= 3:
            return "2-3 fois par semaine"
        elif avg_days_between <= 7:
            return "Hebdomadaire"
        else:
            return f"Environ tous les {int(avg_days_between)} jours"

    def _find_high_engagement_topics(self, df: pd.DataFrame) -> List[str]:
        """Identifie les sujets qui génèrent le plus d'engagement."""
        df['keywords'] = df['title'].apply(extract_keywords)
        
        keyword_engagement = {}
        for idx, row in df.iterrows():
            for keyword in row['keywords']:
                if keyword not in keyword_engagement:
                    keyword_engagement[keyword] = []
                keyword_engagement[keyword].append(row['engagement_rate'])
        
        # Calculer l'engagement moyen par mot-clé
        avg_engagement = {k: np.mean(v) for k, v in keyword_engagement.items() 
                         if len(v) >= 3}  # Minimum 3 vidéos
        
        return sorted(avg_engagement.items(), 
                     key=lambda x: x[1], 
                     reverse=True)[:5]

    def _calculate_engagement_trend(self, df: pd.DataFrame) -> str:
        """Calcule la tendance de l'engagement au fil du temps."""
        df = df.sort_values('published_at')
        engagement_rates = df['engagement_rate'].tolist()
        
        if len(engagement_rates) < 2:
            return "Insuffisant de données"
            
        trend = np.polyfit(range(len(engagement_rates)), engagement_rates, 1)[0]
        
        if trend > 0.01:
            return "En hausse"
        elif trend < -0.01:
            return "En baisse"
        else:
            return "Stable"