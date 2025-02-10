
# Content Gap Finder (YouTube)

Un outil puissant pour aider les créateurs YouTube à identifier les opportunités de contenu inexploitées dans leur niche.

## Fonctionnalités

### Analyse de la Concurrence
- Analyse détaillée des chaînes concurrentes
- Suivi des métriques clés (vues, engagement, fréquence de publication)
- Identification des formats de contenu performants
- Analyse des tendances saisonnières

### Recherche de Mots-clés
- Suggestions de mots-clés pertinents
- Analyse du volume de recherche
- Difficulté de classement
- Tendances des recherches

### Intelligence Artificielle
- Génération de titres optimisés
- Suggestions de sujets connexes
- Analyse du sentiment des commentaires
- Prédiction des performances potentielles

### Rapports et Analytics
- Tableaux de bord personnalisables
- Exportation des données en CSV/PDF
- Rapports hebdomadaires automatisés
- Suivi des progrès

## Écrans de l'Application

### 1. Dashboard Principal
- Vue d'ensemble des opportunités
- Graphiques de performance
- Alertes et notifications
- Résumé des analyses récentes

### 2. Analyse des Concurrents
- Liste des concurrents suivis
- Comparaison des métriques
- Calendrier de publication
- Analyse des meilleures vidéos

### 3. Recherche de Contenu
- Barre de recherche avancée
- Filtres par catégorie
- Suggestions d'idées
- Score de potentiel

### 4. Planification
- Calendrier éditorial
- Liste des contenus à produire
- Rappels et échéances
- Statut des projets

## Structure du Projet

```
content-gap-finder/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
├── src/
│   ├── scrapers/
│   ├── analyzers/
│   └── utils/
├── main.py
└── requirements.txt
```

## Technologies Utilisées

- Backend: Python, FastAPI
- Frontend: HTML5, CSS3, JavaScript (D3.js)
- Base de données: Elasticsearch
- NLP: SpaCy, GPT-4
- Scraping: BeautifulSoup4





# Content Gap Finder - README

## Description
Content Gap Finder est un outil d'analyse de contenu YouTube qui aide à identifier les opportunités de contenu et à optimiser la stratégie de création de vidéos.

## Alternative à Elasticsearch
Pour simplifier le développement, nous pouvons utiliser SQLite ou MongoDB Atlas (cloud gratuit) à la place d'Elasticsearch. Voici la version modifiée du service de stockage utilisant MongoDB Atlas :

```python:src/services/storage_service.py
from pymongo import MongoClient
import os
from typing import Dict, List
import logging
from datetime import datetime

class StorageService:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client.content_gap_finder
        self.videos = self.db.videos
        self.analyses = self.db.analyses

    def store_video(self, video_data: Dict):
        """Stocke les données d'une vidéo."""
        video_data['created_at'] = datetime.utcnow()
        self.videos.insert_one(video_data)

    def find_content_gaps(self, channel_id: str) -> List[Dict]:
        """Trouve les opportunités de contenu."""
        pipeline = [
            {"$match": {"channel_id": {"$ne": channel_id}}},
            {"$group": {
                "_id": "$topic",
                "avg_views": {"$avg": "$view_count"},
                "avg_engagement": {"$avg": "$engagement_rate"}
            }},
            {"$sort": {"avg_views": -1}},
            {"$limit": 20}
        ]
        return list(self.videos.aggregate(pipeline))
```

## Configuration du Projet

### 1. Prérequis
- Python 3.8+
- Un compte MongoDB Atlas (gratuit)
- Un compte Together.ai (pour l'API LLM)
- Une clé API YouTube

### 2. Installation

```bash
# Cloner le projet
git clone <url-du-projet>
cd content-gap-finder

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur macOS/Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration des Variables d'Environnement
Créez un fichier `.env` à la racine du projet :

```env
YOUTUBE_API_KEY=votre_clé_api_youtube
TOGETHER_API_KEY=votre_clé_api_together
MONGODB_URI=votre_uri_mongodb_atlas
ENV=development
```

### 4. Structure du Projet
```
content-gap-finder/
├── main.py
├── requirements.txt
├── .env
├── src/
│   ├── scrapers/
│   │   ├── __init__.py
│   │   └── youtube_scraper.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   └── content_analyzer.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   └── storage_service.py
│   └── utils/
│       ├── __init__.py
│       └── text_processor.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/
    ├── base.html
    └── index.html
```

### 5. Configuration MongoDB Atlas
1. Créez un compte sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Créez un cluster gratuit
3. Dans "Network Access", ajoutez votre IP
4. Dans "Database Access", créez un utilisateur
5. Cliquez sur "Connect" et copiez l'URI de connexion
6. Remplacez `<password>` dans l'URI par votre mot de passe

### 6. Obtenir les Clés API
1. YouTube API :
   - Allez sur [Google Cloud Console](https://console.cloud.google.com)
   - Créez un projet
   - Activez YouTube Data API v3
   - Créez des identifiants (clé API)

2. Together.ai :
   - Inscrivez-vous sur [Together.ai](https://www.together.ai)
   - Allez dans les paramètres API
   - Créez une nouvelle clé API

### 7. Lancer l'Application

```bash
python main.py
```
L'application sera accessible sur `http://localhost:8000`

## Endpoints API

- `GET /` : Page d'accueil
- `GET /api/health` : Vérification de l'état de l'API
- `GET /api/analyze-channel` : Analyse une chaîne YouTube
  - Paramètre : `channel_url` (URL de la chaîne YouTube)

## Fonctionnalités Implémentées
- [x] Scraping de données YouTube
- [x] Analyse de contenu
- [x] Intégration IA avec Together.ai
- [x] Stockage des données avec MongoDB
- [x] Interface utilisateur de base

## Prochaines Étapes
1. Améliorer l'interface utilisateur
2. Ajouter des graphiques et visualisations
3. Implémenter l'analyse de la concurrence
4. Ajouter des rapports PDF
5. Optimiser les performances

## Contribution
1. Forkez le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## Support
Pour toute question ou problème, ouvrez une issue sur le projet.

## Notes
- Les données sont stockées dans MongoDB Atlas (version gratuite)
- L'API Together.ai est utilisée pour l'analyse IA
- L'application est en développement actif


