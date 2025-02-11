from typing import List, Dict
import json
import logging
import os
from dotenv import load_dotenv
from together import Together

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv('TOGETHER_API_KEY')
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY non définie dans les variables d'environnement")
        self.client = Together()

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
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Tu es un expert en analyse de contenu YouTube et en stratégie de création de contenu.
Ta mission est d'analyser les données d'une chaîne YouTube et les opportunités de contenu identifiées pour suggérer des idées de vidéos pertinentes.
Tu dois tenir compte du style de la chaîne, de sa taille, et des opportunités spécifiques identifiées.
Tes suggestions doivent être précises, réalisables et alignées avec les opportunités de contenu identifiées.
Tu dois TOUJOURS répondre en format JSON valide selon le schéma demandé."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Erreur API Together: {e}")
            raise

    def _create_suggestion_prompt(self, 
                                channel_data: Dict, 
                                content_gaps: List[Dict]) -> str:
        """Crée un prompt pour la génération de suggestions."""
        channel_info = (
            f"Nom: {channel_data.get('title', 'Non spécifié')}\n"
            f"Nombre d'abonnés: {channel_data.get('subscriber_count', '0')}\n"
            f"Description: {channel_data.get('description', 'Non spécifié')}\n"
        )

        gaps_info = "Opportunités de contenu identifiées:\n"
        for gap in content_gaps[:5]:
            topic = gap.get('topic', 'Non spécifié')
            potential = gap.get('potential', 'Non spécifié')
            competition = gap.get('competition', 'Non spécifié')
            gaps_info += f"- Sujet: {topic}\n  Potentiel: {potential}\n  Niveau de compétition: {competition}\n"

        return f"""Analyse les informations suivantes et génère des suggestions de contenu adaptées:

DONNÉES DE LA CHAÎNE:
{channel_info}

ANALYSE DES OPPORTUNITÉS:
{gaps_info}

INSTRUCTIONS:
1. Génère exactement 5 suggestions de vidéos
2. Chaque suggestion doit exploiter une des opportunités identifiées
3. Les suggestions doivent correspondre au style et à la taille de la chaîne
4. Le format des titres doit être accrocheur et optimisé pour YouTube
5. Les points clés doivent être spécifiques et actionables

Réponds UNIQUEMENT avec un JSON valide au format suivant, sans texte avant ou après:

{{
    "suggestions": [
        {{
            "title": "Titre accrocheur de la vidéo",
            "topic": "Opportunité exploitée",
            "description": "Description courte et engageante",
            "estimated_potential": "Estimation du potentiel de vues",
            "key_points": ["Point clé 1", "Point clé 2", "Point clé 3"]
        }}
    ]
}}"""

    def _parse_ai_suggestions(self, response: str) -> List[Dict]:
        """Parse la réponse de l'IA en suggestions structurées."""
        try:
            # Nettoyer la réponse pour ne garder que le JSON
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            # Parser le JSON
            data = json.loads(json_str)
            
            # Vérifier la structure
            if not isinstance(data, dict) or 'suggestions' not in data:
                return []
                
            # Valider et nettoyer chaque suggestion
            suggestions = []
            for suggestion in data['suggestions']:
                if isinstance(suggestion, dict):
                    cleaned_suggestion = {
                        'title': str(suggestion.get('title', '')),
                        'topic': str(suggestion.get('topic', '')),
                        'description': str(suggestion.get('description', '')),
                        'estimated_potential': str(suggestion.get('estimated_potential', '')),
                        'key_points': [str(point) for point in suggestion.get('key_points', [])]
                    }
                    suggestions.append(cleaned_suggestion)
                    
            return suggestions
            
        except json.JSONDecodeError as e:
            logging.error(f"Erreur de parsing JSON: {e}")
            return []
        except Exception as e:
            logging.error(f"Erreur lors du parsing des suggestions: {e}")
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