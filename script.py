from together import Together
import os

# Définir la clé API directement (pour les tests uniquement)
os.environ["TOGETHER_API_KEY"] = "b5b2aa3d026a92cfb42606299601d9588d4c800b6537c561bf856c4259aa5f76"

# Initialiser le client Together
# Assurez-vous d'avoir défini votre clé API dans les variables d'environnement
# export TOGETHER_API_KEY='votre_clé_api'
client = Together()

def get_video_ideas(theme):
    try:
        # Créer un prompt détaillé en français
        prompt = f"""Suggère 5 idées de vidéos courtes sur le thème: {theme}.
Format pour chaque idée:
- Titre
- Description (2 lignes max)
- 3 points clés
"""

        # Appeler l'API Together
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en création de contenu YouTube qui donne des suggestions en français."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Ajuster la créativité des réponses
            max_tokens=1000   # Limiter la longueur de la réponse
        )

        # Afficher la réponse
        print("\n=== Suggestions de vidéos ===")
        print(response.choices[0].message.content)
        print(f"\nTokens utilisés : {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")

if __name__ == "__main__":
    # Exemple d'utilisation
    theme = input("Sur quel thème voulez-vous des suggestions de vidéos ? ")
    get_video_ideas(theme)
