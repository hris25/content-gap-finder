import re
from typing import List
from collections import Counter
import spacy

class TextProcessor:
    def __init__(self):
        self.nlp = spacy.load('fr_core_news_sm')
        self.stop_words = set(self.nlp.Defaults.stop_words)

    def extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés pertinents d'un texte."""
        # Nettoyage basique
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Traitement avec spaCy
        doc = self.nlp(text)
        
        # Extraction des mots pertinents (noms, adjectifs, verbes)
        keywords = [token.text for token in doc 
                   if not token.is_stop 
                   and token.pos_ in ['NOUN', 'ADJ', 'VERB']
                   and len(token.text) > 2]
        
        # Comptage des occurrences
        keyword_counts = Counter(keywords)
        
        # Retourner les mots-clés les plus fréquents
        return [word for word, count in keyword_counts.most_common(10)]

    def clean_text(self, text: str) -> str:
        """Nettoie le texte des caractères spéciaux et de la ponctuation."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

def extract_keywords(text: str) -> List[str]:
    """Fonction utilitaire pour extraire les mots-clés."""
    processor = TextProcessor()
    return processor.extract_keywords(text)