from typing import List, Dict
import json
import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv('TOGETHER_API_KEY')
        self.api_url = "https://api.together.xyz/inference"
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY non définie dans les variables d'environnement")

    async def generate_content_suggestions(self, 
                                        channel_data: Dict,
                                        content_gaps: List[Dict]) -> List[Dict]:
        """Génère des suggestions de contenu personnalisées."""
        try:
            prompt = self._create_suggestion_prompt(channel_data, content_gaps)
            response = self._get_ai_response(prompt)
            return self._parse_ai_suggestions(response)
        except Exception as e:
            logging.error(f"Erreur lors de la génération des suggestions: {e}")
            return []

    async def analyze_competition(self, 
                                topic: str, 
                                existing_videos: List[Dict]) -> Dict:
        """Analyse la concurrence pour un sujet donné."""
        try:
            prompt = self._create_competition_prompt(topic, existing_videos)
            response = self._get_ai_response(prompt)
            return self._parse_competition_analysis(response)
        except Exception as e:
            logging.error(f"Erreur lors de l'analyse de la concurrence: {e}")
            return {}

    def _get_ai_response(self, prompt: str) -> str:
        """Obtient une réponse via l'API Together.ai."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "togethercomputer/llama-2-7b-chat",
            "prompt": f"<s>[INST] {prompt} [/INST]",
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.1
        }
        
        try:
            response = requests.post(self.api_url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()['output']['choices'][0]['text']
        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur API Together: {e}")
            raise

    def _create_suggestion_prompt(self, 
                                channel_data: Dict, 
                                content_gaps: List[Dict]) -> str:
        """Crée un prompt pour la génération de suggestions."""
        return f"""
        Analyse cette chaîne YouTube et suggère du contenu:

        Données de la chaîne:
        - Nom: {channel_data.get('title')}
        - Thèmes principaux: {', '.join(channel_data.get('main_topics', []))}
        - Nombre d'abonnés: {channel_data.get('subscriber_count')}

        Opportunités identifiées:
        {json.dumps(content_gaps[:5], indent=2, ensure_ascii=False)}

        Génère 5 suggestions de vidéos spécifiques qui:
        1. Correspondent au style de la chaîne
        2. Exploitent les opportunités identifiées
        3. Ont un potentiel de vues élevé

        Réponds uniquement avec un JSON au format suivant:
        {
            "suggestions": [
                {
                    "title": "Titre suggéré",
                    "topic": "Thème principal",
                    "description": "Description courte",
                    "estimated_potential": "Estimation du potentiel",
                    "key_points": ["Point 1", "Point 2", "Point 3"]
                }
            ]
        }
        """

    def _parse_ai_suggestions(self, response: str) -> List[Dict]:
        """Parse la réponse de l'IA en suggestions structurées."""
        try:
            # Nettoyer la réponse pour extraire uniquement le JSON
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            return data.get('suggestions', [])
        except json.JSONDecodeError:
            logging.error("Erreur de parsing de la réponse AI")
            return []

    def _create_competition_prompt(self, 
                                 topic: str, 
                                 existing_videos: List[Dict]) -> str:
        """Crée un prompt pour l'analyse de la concurrence."""
        return f"""
        Analyse la concurrence pour le sujet suivant: {topic}

        Vidéos existantes:
        {json.dumps(existing_videos[:5], indent=2, ensure_ascii=False)}

        Fournis une analyse détaillée incluant:
        1. Angles non exploités
        2. Points différenciants possibles
        3. Niveau de saturation du marché
        4. Suggestions d'approches uniques

        Réponds uniquement avec un JSON au format suivant:
        {
            "market_analysis": {
                "saturation_level": "élevé/moyen/faible",
                "unexplored_angles": ["angle 1", "angle 2"],
                "differentiators": ["différenciateur 1", "différenciateur 2"],
                "recommendations": ["recommandation 1", "recommandation 2"]
            }
        }
        """

    def _parse_competition_analysis(self, response: str) -> Dict:
        """Parse la réponse de l'analyse de concurrence."""
        try:
            json_str = self._extract_json(response)
            return json.loads(json_str)
        except json.JSONDecodeError:
            logging.error("Erreur de parsing de l'analyse de concurrence")
            return {}

    def _extract_json(self, text: str) -> str:
        """Extrait le JSON d'une réponse texte."""
        try:
            # Chercher le premier { et le dernier }
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                return text[start:end]
            return "{}"
        except Exception:
            return "{}"