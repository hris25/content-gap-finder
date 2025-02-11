from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class YouTubeScraper:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY n'est pas définie")
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        
    def get_channel_info(self, channel_identifier: str) -> Dict:
        """Récupère les informations de base d'une chaîne YouTube."""
        try:
            # D'abord, essayer de trouver la chaîne par son nom d'utilisateur
            try:
                request = self.youtube.search().list(
                    part="id",
                    q=channel_identifier,
                    type="channel",
                    maxResults=1
                )
                response = request.execute()
                
                if response.get('items'):
                    channel_id = response['items'][0]['id']['channelId']
                    logger.debug(f"ID de chaîne trouvé pour {channel_identifier}: {channel_id}")
                else:
                    channel_id = channel_identifier
                    logger.debug(f"Utilisation directe de l'identifiant: {channel_id}")
                
            except Exception as e:
                logger.warning(f"Erreur lors de la recherche du canal, utilisation directe de l'identifiant: {e}")
                channel_id = channel_identifier
            
            # Récupérer les informations de la chaîne
            request = self.youtube.channels().list(
                part="snippet,statistics,contentDetails",
                id=channel_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError(f"Chaîne non trouvée pour l'identifiant: {channel_identifier}")
                
            channel_data = response['items'][0]
            return {
                'id': channel_id,
                'title': channel_data['snippet']['title'],
                'description': channel_data['snippet']['description'],
                'subscriber_count': channel_data['statistics'].get('subscriberCount', '0'),
                'video_count': channel_data['statistics'].get('videoCount', '0'),
                'view_count': channel_data['statistics'].get('viewCount', '0')
            }
        except HttpError as e:
            logger.error(f"Erreur API YouTube: {e}")
            raise ValueError(f"Erreur lors de l'accès à l'API YouTube: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            raise ValueError(f"Erreur lors de la récupération des informations de la chaîne: {str(e)}")
            
    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """Récupère les dernières vidéos d'une chaîne."""
        try:
            # D'abord, obtenir l'ID de la playlist des uploads
            playlist_id = self._get_uploads_playlist_id(channel_id)
            
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                # Récupérer les vidéos de la playlist
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                )
                response = request.execute()
                
                # Extraire les informations des vidéos
                for item in response['items']:
                    video_id = item['contentDetails']['videoId']
                    video_info = self._get_video_details(video_id)
                    if video_info:
                        videos.append(video_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            return videos
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des vidéos: {e}")
            return []

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
            'view_count': video_data['statistics'].get('viewCount', '0'),
            'like_count': video_data['statistics'].get('likeCount', '0'),
            'comment_count': video_data['statistics'].get('commentCount', '0'),
            'published_at': video_data['snippet']['publishedAt']
        }

    def _get_uploads_playlist_id(self, channel_id: str) -> str:
        """Récupère l'ID de la playlist des uploads d'une chaîne."""
        request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()
        
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']