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

app = FastAPI(title="Content Gap Finder")

# Configuration des dossiers statiques et templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/analyze-channel")
async def analyze_channel(channel_url: str):
    try:
        scraper = YouTubeScraper()
        analyzer = ContentAnalyzer()
        es_service = ElasticsearchService()
        ai_service = AIService()
        
        # Récupérer les informations de la chaîne
        channel_info = scraper.get_channel_info(channel_url)
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
        
        return {
            "channel_info": channel_info,
            "analysis": analysis,
            "content_gaps": content_gaps,
            "ai_suggestions": ai_suggestions
        }
    except Exception as e:
        logging.error(f"Erreur lors de l'analyse: {e}")
        raise HTTPException(status_code=400, detail=str(e))

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
        logging.error(f"Erreur lors de l'analyse du sujet: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)