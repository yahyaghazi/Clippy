"""
Client pour communiquer avec Ollama
"""

import requests
import json
from typing import Optional, Dict, Any
from ..config.settings import settings


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