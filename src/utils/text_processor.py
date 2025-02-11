import spacy
from typing import List
import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

def load_spacy_model():
    """Charge le modèle spaCy avec gestion des erreurs."""
    try:
        return spacy.load('fr_core_news_sm')
    except OSError:
        logger.warning("Modèle spaCy français non trouvé. Utilisation d'une méthode de repli.")
        return None

nlp = load_spacy_model()

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extrait les mots-clés d'un texte."""
    try:
        # Nettoyage basique du texte
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        if nlp:
            # Utiliser spaCy si disponible
            doc = nlp(text)
            # Extraire les noms et adjectifs significatifs
            keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN', 'ADJ'] 
                       and not token.is_stop and len(token.text) > 2]
        else:
            # Méthode de repli simple basée sur la fréquence des mots
            words = text.split()
            # Filtrer les mots courts et les mots vides courants
            stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais', 'donc',
                         'car', 'pour', 'dans', 'sur', 'avec', 'sans', 'par'}
            keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Compter les occurrences
        keyword_counts = Counter(keywords)
        
        # Retourner les mots-clés les plus fréquents
        return [word for word, count in keyword_counts.most_common(max_keywords)]
        
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des mots-clés: {e}")
        return []

def analyze_sentiment(text: str) -> str:
    """Analyse le sentiment d'un texte."""
    try:
        if not nlp:
            return "neutre"
            
        doc = nlp(text)
        # Analyse simple basée sur des mots positifs/négatifs
        positive_words = {'super', 'génial', 'excellent', 'incroyable', 'parfait', 'merci'}
        negative_words = {'mauvais', 'nul', 'terrible', 'horrible', 'problème', 'bug'}
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positif"
        elif negative_count > positive_count:
            return "négatif"
        return "neutre"
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du sentiment: {e}")
        return "neutre"