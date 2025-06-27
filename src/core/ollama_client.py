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
        """Génère une suggestion contextuelle"""
        print(f"[DEBUG OLLAMA] Génération pour {app_name} - {context}")
        
        if not self.available:
            result = f"🔌 Ollama non connecté ({self.last_error or 'Inconnu'})"
            print(f"[DEBUG OLLAMA] Retour: {result}")
            return result
        
        # Obtenir la catégorie de l'application
        from ..utils.app_mapper import app_mapper
        app_category = app_mapper.get_app_category(app_name)
        
        # Créer un prompt adapté
        prompt = self._create_contextual_prompt(app_name, context, app_category)
        
        try:
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
                
                if suggestion:
                    cleaned = self._clean_suggestion(suggestion)
                    print(f"[DEBUG OLLAMA] Suggestion générée: {cleaned[:100]}...")
                    return cleaned
                else:
                    fallback = "🤔 Pas de suggestion pour le moment"
                    print(f"[DEBUG OLLAMA] Pas de réponse, fallback: {fallback}")
                    return fallback
            else:
                error_msg = f"❌ Erreur Ollama: HTTP {response.status_code}"
                print(f"[DEBUG OLLAMA] Erreur HTTP: {error_msg}")
                return error_msg
                
        except requests.exceptions.Timeout:
            return "⏱️ Timeout - Ollama surchargé"
        except requests.exceptions.ConnectionError:
            self.available = False
            return "🔌 Connexion perdue avec Ollama"
        except Exception as e:
            print(f"Erreur génération: {e}")
            return "🔄 Erreur lors de la génération"
    
    def _create_contextual_prompt(self, app_name: str, context: str, category: str) -> str:
        """Crée un prompt adapté au contexte"""
        base_prompt = f"""Tu es un assistant de productivité qui aide l'utilisateur selon son contexte actuel.

Application: {app_name}
Catégorie: {category}
Contexte: {context}

Donne UN conseil pratique et spécifique (1-2 phrases maximum) pour cette situation.
"""
        
        # Prompts spécialisés par catégorie
        category_prompts = {
            'Navigation': """
Exemples de conseils pour navigateurs:
- "Essaie Ctrl+Shift+T pour rouvrir un onglet fermé !"
- "Utilise Ctrl+L pour aller directement à la barre d'adresse."
- "Ctrl+Shift+N pour ouvrir une fenêtre de navigation privée."
""",
            'Développement': """
Exemples de conseils pour développement:
- "N'oublie pas Ctrl+Shift+P pour la palette de commandes !"
- "Utilise Ctrl+` pour ouvrir/fermer le terminal intégré."
- "F12 pour déboguer ton code pas à pas."
""",
            'Bureautique': """
Exemples de conseils pour bureautique:
- "Ctrl+S pour sauvegarder régulièrement ton travail !"
- "F7 pour vérifier l'orthographe de ton document."
- "Utilise les styles pour une mise en forme cohérente."
""",
            'Système': """
Exemples de conseils pour système:
- "Tape 'cls' pour nettoyer l'écran."
- "Utilise Tab pour l'autocomplétion."
- "Flèche haut pour rappeler la dernière commande."
""",
            'Communication': """
Exemples de conseils pour communication:
- "Utilise @nom pour mentionner quelqu'un."
- "Ctrl+Shift+M pour couper/remettre le micro."
- "Organise tes conversations avec des dossiers."
"""
        }
        
        category_specific = category_prompts.get(category, "")
        
        return base_prompt + category_specific + "\nRéponds avec un émoji et un conseil court:"
    
    def _clean_suggestion(self, suggestion: str) -> str:
        """Nettoie la réponse de l'IA"""
        # Supprimer les préfixes courants
        prefixes_to_remove = [
            "Voici un conseil :",
            "Conseil :",
            "Astuce :",
            "💡",
            "Suggestion :"
        ]
        
        cleaned = suggestion
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # Limiter la longueur
        if len(cleaned) > 200:
            cleaned = cleaned[:197] + "..."
        
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