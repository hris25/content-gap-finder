from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.scrapers.youtube_scraper import YouTubeScraper
from src.analyzers.content_analyzer import ContentAnalyzer
from pathlib import Path
import uvicorn
from src.services.elasticsearch_service import ElasticsearchService
from src.services.ai_service import AIService
import logging
import re
from urllib.parse import unquote

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Content Gap Finder")

# Configuration des dossiers statiques et templates
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Middleware pour désactiver le cache en développement
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if "static" in request.url.path:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

templates = Jinja2Templates(directory="templates")

def extract_channel_id(url: str) -> str:
    """Extrait l'ID de la chaîne à partir de différents formats d'URL YouTube."""
    # Nettoyage et décodage de l'URL
    url = unquote(url.strip())
    logger.debug(f"URL après nettoyage: {url}")

    patterns = [
        (r'(?:https?://)?(?:www\.)?youtube\.com/@([^/\s?]+)', 'username'),  # Format @username
        (r'(?:https?://)?(?:www\.)?youtube\.com/channel/(UC[^/\s?]+)', 'channel'),  # Format channel/ID
        (r'(?:https?://)?(?:www\.)?youtube\.com/c/([^/\s?]+)', 'custom'),  # Format c/custom_name
        (r'(?:https?://)?(?:www\.)?youtube\.com/user/([^/\s?]+)', 'user')  # Format user/username
    ]
    
    for pattern, pattern_type in patterns:
        logger.debug(f"Essai du pattern {pattern_type}: {pattern}")
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            result = match.group(1)
            logger.debug(f"Match trouvé ({pattern_type}): {result}")
            return result

    logger.error(f"Aucun pattern ne correspond à l'URL: {url}")
    raise ValueError("Format d'URL YouTube non valide")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/analyze-channel")
async def analyze_channel(channel_url: str):
    try:
        # Validation de l'URL
        logger.info(f"URL reçue (brute): {channel_url}")
        
        if not channel_url:
            raise ValueError("URL non fournie")
        
        if "youtube.com" not in channel_url.lower():
            raise ValueError("L'URL doit être une URL YouTube valide")

        channel_identifier = extract_channel_id(channel_url)
        logger.info(f"Identifiant extrait: {channel_identifier}")
        
        scraper = YouTubeScraper()
        analyzer = ContentAnalyzer()
        es_service = ElasticsearchService()
        ai_service = AIService()
        
        # Récupérer les informations de la chaîne
        channel_info = scraper.get_channel_info(channel_identifier)
        if not channel_info:
            raise ValueError("Impossible de récupérer les informations de la chaîne")
            
        videos = scraper.get_channel_videos(channel_info['id'], max_results=50)
        
        # Analyser le contenu
        analysis = analyzer.analyze_channel_content(videos)
        
        # Indexer les vidéos dans Elasticsearch
        for video in videos:
            es_service.index_video({
                **video,
                'channel_id': channel_info['id'],
                'analysis': analyzer.analyze_channel_content([video])
            })
        
        # Trouver les opportunités de contenu
        content_gaps = es_service.find_content_gaps(channel_info['id'])
        
        # Générer des suggestions d'IA
        ai_suggestions = await ai_service.generate_content_suggestions(
            channel_info,
            content_gaps
        )
        
        # Formater la réponse
        response = {
            'channel_info': {
                'title': channel_info.get('title', ''),
                'subscriber_count': int(channel_info.get('subscriber_count', 0)),
                'video_count': int(channel_info.get('video_count', 0)),
                'view_count': int(channel_info.get('view_count', 0))
            },
            'analysis': {
                'performance_metrics': analysis.get('performance_metrics', {}),
                'content_patterns': analysis.get('content_patterns', {
                    'common_keywords': [],
                    'title_patterns': {},
                    'video_categories': []
                }),
                'temporal_patterns': analysis.get('temporal_patterns', {
                    'best_days': 'Non déterminé',
                    'best_hours': 0,
                    'posting_frequency': 'Non déterminé'
                }),
                'engagement_analysis': analysis.get('engagement_analysis', {
                    'high_engagement_topics': [],
                    'engagement_trend': 'stable'
                })
            },
            'content_gaps': content_gaps or [],
            'ai_suggestions': ai_suggestions or []
        }
        
        return response
        
    except ValueError as e:
        logger.error(f"Erreur de validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        raise HTTPException(status_code=500, detail="Une erreur est survenue lors de l'analyse")

@app.get("/api/analyze-topic")
async def analyze_topic(topic: str):
    try:
        es_service = ElasticsearchService()
        ai_service = AIService()
        
        # Rechercher les vidéos existantes sur ce sujet
        existing_videos = es_service.search_videos_by_topic(topic)
        
        # Analyser la concurrence
        competition_analysis = await ai_service.analyze_competition(
            topic,
            existing_videos
        )
        
        return {
            "topic": topic,
            "competition_analysis": competition_analysis,
            "existing_videos": existing_videos[:5]  # Limiter à 5 exemples
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du sujet: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)