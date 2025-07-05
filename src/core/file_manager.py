"""
Gestionnaire de fichiers avec IA pour l'Assistant
"""

import os
import json
import shutil
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any
import requests

from ..config.settings import settings


class FileManager:
    """Gestionnaire de fichiers intelligent avec IA"""
    
    def __init__(self, base_directory: str = None):
        # self.base_directory = base_directory or str(Path.home() / "Documents" / "AI_Assistant_Files")
        self.base_directory = base_directory or str(Path.home())  # Utilisation de C:\ pour Windows, sinon utiliser Path.home() pour Linux/Mac
        self.last_file_logical = None
        self.last_path_found = None
        
        # Créer le dossier de base s'il n'existe pas (inutile pour C:\ mais conservé pour compatibilité)
        Path(self.base_directory).mkdir(parents=True, exist_ok=True)
        
        print(f"[FILE_MANAGER] Dossier de base: {self.base_directory}")
    
    def analyze_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Analyse une commande en langage naturel avec l'IA"""
        prompt = f"""
Tu es un assistant IA spécialisé dans la gestion de fichiers. Analyse cette commande en français et retourne un JSON structuré :

- "action" : lancer, déplacer, modifier_code, creer, ouvrir, supprimer
- "fichier" : nom logique du fichier (ex : test.py, index.html, mon_script.js)
- "chemin" : dossier cible relatif (ex : python, html, scripts, backup)
- "instruction" : consigne textuelle pour générer/modifier du code
- "type_fichier" : extension du fichier (py, html, js, txt, etc.)

⚠️ Réponds uniquement avec un JSON valide. Aucune explication.

Exemples de commandes :
- "crée un script python qui calcule les nombres premiers" → {{"action": "creer", "fichier": "nombres_premiers.py", "chemin": "python", "instruction": "script qui calcule et affiche les nombres premiers jusqu'à 100", "type_fichier": "py"}}
- "lance le fichier test" → {{"action": "lancer", "fichier": "test", "chemin": "", "instruction": "", "type_fichier": ""}}
- "modifie index.html pour ajouter un menu" → {{"action": "modifier_code", "fichier": "index.html", "chemin": "", "instruction": "ajouter un menu de navigation horizontal", "type_fichier": "html"}}

Commande : {command}
"""
        
        try:
            # Utiliser le client Ollama existant
            from .ollama_client import OllamaClient
            ollama = OllamaClient()
            
            if not ollama.available:
                print("[FILE_MANAGER] Ollama non disponible")
                return None
            
            response = requests.post(
                f"{ollama.base_url}/api/generate",
                json={
                    "model": ollama.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Plus déterministe pour l'analyse
                        "num_predict": 200
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                return self._extract_json(text)
            else:
                print(f"[FILE_MANAGER] Erreur API: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[FILE_MANAGER] Erreur analyse: {e}")
            return None
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extrait le JSON de la réponse de l'IA"""
        # Rechercher le JSON dans le texte
        match = re.search(r'\{[\s\S]+\}', text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as e:
                print(f"[FILE_MANAGER] JSON mal formé: {e}")
        
        print(f"[FILE_MANAGER] Réponse non exploitable: {text}")
        return None
    
    def find_file(self, logical_name: str) -> Optional[str]:
        """Recherche un fichier par son nom logique"""
        if not logical_name:
            return None
        
        # Mots-clés de recherche
        keywords = logical_name.lower().split()
        candidates = []
        
        # Parcourir récursivement le dossier de base
        for root, dirs, files in os.walk(self.base_directory):
            for file in files:
                file_lower = file.lower()
                # Vérifier si tous les mots-clés sont dans le nom de fichier
                if all(keyword in file_lower for keyword in keywords):
                    candidates.append(os.path.join(root, file))
        
        # Fallback pour les fichiers HTML
        if not candidates and any(keyword in ["site", "page", "web"] for keyword in keywords):
            for root, dirs, files in os.walk(self.base_directory):
                for file in files:
                    if file.lower().endswith(".html"):
                        candidates.append(os.path.join(root, file))
        
        return candidates[0] if candidates else None
    
    def _clean_code(self, raw_code: str) -> str:
            """Nettoie le code généré par l'IA"""
            code = raw_code.strip()
            
            # Supprimer les explications avant le code
            lines = code.split('\n')
            code_start = 0
            
            # Trouver où commence le vrai code
            for i, line in enumerate(lines):
                line_clean = line.strip()
                if (line_clean.startswith('```') or 
                    line_clean.startswith('def ') or 
                    line_clean.startswith('import ') or
                    line_clean.startswith('from ') or
                    line_clean.startswith('#') or
                    line_clean.startswith('print(') or
                    line_clean.startswith('if ') or
                    line_clean.startswith('for ') or
                    line_clean.startswith('while ') or
                    line_clean.startswith('class ') or
                    line_clean.startswith('<!DOCTYPE') or
                    line_clean.startswith('<html') or
                    line_clean.startswith('function ') or
                    line_clean.startswith('var ') or
                    line_clean.startswith('let ') or
                    line_clean.startswith('const ')):
                    code_start = i
                    break
            
            # Prendre seulement la partie code
            code_lines = lines[code_start:]
            code = '\n'.join(code_lines)
            
            # Supprimer les balises markdown
            if '```' in code:
                # Supprimer la première balise ```python, ```html, etc.
                code = re.sub(r'^```[a-z]*\n?', '', code, flags=re.MULTILINE)
                # Supprimer la balise de fin ```
                code = re.sub(r'\n?```$', '', code, flags=re.MULTILINE)
            
            # Supprimer les explications après le code
            lines = code.split('\n')
            code_end = len(lines)
            
            # Trouver où finit le vrai code (supprimer les explications de fin)
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if line and not (
                    line.startswith('Ce code') or
                    line.startswith('Cette fonction') or
                    line.startswith('Le script') or
                    line.startswith('Finalement') or
                    line.startswith('Ensuite') or
                    line.lower().startswith('explication') or
                    'utilise une fonction' in line.lower() or
                    'affiche la liste' in line.lower()
                ):
                    code_end = i + 1
                    break
            
            # Prendre seulement le code sans explications
            if code_end < len(lines):
                code = '\n'.join(lines[:code_end])
            
            return code.strip()
    
    def generate_code(self, instruction: str, file_type: str = "") -> Optional[str]:
        """Génère du code avec l'IA selon les instructions - VERSION AMÉLIORÉE"""
        language_hints = {
            "py": "Python",
            "js": "JavaScript", 
            "html": "HTML",
            "css": "CSS",
            "java": "Java",
            "cpp": "C++",
            "c": "C"
        }
        
        language = language_hints.get(file_type.lower(), "")
        
        prompt = f"""Tu es un expert en programmation. Génère UNIQUEMENT le code pour cette consigne, sans aucune explication :

Consigne : {instruction}
Langage : {language}

IMPORTANT :
- Réponds UNIQUEMENT avec le code
- Aucune explication avant, pendant ou après
- Pas de balises markdown
- Pas de commentaires explicatifs
- Code prêt à être exécuté directement

Code :"""

        try:
            from ..core.ollama_client import OllamaClient
            ollama = OllamaClient()
            
            if not ollama.available:
                return None
            
            response = requests.post(
                f"{ollama.base_url}/api/generate",
                json={
                    "model": ollama.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,  # Moins créatif, plus précis
                        "num_predict": 400
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_code = result.get("response", "").strip()
                
                # Nettoyer le code avec la nouvelle fonction
                clean_code = self._clean_code(raw_code)
                
                return clean_code if clean_code else raw_code
            else:
                print(f"[FILE_MANAGER] Erreur génération code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[FILE_MANAGER] Erreur génération: {e}")
            return None
            
    def execute_action(self, command_json: Dict[str, Any]) -> str:
        """Exécute l'action demandée"""
        action = command_json.get("action", "")
        logical_file = command_json.get("fichier", "")
        target_path = command_json.get("chemin", "")
        instruction = command_json.get("instruction", "")
        file_type = command_json.get("type_fichier", "")
        
        print(f"[FILE_MANAGER] Action: {action}, Fichier: {logical_file}")
        
        # Utiliser le dernier fichier si pas de nom spécifié
        if not logical_file and self.last_file_logical:
            logical_file = self.last_file_logical
            file_path = self.last_path_found
        else:
            file_path = self.find_file(logical_file)
        
        # Actions de création/modification de code
        if action in ["modifier_code", "creer"]:
            if not instruction:
                return "❌ Aucune instruction pour générer le code."

            # Ajout automatique de l'extension si manquante
            filename = logical_file
            if file_type and not filename.lower().endswith(f".{file_type.lower()}"):
                filename = f"{filename}.{file_type.lower()}"

            code = self.generate_code(instruction, file_type)
            if not code:
                return "❌ Impossible de générer le code."

            # Définir le chemin pour création
            if action == "creer":
                target_dir = os.path.join(self.base_directory, target_path) if target_path else self.base_directory
                os.makedirs(target_dir, exist_ok=True)
                file_path = os.path.join(target_dir, filename)
            elif not file_path:
                return f"❌ Aucun fichier trouvé correspondant à : '{logical_file}'"

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)

                self.last_file_logical = filename
                self.last_path_found = file_path

                action_text = "créé" if action == "creer" else "modifié"
                return f"📄 Fichier {action_text} : {os.path.basename(file_path)}"

            except Exception as e:
                return f"❌ Erreur d'écriture : {e}"
        
        # Vérifier que le fichier existe pour les autres actions
        if not file_path:
            return f"❌ Aucun fichier trouvé correspondant à : '{logical_file}'"
        
        self.last_file_logical = logical_file
        self.last_path_found = file_path
        
        # Exécuter selon l'action
        if action == "lancer" or action == "ouvrir":
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                else:  # Linux/Mac
                    subprocess.Popen(['xdg-open', file_path])
                return f"🚀 Ouverture de : {os.path.basename(file_path)}"
            except Exception as e:
                return f"❌ Impossible d'ouvrir le fichier : {e}"
        
        elif action == "déplacer":
            if not target_path:
                return "❌ Chemin de destination non précisé."
            
            try:
                destination_dir = os.path.join(self.base_directory, target_path)
                os.makedirs(destination_dir, exist_ok=True)
                
                new_path = os.path.join(destination_dir, os.path.basename(file_path))
                shutil.move(file_path, new_path)
                
                self.last_path_found = new_path
                return f"📁 Fichier déplacé vers : {target_path}"
                
            except Exception as e:
                return f"❌ Erreur déplacement : {e}"
        
        elif action == "supprimer":
            try:
                os.remove(file_path)
                return f"🗑️ Fichier supprimé : {os.path.basename(file_path)}"
            except Exception as e:
                return f"❌ Erreur suppression : {e}"
        
        else:
            return f"❓ Action inconnue : {action}"
    
    def process_command(self, command: str) -> str:
        """Traite une commande complète en langage naturel"""
        print(f"[FILE_MANAGER] Commande reçue: {command}")
        
        # Analyser la commande
        command_json = self.analyze_command(command)
        if not command_json:
            return "❌ Impossible de comprendre la commande."
        
        print(f"[FILE_MANAGER] Analyse: {command_json}")
        
        # Exécuter l'action
        result = self.execute_action(command_json)
        print(f"[FILE_MANAGER] Résultat: {result}")
        
        return result
    
    def list_files(self, subdirectory: str = "") -> str:
        """Liste les fichiers dans un sous-dossier"""
        target_dir = os.path.join(self.base_directory, subdirectory) if subdirectory else self.base_directory

        if not os.path.exists(target_dir):
            return f"❌ Dossier non trouvé : {subdirectory}"

        files = []
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isfile(item_path):
                files.append(f"📄 {item}")
            elif os.path.isdir(item_path):
                files.append(f"📁 {item}/")

        if not files:
            return f"📂 Dossier vide : {subdirectory or 'racine'}"

        return f"📂 Contenu de {subdirectory or 'racine'} :\n" + "\n".join(files[:10])  # Limiter à 10 items


# Instance globale
file_manager = FileManager()