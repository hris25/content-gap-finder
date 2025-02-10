from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
import logging

load_dotenv()

class YouTubeScraper:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        
    def get_channel_info(self, channel_url: str) -> Dict:
        """Récupère les informations de base d'une chaîne YouTube."""
        try:
            # Extraire l'ID de la chaîne de l'URL
            channel_id = self._extract_channel_id(channel_url)
            
            request = self.youtube.channels().list(
                part="snippet,statistics,contentDetails",
                id=channel_id
            )
            response = request.execute()
            
            if not response['items']:
                raise ValueError("Chaîne non trouvée")
                
            channel_data = response['items'][0]
            return {
                'id': channel_id,
                'title': channel_data['snippet']['title'],
                'description': channel_data['snippet']['description'],
                'subscriber_count': channel_data['statistics']['subscriberCount'],
                'video_count': channel_data['statistics']['videoCount'],
                'view_count': channel_data['statistics']['viewCount']
            }
        except HttpError as e:
            logging.error(f"Erreur API YouTube: {e}")
            raise
            
    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """Récupère les dernières vidéos d'une chaîne."""
        try:
            # D'abord, obtenir l'ID de la playlist des uploads
            playlist_id = self._get_uploads_playlist_id(channel_id)
            
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                )
                response = request.execute()
                
                # Récupérer les détails de chaque vidéo
                for item in response['items']:
                    video_id = item['contentDetails']['videoId']
                    video_details = self._get_video_details(video_id)
                    videos.append(video_details)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            return videos
            
        except HttpError as e:
            logging.error(f"Erreur lors de la récupération des vidéos: {e}")
            raise

    def _get_video_details(self, video_id: str) -> Dict:
        """Récupère les détails d'une vidéo spécifique."""
        request = self.youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        )
        response = request.execute()
        
        video_data = response['items'][0]
        return {
            'id': video_id,
            'title': video_data['snippet']['title'],
            'description': video_data['snippet']['description'],
            'view_count': video_data['statistics']['viewCount'],
            'like_count': video_data['statistics'].get('likeCount', 0),
            'comment_count': video_data['statistics'].get('commentCount', 0),
            'published_at': video_data['snippet']['publishedAt']
        }

    def _extract_channel_id(self, channel_url: str) -> str:
        """Extrait l'ID de la chaîne à partir de l'URL."""
        # Gérer différents formats d'URL YouTube
        if 'youtube.com/channel/' in channel_url:
            return channel_url.split('channel/')[1].split('/')[0]
        elif 'youtube.com/c/' in channel_url:
            # Pour les URLs personnalisées, il faut faire une requête supplémentaire
            custom_name = channel_url.split('c/')[1].split('/')[0]
            return self._get_channel_id_from_custom_url(custom_name)
        raise ValueError("Format d'URL de chaîne non valide")

    def _get_channel_id_from_custom_url(self, custom_name: str) -> str:
        """Récupère l'ID de la chaîne à partir d'un nom personnalisé."""
        request = self.youtube.search().list(
            part="snippet",
            q=custom_name,
            type="channel",
            maxResults=1
        )
        response = request.execute()
        
        if not response['items']:
            raise ValueError("Chaîne non trouvée")
            
        return response['items'][0]['snippet']['channelId']

    def _get_uploads_playlist_id(self, channel_id: str) -> str:
        """Récupère l'ID de la playlist des uploads d'une chaîne."""
        request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()
        
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']