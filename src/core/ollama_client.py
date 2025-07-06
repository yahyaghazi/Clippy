"""
Client pour communiquer avec Ollama
"""

import requests
import json
from typing import Optional, Dict, Any
from ..config.settings import settings
from ..utils.app_mapper import app_mapper


class OllamaClient:
    """Client pour l'API Ollama"""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.ollama.base_url
        self.model = model or settings.ollama.model
        self.available = False
        self.last_error = None
        
        # Vérifier la connexion au démarrage
        self.check_connection()
    
    def check_connection(self) -> bool:
        """Vérifie si Ollama est accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            self.available = response.status_code == 200
            
            if self.available:
                print("✅ Ollama connecté !")
                self.last_error = None
            else:
                self.last_error = f"HTTP {response.status_code}"
                print(f"❌ Ollama non accessible: {self.last_error}")
                
        except requests.exceptions.ConnectionError:
            self.available = False
            self.last_error = "Connexion refusée"
            print("❌ Ollama non accessible: connexion refusée")
        except requests.exceptions.Timeout:
            self.available = False
            self.last_error = "Timeout de connexion"
            print("❌ Ollama non accessible: timeout")
        except Exception as e:
            self.available = False
            self.last_error = str(e)
            print(f"❌ Erreur connexion Ollama: {e}")
        
        return self.available
    
    def get_available_models(self) -> list:
        """Récupère la liste des modèles disponibles"""
        if not self.available:
            return []
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            print(f"Erreur récupération modèles: {e}")
        
        return []
    
    def generate_suggestion(self, app_name: str, context: str) -> str:
        """Génère une suggestion contextuelle pour l'application"""
        if not self.available:
            return "🔌 Ollama non connecté (démarrez: ollama serve)"
        
        try:
            # Obtenir la catégorie de l'application
            category = app_mapper.get_app_category(app_name)
            
            # Créer un prompt contextualisé
            prompt = self._create_contextual_prompt(app_name, context, category)
            
            if settings.debug_mode:
                print(f"[DEBUG OLLAMA] Génération pour {app_name} - {context}")
            
            # Appel API Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": settings.ollama.temperature,
                    "num_predict": settings.ollama.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=settings.ollama.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestion = result.get("response", "").strip()
                
                # Nettoyer la suggestion
                cleaned_suggestion = self._clean_suggestion(suggestion)
                return cleaned_suggestion or "Continuez votre bon travail !"
            
            else:
                return f"❌ Erreur Ollama (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "⏱️ Timeout - Ollama met trop de temps à répondre"
        except requests.exceptions.ConnectionError:
            self.available = False
            return "🔌 Connexion Ollama perdue"
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def _create_contextual_prompt(self, app_name: str, context: str, category: str) -> str:
        """Crée un prompt contextualisé selon l'application"""
        base_prompt = f"""Tu es un assistant IA bienveillant. L'utilisateur utilise actuellement {app_name} ({category}).

Contexte: {context}

Donne UN SEUL conseil pratique et utile en français, en 1 phrase courte et claire.
Le conseil doit être spécifique à {app_name} et immédiatement applicable.

Exemples de bons conseils:
- "Essaie Ctrl+Shift+T pour rouvrir un onglet fermé"
- "Utilise F12 pour déboguer ton code"
- "Pense à sauvegarder avec Ctrl+S"

Réponds UNIQUEMENT avec le conseil, sans introduction."""

        # Personnalisation selon la catégorie
        if category == "Navigation":
            return base_prompt + "\nFocus sur les raccourcis de navigation web, onglets, et productivité browsing."
        elif category == "Développement":
            return base_prompt + "\nFocus sur les raccourcis de développement, debugging, et productivité code."
        elif category == "Bureautique":
            return base_prompt + "\nFocus sur les fonctionnalités Office, mise en forme, et productivité document."
        elif category == "Système":
            return base_prompt + "\nFocus sur les commandes système, navigation fichiers, et administration."
        else:
            return base_prompt + "\nFocus sur la productivité générale et les bonnes pratiques."
    
    def _clean_suggestion(self, suggestion: str) -> str:
        """Nettoie la suggestion générée"""
        if not suggestion:
            return ""
        
        # Supprimer les préfixes communs
        prefixes_to_remove = [
            "Voici un conseil :", "Conseil :", "Astuce :", "Suggestion :",
            "Je recommande :", "Tu peux :", "Il est recommandé de :",
            "N'hésite pas à :", "Pense à :", "Essaie de :"
        ]
        
        cleaned = suggestion.strip()
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        # Enlever les guillemets en début/fin
        cleaned = cleaned.strip('"\'')
        
        # S'assurer que ça commence par une majuscule
        if cleaned and cleaned[0].islower():
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        # Limiter la longueur
        if len(cleaned) > 100:
            # Couper à la dernière phrase complète
            sentences = cleaned.split('.')
            if len(sentences) > 1:
                cleaned = sentences[0] + '.'
            else:
                cleaned = cleaned[:97] + "..."
        
        return cleaned
    
    def test_model(self, test_prompt: str = "Dis bonjour en une phrase.") -> Dict[str, Any]:
        """Teste le modèle avec un prompt simple"""
        if not self.available:
            return {"success": False, "error": "Ollama non disponible"}
        
        try:
            payload = {
                "model": self.model,
                "prompt": test_prompt,
                "stream": False,
                "options": {"num_predict": 50}
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0)
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}