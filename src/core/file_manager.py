"""
Gestionnaire de fichiers avec IA et exécution - VERSION COMPLÈTE
"""

import os
import json
import shutil
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Any
import requests
from datetime import datetime

from ..config.settings import settings


class CodeExecutor:
    """Gestionnaire d'exécution de code sécurisé"""
    
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.running_processes = {}
        
    def execute_file(self, file_path: str) -> str:
        """Exécute un fichier selon son type"""
        if not os.path.exists(file_path):
            return f"❌ Fichier non trouvé: {file_path}"
        
        # Vérifications de sécurité
        security_check = self._security_check(file_path)
        if security_check:
            return security_check
        
        file_ext = Path(file_path).suffix.lower()
        filename = os.path.basename(file_path)
        
        print(f"[EXECUTOR] 🚀 Exécution de {filename} (type: {file_ext})")
        
        try:
            if file_ext == '.py':
                return self._execute_python(file_path)
            elif file_ext == '.js':
                return self._execute_javascript(file_path)
            elif file_ext == '.html':
                return self._open_in_browser(file_path)
            elif file_ext == '.bat':
                return self._execute_batch(file_path)
            elif file_ext in ['.txt', '.md']:
                return self._open_in_editor(file_path)
            else:
                return self._open_with_system(file_path)
                
        except Exception as e:
            return f"❌ Erreur d'exécution: {str(e)}"
    
    def _security_check(self, file_path: str) -> str:
        """Vérifications de sécurité avant exécution"""
        # Vérifier que le fichier est dans notre dossier autorisé
        try:
            file_path_resolved = Path(file_path).resolve()
            base_path_resolved = Path(self.base_directory).resolve()
            
            if not str(file_path_resolved).startswith(str(base_path_resolved)):
                return "❌ Erreur de sécurité: fichier hors du dossier autorisé"
        except Exception:
            return "❌ Erreur de sécurité: chemin invalide"
        
        # Vérifier la taille du fichier (max 5MB)
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 5 * 1024 * 1024:  # 5MB
                return "❌ Fichier trop volumineux (max 5MB)"
        except Exception:
            return "❌ Impossible de lire le fichier"
        
        return ""  # Pas d'erreur de sécurité
    
    def _execute_python(self, file_path: str) -> str:
        """Exécute un script Python"""
        try:
            # Utiliser le même interpréteur Python
            python_exe = sys.executable
            
            # Exécuter dans un processus séparé avec timeout
            result = subprocess.run(
                [python_exe, file_path],
                capture_output=True,
                text=True,
                timeout=30,  # Timeout de 30 secondes
                cwd=os.path.dirname(file_path)
            )
            
            output_parts = []
            
            if result.stdout:
                output_parts.append(f"📤 Sortie du programme:\n{result.stdout}")
            
            if result.stderr:
                output_parts.append(f"⚠️ Messages d'erreur:\n{result.stderr}")
            
            if result.returncode == 0:
                if output_parts:
                    return f"✅ Script Python exécuté avec succès!\n\n" + "\n\n".join(output_parts)
                else:
                    return "✅ Script Python exécuté avec succès! (aucune sortie)"
            else:
                return f"❌ Erreur d'exécution (code {result.returncode}):\n" + "\n".join(output_parts)
                
        except subprocess.TimeoutExpired:
            return "⏱️ Timeout: Le script a pris trop de temps (>30s)"
        except FileNotFoundError:
            return "❌ Python non trouvé sur le système"
        except Exception as e:
            return f"❌ Erreur d'exécution: {str(e)}"
    
    def _execute_javascript(self, file_path: str) -> str:
        """Exécute un script JavaScript avec Node.js"""
        try:
            # Essayer avec Node.js
            result = subprocess.run(
                ['node', file_path],
                capture_output=True,
                text=True,
                timeout=20,
                cwd=os.path.dirname(file_path)
            )
            
            if result.returncode == 0:
                output = result.stdout if result.stdout else "Script exécuté sans sortie"
                return f"✅ Script JavaScript exécuté!\n\n📤 Sortie:\n{output}"
            else:
                return f"❌ Erreur JavaScript:\n{result.stderr}"
                
        except FileNotFoundError:
            # Si Node.js n'est pas installé, ouvrir dans le navigateur
            return self._open_in_browser(file_path)
        except subprocess.TimeoutExpired:
            return "⏱️ Timeout JavaScript"
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def _open_in_browser(self, file_path: str) -> str:
        """Ouvre un fichier HTML dans le navigateur"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.Popen(['xdg-open', file_path])
            
            return f"✅ Fichier ouvert dans le navigateur:\n📄 {os.path.basename(file_path)}"
            
        except Exception as e:
            return f"❌ Impossible d'ouvrir le navigateur: {str(e)}"
    
    def _execute_batch(self, file_path: str) -> str:
        """Exécute un fichier batch (.bat)"""
        try:
            result = subprocess.run(
                [file_path],
                capture_output=True,
                text=True,
                timeout=15,
                shell=True,
                cwd=os.path.dirname(file_path)
            )
            
            output = ""
            if result.stdout:
                output += f"📤 Sortie:\n{result.stdout}"
            if result.stderr:
                output += f"\n⚠️ Erreurs:\n{result.stderr}"
            
            if result.returncode == 0:
                return f"✅ Script Batch exécuté!\n\n{output}"
            else:
                return f"❌ Erreur Batch (code {result.returncode}):\n{output}"
                
        except subprocess.TimeoutExpired:
            return "⏱️ Timeout Batch"
        except Exception as e:
            return f"❌ Erreur Batch: {str(e)}"
    
    def _open_in_editor(self, file_path: str) -> str:
        """Ouvre un fichier texte dans l'éditeur par défaut"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            else:  # Linux/Mac
                subprocess.Popen(['xdg-open', file_path])
            
            return f"✅ Fichier ouvert dans l'éditeur:\n📄 {os.path.basename(file_path)}"
            
        except Exception as e:
            return f"❌ Impossible d'ouvrir l'éditeur: {str(e)}"
    
    def _open_with_system(self, file_path: str) -> str:
        """Ouvre un fichier avec l'application système par défaut"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            else:  # Linux/Mac
                subprocess.Popen(['xdg-open', file_path])
            
            return f"✅ Fichier ouvert avec l'application par défaut:\n📄 {os.path.basename(file_path)}"
            
        except Exception as e:
            return f"❌ Impossible d'ouvrir le fichier: {str(e)}"


class FileManager:
    """Gestionnaire de fichiers intelligent avec IA et exécution"""
    
    def __init__(self, base_directory: str = None):
        self.base_directory = base_directory or str(Path.home() / "Documents" / "AI_Assistant_Files")
        self.last_file_logical = None
        self.last_path_found = None
        
        # Créer le dossier de base s'il n'existe pas
        Path(self.base_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialiser l'exécuteur
        self.executor = CodeExecutor(self.base_directory)
        
        print(f"[FILE_MANAGER] Dossier de base: {self.base_directory}")
        print(f"[FILE_MANAGER] Exécuteur de code initialisé")
    
    def analyze_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Analyse une commande en langage naturel avec détection d'exécution"""
        
        command_lower = command.lower()
        
        # 🔍 DÉTECTION DES COMMANDES D'EXÉCUTION
        execution_keywords = [
            "lance", "lancer", "exécute", "execute", "démarre", "demarrer", 
            "run", "ouvre", "ouvrir", "joue", "jouer", "teste", "tester"
        ]
        
        creation_keywords = [
            "crée", "créer", "génère", "générer", "écris", "fais", "code", "programme"
        ]
        
        # Détecter : "crée X et lance-le" ou "fais X et exécute"
        if any(create in command_lower for create in creation_keywords) and \
           any(execute in command_lower for execute in execution_keywords):
            return self._parse_create_and_run_command(command)
        
        # Détecter : "lance le fichier X" ou "exécute X"
        elif any(execute in command_lower for execute in execution_keywords):
            return self._parse_execution_command(command)
        
        # Commande de création simple
        elif any(create in command_lower for create in creation_keywords):
            return self._parse_creation_command(command)
        
        # Fallback vers l'analyse IA
        return self._analyze_with_ai(command)
    
    def _parse_create_and_run_command(self, command: str) -> Dict[str, Any]:
        """Parse une commande de création + exécution"""
        print("[FILE_MANAGER] 🔄 Commande création + exécution détectée")
        
        # Extraire la partie création (avant "et")
        if " et " in command.lower():
            creation_part = command.lower().split(" et ")[0]
        else:
            creation_part = command
        
        # Analyser la partie création
        creation_json = self._parse_creation_command(creation_part)
        if creation_json:
            creation_json["action"] = "creer_et_executer"
            return creation_json
        
        # Fallback
        return {
            "action": "creer_et_executer",
            "fichier": "script.py",
            "instruction": command,
            "type_fichier": "py",
            "chemin": "python"
        }
    
    def _parse_execution_command(self, command: str) -> Dict[str, Any]:
        """Parse une commande d'exécution"""
        print("[FILE_MANAGER] ▶️ Commande d'exécution détectée")
        
        # Patterns pour extraire le nom de fichier
        patterns = [
            r"(?:lance|exécute|ouvre|démarre|run|teste)\s+(?:le\s+fichier\s+)?([a-zA-Z0-9_.-]+)",
            r"(?:lance|exécute|ouvre|démarre|run|teste)\s+([a-zA-Z0-9_.-]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command.lower())
            if match:
                fichier = match.group(1)
                return {
                    "action": "lancer",
                    "fichier": fichier,
                    "instruction": "",
                    "type_fichier": "",
                    "chemin": ""
                }
        
        # Chercher un nom de fichier dans la commande
        words = command.split()
        for word in words:
            if "." in word and not word.startswith("http"):  # Probablement un nom de fichier
                return {
                    "action": "lancer",
                    "fichier": word,
                    "instruction": "",
                    "type_fichier": "",
                    "chemin": ""
                }
        
        # Fallback - chercher le dernier mot comme nom de fichier
        return {
            "action": "lancer",
            "fichier": words[-1] if words else "script",
            "instruction": "",
            "type_fichier": "",
            "chemin": ""
        }
    
    def _parse_creation_command(self, command: str) -> Dict[str, Any]:
        """Parse une commande de création"""
        command_lower = command.lower()

        # Déterminer le type de fichier
        if "python" in command_lower or ".py" in command_lower:
            file_type = "py"
            default_name = "script.py"
            default_path = "python"
        elif "html" in command_lower or "web" in command_lower or "page" in command_lower:
            file_type = "html"
            default_name = "page.html"
            default_path = "html"
        elif "javascript" in command_lower or ".js" in command_lower:
            file_type = "js"
            default_name = "script.js"
            default_path = "javascript"
        elif "pdf" in command_lower or "rapport" in command_lower:
            file_type = "pdf"
            default_name = "rapport.pdf"
            default_path = "documents"
        else:
            file_type = "py"  # Par défaut Python
            default_name = "script.py"
            default_path = "python"

        # ==== NOUVEAU : Demander un nom de fichier à l'IA ====
        ai_filename = None
        try:
            from ..core.ollama_client import OllamaClient
            ollama = OllamaClient()
            if ollama.available:
                prompt = (
                    f"Propose un nom de fichier court et pertinent (sans explication, juste le nom) "
                    f"pour ce projet {file_type} : \"{command}\". "
                    f"Le nom doit finir par .{file_type}."
                )
                response = requests.post(
                    f"{ollama.base_url}/api/generate",
                    json={
                        "model": ollama.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.1, "num_predict": 20}
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    text = response.json().get("response", "").strip()
                    # Nettoyer le nom (enlever code block, espaces, etc)
                    ai_filename = re.sub(r"[`\s]", "", text)
                    if not ai_filename.endswith(f".{file_type}"):
                        ai_filename += f".{file_type}"
        except Exception as e:
            print(f"[FILE_MANAGER] Erreur IA nom fichier: {e}")

        # Extraire un nom de fichier potentiel (fallback logique)
        filename = ai_filename or self._extract_filename_from_command(command, file_type) or default_name

        return {
            "action": "generer_pdf" if file_type == "pdf" else "creer",
            "fichier": filename,
            "instruction": command,
            "type_fichier": file_type,
            "chemin": default_path
        }
    
    def _extract_filename_from_command(self, command: str, file_type: str) -> Optional[str]:
        """Extrait un nom de fichier potentiel de la commande"""
        # Mots-clés qui peuvent indiquer un nom
        keywords = ["fibonacci", "calculatrice", "jeu", "test", "exemple", "demo"]
        
        command_lower = command.lower()
        for keyword in keywords:
            if keyword in command_lower:
                return f"{keyword}.{file_type}"
        
        return None
    
    def _analyze_with_ai(self, command: str) -> Optional[Dict[str, Any]]:
        """Analyse avec l'IA comme fallback"""
        prompt = f"""
Analyse cette commande et réponds avec un JSON valide :

Commande: "{command}"

Actions possibles: "creer", "lancer", "modifier_code", "supprimer", "lister", "generer_pdf", "creer_et_executer"

Format JSON uniquement:
{{
    "action": "action_choisie",
    "fichier": "nom_fichier.ext",
    "chemin": "dossier",
    "instruction": "description",
    "type_fichier": "py|html|js|txt"
}}

JSON:"""

        try:
            from ..core.ollama_client import OllamaClient
            ollama = OllamaClient()
            
            if not ollama.available:
                return self._basic_analysis(command)
            
            response = requests.post(
                f"{ollama.base_url}/api/generate",
                json={
                    "model": ollama.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 100}
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                return self._extract_json(text)
                
        except Exception as e:
            print(f"[FILE_MANAGER] Erreur analyse IA: {e}")
        
        return self._basic_analysis(command)
    
    def _basic_analysis(self, command: str) -> Dict[str, Any]:
        """Analyse basique sans IA"""
        command_lower = command.lower()
        
        if "python" in command_lower:
            return {
                "action": "creer",
                "fichier": "script.py",
                "chemin": "python",
                "instruction": command,
                "type_fichier": "py"
            }
        elif "html" in command_lower:
            return {
                "action": "creer",
                "fichier": "page.html",
                "chemin": "html", 
                "instruction": command,
                "type_fichier": "html"
            }
        else:
            return {
                "action": "creer",
                "fichier": "document.txt",
                "chemin": "",
                "instruction": command,
                "type_fichier": "txt"
            }
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extrait le JSON de la réponse"""
        try:
            match = re.search(r'\{[^}]+\}', text)
            if match:
                return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
        return None
    
    def find_file(self, logical_name: str) -> Optional[str]:
        """Recherche un fichier par son nom logique"""
        if not logical_name:
            return None
        
        # Nettoyer le nom de recherche
        search_terms = logical_name.lower().replace('.py', '').replace('.html', '').replace('.js', '').split()
        
        candidates = []
        
        # Parcourir récursivement le dossier de base
        for root, dirs, files in os.walk(self.base_directory):
            for file in files:
                file_lower = file.lower()
                
                # Correspondance exacte
                if logical_name.lower() == file_lower:
                    return os.path.join(root, file)
                
                # Correspondance partielle avec tous les termes
                if all(term in file_lower for term in search_terms):
                    candidates.append(os.path.join(root, file))
        
        # Retourner le premier candidat trouvé
        return candidates[0] if candidates else None
    
    def generate_code(self, instruction: str, file_type: str = "") -> Optional[str]:
        """Génère du code avec l'IA - VERSION UNIVERSELLE"""
        print(f"[FILE_MANAGER] 🤖 Génération de code: {instruction} (type: {file_type})")
        
        try:
            from ..core.ollama_client import OllamaClient
            ollama = OllamaClient()
            
            if not ollama.available:
                print("[FILE_MANAGER] ❌ Ollama non disponible")
                return self._generate_minimal_fallback(instruction, file_type)
            
            # Prompt universel optimisé
            prompt = self._create_universal_prompt(instruction, file_type)
            
            response = requests.post(
                f"{ollama.base_url}/api/generate",
                json={
                    "model": ollama.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 500,
                        "top_p": 0.95,
                        "repeat_penalty": 1.1,
                        "stop": ["```", "Explication:", "Note:", "Voici"]
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_code = result.get("response", "").strip()
                
                if raw_code and len(raw_code) > 30:
                    clean_code = self._clean_code_universal(raw_code, file_type)
                    
                    if self._validate_code_quality(clean_code, instruction, file_type):
                        print(f"[FILE_MANAGER] ✅ Code généré ({len(clean_code)} chars)")
                        return clean_code
                    else:
                        print("[FILE_MANAGER] ⚠️ Qualité insuffisante, nouvelle tentative...")
                        return self._retry_generation(instruction, file_type, ollama)
                else:
                    return self._retry_generation(instruction, file_type, ollama)
            
        except Exception as e:
            print(f"[FILE_MANAGER] ❌ Erreur génération: {e}")
        
        return self._generate_minimal_fallback(instruction, file_type)
    
    def _create_universal_prompt(self, instruction: str, file_type: str) -> str:
        """Crée un prompt universel pour la génération de code"""
        language_info = self._get_language_info(file_type)
        
        return f"""Tu es un expert programmeur {language_info['name']}.

TÂCHE: Écris un programme {language_info['name']} complet pour: "{instruction}"

EXIGENCES:
- Code complet et fonctionnel
- Directement exécutable
- Structure claire avec fonctions
- Commentaires utiles
- Interface utilisateur simple

FORMAT:
- Commence directement par le code
- Pas d'explication avant/après
- {language_info['start_indicator']}

CODE:"""
    
    def _get_language_info(self, file_type: str) -> Dict[str, str]:
        """Informations par langage"""
        configs = {
            "py": {
                "name": "Python",
                "start_indicator": "Commence par #!/usr/bin/env python3"
            },
            "js": {
                "name": "JavaScript",
                "start_indicator": "Commence par le code JavaScript"
            },
            "html": {
                "name": "HTML/CSS",
                "start_indicator": "Commence par <!DOCTYPE html>"
            }
        }
        
        return configs.get(file_type.lower(), {
            "name": "générique",
            "start_indicator": "Commence par le code"
        })
    
    def _retry_generation(self, instruction: str, file_type: str, ollama) -> Optional[str]:
        """Nouvelle tentative de génération"""
        retry_prompt = f"""URGENT: Code {file_type} fonctionnel pour: {instruction}

RÈGLES:
1. SEULEMENT du code exécutable
2. PAS d'explication
3. Code COMPLET

CODE:"""

        try:
            response = requests.post(
                f"{ollama.base_url}/api/generate",
                json={
                    "model": ollama.model,
                    "prompt": retry_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.05,
                        "num_predict": 400,
                        "stop": ["Explication", "Voici", "Note"]
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_code = result.get("response", "").strip()
                if raw_code:
                    return self._clean_code_universal(raw_code, file_type)
                    
        except Exception as e:
            print(f"[FILE_MANAGER] ❌ Erreur retry: {e}")
        
        return None
    
    def _clean_code_universal(self, raw_code: str, file_type: str) -> str:
        """Nettoyage universel du code"""
        if not raw_code:
            return ""
        
        # Supprimer les balises markdown
        code = re.sub(r'^```[a-zA-Z]*\n?', '', raw_code, flags=re.MULTILINE)
        code = re.sub(r'\n?```\s*$', '', code, flags=re.MULTILINE)
        
        # Supprimer les explications
        lines = code.split('\n')
        cleaned_lines = []
        code_started = False
        
        for line in lines:
            line_stripped = line.strip()
            
            if self._is_code_start(line_stripped, file_type):
                code_started = True
            
            if not code_started and self._is_explanation_line(line_stripped):
                continue
                
            if code_started and self._is_explanation_line(line_stripped) and not self._is_comment_line(line_stripped, file_type):
                break
            
            if code_started or not line_stripped:
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines).strip()
        return result if result else raw_code.strip()
    
    def _is_code_start(self, line: str, file_type: str) -> bool:
        """Détecte le début du code"""
        starters = {
            "py": ["#!/", "import ", "from ", "def ", "class ", "if __name__"],
            "js": ["function ", "const ", "let ", "var ", "class "],
            "html": ["<!DOCTYPE", "<html", "<head", "<body"]
        }
        
        return any(line.startswith(s) for s in starters.get(file_type.lower(), ["def", "function"]))
    
    def _is_explanation_line(self, line: str) -> bool:
        """Détecte les explications"""
        explanations = ["voici le code", "ce code", "explication", "utilisation"]
        return any(exp in line.lower() for exp in explanations)
    
    def _is_comment_line(self, line: str, file_type: str) -> bool:
        """Détecte les commentaires légitimes"""
        comment_chars = {
            "py": ["#", '"""', "'''"],
            "js": ["//", "/*"],
            "html": ["<!--"]
        }
        
        chars = comment_chars.get(file_type.lower(), ["#", "//"])
        return any(line.strip().startswith(char) for char in chars)
    
    def _validate_code_quality(self, code: str, instruction: str, file_type: str) -> bool:
        """Valide la qualité du code"""
        if not code or len(code) < 30:
            return False
        
        if "TODO" in code and len(code) < 100:
            return False
        
        # Vérifications par langage
        if file_type.lower() == "py":
            must_have = ["def ", "class ", "for ", "while ", "if ", "print("]
            if not any(item in code for item in must_have):
                return False
                
        return True
    
    def _generate_minimal_fallback(self, instruction: str, file_type: str) -> str:
        """Fallback minimal"""
        if file_type.lower() == "py":
            return f'''#!/usr/bin/env python3
"""
{instruction}
"""

def main():
    print("Programme: {instruction}")
    print("TODO: Code à implémenter")

if __name__ == "__main__":
    main()'''
        
        return f'// {instruction}\n// TODO: Implémentation nécessaire'
    
    def execute_action(self, command_json: Dict[str, Any]) -> str:
        """Exécute l'action demandée - VERSION COMPLÈTE AVEC EXÉCUTION"""
        action = command_json.get("action", "")
        logical_file = command_json.get("fichier", "")
        target_path = command_json.get("chemin", "")
        instruction = command_json.get("instruction", "")
        file_type = command_json.get("type_fichier", "")
        
        print(f"[FILE_MANAGER] 🎯 Action: {action} - Fichier: {logical_file}")
        
        # === NOUVELLES ACTIONS D'EXÉCUTION ===
        
        if action == "lancer":
            """Exécuter un fichier existant"""
            if not logical_file:
                return "❌ Nom de fichier manquant"
            
            file_path = self.find_file(logical_file)
            if not file_path:
                return f"❌ Fichier '{logical_file}' non trouvé dans {self.base_directory}"
            
            return self.executor.execute_file(file_path)
        
        elif action == "creer_et_executer":
            """Créer un fichier puis l'exécuter immédiatement"""
            # Étape 1: Créer le fichier
            create_result = self._create_file(logical_file, target_path, instruction, file_type)
            
            if "❌" in create_result:
                return create_result
            
            # Étape 2: Exécuter le fichier créé
            if self.last_path_found and os.path.exists(self.last_path_found):
                execution_result = self.executor.execute_file(self.last_path_found)
                return f"{create_result}\n\n🚀 EXÉCUTION:\n{execution_result}"
            else:
                return f"{create_result}\n❌ Impossible d'exécuter: fichier non créé"
        
        # === ACTIONS DE CRÉATION ===
        
        elif action in ["creer", "modifier_code"]:
            """Créer ou modifier un fichier"""
            return self._create_file(logical_file, target_path, instruction, file_type)
        
        elif action == "generer_pdf":
            """Générer un rapport PDF"""
            if not instruction:
                return "❌ Sujet manquant pour le PDF"
            return self._generate_pdf_report(instruction, logical_file or "rapport.pdf")
        
        elif action in ["resumer", "resumer_pdf"]:
            """Résumer un document PDF"""
            if not logical_file:
                return "❌ Nom de fichier PDF manquant"
            file_path = self.find_file(logical_file)
            if not file_path or not file_path.lower().endswith(".pdf"):
                return f"❌ Fichier PDF '{logical_file}' non trouvé"
            return self._summarize_pdf(file_path)
        
        # === AUTRES ACTIONS ===
        
        elif action == "lister":
            """Lister les fichiers"""
            return self._list_files(target_path)
        
        elif action == "supprimer":
            """Supprimer un fichier"""
            if not logical_file:
                return "❌ Nom de fichier manquant"
            
            file_path = self.find_file(logical_file)
            if not file_path:
                return f"❌ Fichier '{logical_file}' non trouvé"
            
            try:
                os.remove(file_path)
                return f"🗑️ Fichier supprimé: {os.path.basename(file_path)}"
            except Exception as e:
                return f"❌ Erreur suppression: {str(e)}"
        
        elif action == "deplacer":
            """Déplacer un fichier"""
            if not logical_file or not target_path:
                return "❌ Nom de fichier ou destination manquant"
            
            file_path = self.find_file(logical_file)
            if not file_path:
                return f"❌ Fichier '{logical_file}' non trouvé"
            
            try:
                destination_dir = os.path.join(self.base_directory, target_path)
                os.makedirs(destination_dir, exist_ok=True)
                
                new_path = os.path.join(destination_dir, os.path.basename(file_path))
                shutil.move(file_path, new_path)
                
                self.last_path_found = new_path
                return f"📁 Fichier déplacé vers: {target_path}"
                
            except Exception as e:
                return f"❌ Erreur déplacement: {str(e)}"
        
        else:
            return f"❓ Action inconnue: {action}"
    
    def _create_file(self, logical_file: str, target_path: str, instruction: str, file_type: str) -> str:
        """Logique de création de fichier centralisée"""
        if not instruction:
            return "❌ Instructions manquantes"
        
        # Générer le code
        print(f"[FILE_MANAGER] 📝 Génération du contenu...")
        code = self.generate_code(instruction, file_type)
        if not code:
            return "❌ Impossible de générer le code"
        
        # Déterminer le chemin de destination
        if target_path:
            target_dir = os.path.join(self.base_directory, target_path)
        else:
            # Dossiers par défaut selon le type
            if file_type == "py":
                target_dir = os.path.join(self.base_directory, "python")
            elif file_type == "html":
                target_dir = os.path.join(self.base_directory, "html")
            elif file_type == "js":
                target_dir = os.path.join(self.base_directory, "javascript")
            else:
                target_dir = self.base_directory
        
        # Créer le dossier si nécessaire
        os.makedirs(target_dir, exist_ok=True)
        
        # S'assurer que le fichier a la bonne extension
        if not logical_file.endswith(f".{file_type}"):
            logical_file = f"{logical_file}.{file_type}"
        
        file_path = os.path.join(target_dir, logical_file)
        
        try:
            # Écrire le fichier
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Mettre à jour les variables de suivi
            self.last_file_logical = logical_file
            self.last_path_found = file_path
            
            # Afficher un aperçu du code pour confirmation
            code_preview = code[:150] + "..." if len(code) > 150 else code
            
            return f"✅ Fichier créé: {logical_file}\n📁 Emplacement: {file_path}\n\n📝 Aperçu du code:\n{code_preview}"
            
        except Exception as e:
            return f"❌ Erreur lors de la création: {str(e)}"
    
    def _generate_pdf_report(self, topic: str, filename: str) -> str:
        """Génère un rapport PDF sur un sujet"""
        try:
            # Vérifier si fpdf est disponible
            try:
                from fpdf import FPDF
            except ImportError:
                return "❌ Module PDF non disponible (pip install fpdf2)"
            
            print(f"[FILE_MANAGER] 📄 Génération PDF sur: {topic}")
            
            # Générer le contenu avec l'IA
            content = self._generate_report_content(topic)
            
            # Créer le chemin du PDF
            pdf_dir = os.path.join(self.base_directory, "documents")
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_path = os.path.join(pdf_dir, filename)
            
            # Créer le PDF
            pdf = FPDF()
            pdf.add_page()
            
            # En-tête
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Rapport: {topic.title()}", ln=True, align="C")
            pdf.ln(5)
            
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", ln=True, align="C")
            pdf.ln(10)
            
            # Contenu
            pdf.set_font("Arial", "", 12)
            for line in content.split('\n'):
                if line.strip():
                    if line.startswith('#') or line.isupper():
                        # Titre
                        pdf.set_font("Arial", "B", 12)
                        pdf.ln(5)
                        pdf.multi_cell(0, 8, line.strip().replace('#', ''))
                        pdf.ln(2)
                        pdf.set_font("Arial", "", 12)
                    else:
                        # Texte normal
                        pdf.multi_cell(0, 6, line.strip())
                        pdf.ln(1)
            
            # Pied de page
            pdf.ln(10)
            pdf.set_font("Arial", "I", 8)
            pdf.cell(0, 10, "Document généré par Assistant IA", ln=True, align="C")
            
            pdf.output(pdf_path)
            
            self.last_path_found = pdf_path
            
            return f"📄 PDF créé avec succès: {filename}\n📁 Emplacement: {pdf_path}"
            
        except Exception as e:
            return f"❌ Erreur génération PDF: {str(e)}"
    
    def _generate_report_content(self, topic: str) -> str:
        """Génère le contenu d'un rapport"""
        prompt = f"""Rédige un rapport informatif et professionnel sur : {topic}

Tu es libre de structurer le texte comme tu le souhaites, sans contrainte de plan ou de sections imposées.
Le rapport doit être clair, cohérent et pertinent pour le sujet."""

        try:
            from ..core.ollama_client import OllamaClient
            ollama = OllamaClient()
            
            if ollama.available:
                response = requests.post(
                    f"{ollama.base_url}/api/generate",
                    json={
                        "model": ollama.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.7, "num_predict": 500}
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json().get("response", "")
        
        except Exception as e:
            print(f"[FILE_MANAGER] Erreur génération contenu: {e}")
        
        # Contenu de fallback
        return f"Rapport sur {topic}\n\n(Texte généré automatiquement. Sujet : {topic})"
    
    def _list_files(self, subdirectory: str = "") -> str:
        """Liste les fichiers dans un dossier"""
        target_dir = os.path.join(self.base_directory, subdirectory) if subdirectory else self.base_directory
        
        if not os.path.exists(target_dir):
            return f"❌ Dossier non trouvé: {subdirectory}"
        
        try:
            items = []
            file_count = 0
            dir_count = 0
            
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    size_str = f"{size} bytes" if size < 1024 else f"{size//1024} KB"
                    items.append(f"📄 {item} ({size_str})")
                    file_count += 1
                elif os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                    dir_count += 1
            
            if not items:
                return f"📂 Dossier vide: {subdirectory or 'racine'}"
            
            header = f"📂 Contenu de {subdirectory or 'racine'} ({file_count} fichiers, {dir_count} dossiers):\n"
            return header + "\n".join(items[:20])  # Limiter à 20 items
            
        except Exception as e:
            return f"❌ Erreur listage: {str(e)}"
    
    def process_command(self, command: str) -> str:
        """Traite une commande complète"""
        print(f"[FILE_MANAGER] 📥 Commande reçue: {command}")
        
        # Analyser la commande
        command_json = self.analyze_command(command)
        if not command_json:
            return "❌ Impossible de comprendre la commande"
        
        print(f"[FILE_MANAGER] 🧠 Analyse: {command_json}")
        
        # Exécuter l'action
        result = self.execute_action(command_json)
        print(f"[FILE_MANAGER] ✅ Résultat: {result[:100]}...")
        
        return result
    
    def get_stats(self) -> str:
        """Retourne les statistiques du gestionnaire de fichiers"""
        try:
            total_files = 0
            total_size = 0
            file_types = {}
            
            for root, dirs, files in os.walk(self.base_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        total_size += size
                        total_files += 1
                        
                        ext = Path(file).suffix.lower()
                        if ext:
                            file_types[ext] = file_types.get(ext, 0) + 1
                    except:
                        continue
            
            # Formater la taille
            if total_size < 1024:
                size_str = f"{total_size} bytes"
            elif total_size < 1024*1024:
                size_str = f"{total_size//1024} KB"
            else:
                size_str = f"{total_size//(1024*1024)} MB"
            
            # Top 5 des types de fichiers
            top_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]
            
            stats = f"""📊 Statistiques du gestionnaire de fichiers:

📁 Dossier de base: {self.base_directory}
📄 Total fichiers: {total_files}
💾 Taille totale: {size_str}
📂 Dernier fichier créé: {self.last_file_logical or "Aucun"}

📈 Types de fichiers les plus fréquents:"""
            
            for ext, count in top_types:
                stats += f"\n  {ext}: {count} fichiers"
            
            return stats
            
        except Exception as e:
            return f"❌ Erreur calcul statistiques: {str(e)}"


# Instance globale
file_manager = FileManager()