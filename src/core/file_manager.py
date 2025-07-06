"""
Gestionnaire de fichiers avec IA pour l'Assistant
Version simplifiée et stable
"""

import os
import json
import shutil
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote
import time

from ..config.settings import settings


class FileManager:
    """Gestionnaire de fichiers intelligent avec IA"""
    
    def __init__(self, base_directory: str = None):
        self.base_directory = base_directory or str(Path.home() / "Documents" / "AI_Assistant_Files")
        self.last_file_logical = None
        self.last_path_found = None
        
        # Créer le dossier de base s'il n'existe pas
        Path(self.base_directory).mkdir(parents=True, exist_ok=True)
        
        print(f"[FILE_MANAGER] Dossier de base: {self.base_directory}")
        
    def analyze_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Analyse une commande en langage naturel avec l'IA"""
        prompt = f"""
Tu es un assistant IA spécialisé dans la gestion de fichiers. Analyse cette commande en français et retourne un JSON structuré.

Actions possibles :
- "creer" : créer un nouveau fichier avec du contenu
- "modifier_code" : modifier le code d'un fichier existant
- "lancer" : ouvrir/exécuter un fichier
- "deplacer" : déplacer un fichier
- "supprimer" : supprimer un fichier
- "lister" : lister les fichiers
- "generer_pdf" : créer un rapport PDF sur un sujet

Format de réponse JSON requis :
{{
    "action": "action_choisie",
    "fichier": "nom_du_fichier.extension",
    "chemin": "dossier_destination",
    "instruction": "contenu_ou_sujet_a_traiter",
    "type_fichier": "extension"
}}

⚠️ Réponds UNIQUEMENT avec le JSON, aucune explication.

Exemples :
- "crée un script python qui affiche bonjour" → {{"action": "creer", "fichier": "bonjour.py", "chemin": "python", "instruction": "script qui affiche bonjour monde", "type_fichier": "py"}}
- "génère un PDF sur l'intelligence artificielle" → {{"action": "generer_pdf", "fichier": "rapport_ia.pdf", "chemin": "documents", "instruction": "intelligence artificielle", "type_fichier": "pdf"}}
- "lance le fichier test" → {{"action": "lancer", "fichier": "test", "chemin": "", "instruction": "", "type_fichier": ""}}

Commande à analyser : {command}
"""
        
        try:
            # Utiliser le client Ollama existant
            from .ollama_client import OllamaClient
            ollama = OllamaClient()
            
            if not ollama.available:
                print("[FILE_MANAGER] Ollama non disponible - analyse basique")
                return self._basic_analysis(command)
            
            response = requests.post(
                f"{ollama.base_url}/api/generate",
                json={
                    "model": ollama.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,  # Plus déterministe
                        "num_predict": 150
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                parsed = self._extract_json(text)
                return parsed if parsed else self._basic_analysis(command)
            else:
                print(f"[FILE_MANAGER] Erreur API: {response.status_code}")
                return self._basic_analysis(command)
                
        except Exception as e:
            print(f"[FILE_MANAGER] Erreur analyse: {e}")
            return self._basic_analysis(command)
    
    def _basic_analysis(self, command: str) -> Dict[str, Any]:
        """Analyse basique sans IA"""
        command_lower = command.lower()
        
        # Détection par mots-clés
        if any(word in command_lower for word in ["crée", "créer", "génère", "nouveau"]):
            if "pdf" in command_lower or "rapport" in command_lower:
                return {
                    "action": "generer_pdf",
                    "fichier": "rapport.pdf",
                    "chemin": "documents",
                    "instruction": command,
                    "type_fichier": "pdf"
                }
            elif "python" in command_lower or ".py" in command_lower:
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
        
        elif any(word in command_lower for word in ["lance", "ouvre", "exécute"]):
            # Extraire le nom de fichier
            words = command.split()
            filename = words[-1] if words else "fichier"
            return {
                "action": "lancer",
                "fichier": filename,
                "chemin": "",
                "instruction": "",
                "type_fichier": ""
            }
        
        elif any(word in command_lower for word in ["liste", "affiche"]):
            return {
                "action": "lister",
                "fichier": "",
                "chemin": "",
                "instruction": "",
                "type_fichier": ""
            }
        
        # Par défaut
        return {
            "action": "creer",
            "fichier": "document.txt",
            "chemin": "",
            "instruction": command,
            "type_fichier": "txt"
        }
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extrait le JSON de la réponse de l'IA"""
        try:
            # Chercher le JSON dans le texte
            match = re.search(r'\{[^}]+\}', text)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"[FILE_MANAGER] JSON mal formé: {e}")
        
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
        
        return candidates[0] if candidates else None
    
    def generate_code(self, instruction: str, file_type: str = "") -> Optional[str]:
        """Génère du code avec l'IA selon les instructions"""
        language_hints = {
            "py": "Python",
            "js": "JavaScript", 
            "html": "HTML",
            "css": "CSS",
            "java": "Java",
            "cpp": "C++"
        }
        
        language = language_hints.get(file_type.lower(), "")
        
        prompt = f"""
Génère UNIQUEMENT le code pour cette demande, sans explication :

Demande : {instruction}
Langage : {language}

IMPORTANT :
- Réponds SEULEMENT avec le code
- Pas d'explication avant ou après
- Pas de balises markdown
- Code prêt à utiliser

Code :"""

        try:
            from .ollama_client import OllamaClient
            ollama = OllamaClient()
            
            if not ollama.available:
                return self._generate_basic_code(instruction, file_type)
            
            response = requests.post(
                f"{ollama.base_url}/api/generate",
                json={
                    "model": ollama.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,
                        "num_predict": 300
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_code = result.get("response", "").strip()
                
                # Nettoyer le code
                clean_code = self._clean_code(raw_code)
                return clean_code if clean_code else self._generate_basic_code(instruction, file_type)
            else:
                print(f"[FILE_MANAGER] Erreur génération code: {response.status_code}")
                return self._generate_basic_code(instruction, file_type)
                
        except Exception as e:
            print(f"[FILE_MANAGER] Erreur génération: {e}")
            return self._generate_basic_code(instruction, file_type)
    
    def _generate_basic_code(self, instruction: str, file_type: str) -> str:
        """Génère du code basique sans IA"""
        if file_type.lower() == "py":
            return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{instruction}
"""

def main():
    print("Hello World!")
    # TODO: Implémenter {instruction}

if __name__ == "__main__":
    main()
'''
        elif file_type.lower() == "html":
            return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Web</title>
</head>
<body>
    <h1>Ma Page Web</h1>
    <p>Contenu généré pour : {instruction}</p>
</body>
</html>
'''
        elif file_type.lower() == "js":
            return f'''// {instruction}

function main() {{
    console.log("Hello World!");
    // TODO: Implémenter {instruction}
}}

main();
'''
        else:
            return f"# {instruction}\n\n# Code généré automatiquement\n# TODO: Implémenter la fonctionnalité demandée"
    
    def _clean_code(self, raw_code: str) -> str:
        """Nettoie le code généré par l'IA"""
        code = raw_code.strip()
        
        # Supprimer les balises markdown
        if '```' in code:
            code = re.sub(r'^```[a-z]*\n?', '', code, flags=re.MULTILINE)
            code = re.sub(r'\n?```, ', code, flags=re.MULTILINE)
        
        # Supprimer les préfixes d'explication
        prefixes = [
            "Voici le code :", "Code :", "Résultat :", "Voici :",
            "Voici un exemple :", "Exemple :"
        ]
        for prefix in prefixes:
            if code.startswith(prefix):
                code = code[len(prefix):].strip()
        
        return code.strip()
    
    def generate_pdf_report(self, topic: str, filename: str) -> str:
        """Génère un rapport PDF sur un sujet"""
        try:
            # Vérifier si fpdf est disponible
            try:
                from fpdf import FPDF
            except ImportError:
                return "❌ Module PDF non disponible (pip install fpdf2)"
            
            print(f"📄 Génération PDF sur : {topic}")
            
            # Générer le contenu avec l'IA
            content = self._generate_report_content(topic)
            
            # Créer le PDF
            pdf_path = os.path.join(self.base_directory, "documents", filename)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            pdf = FPDF()
            pdf.add_page()
            
            # En-tête
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Rapport : {topic.title()}", ln=True, align="C")
            pdf.ln(5)
            
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", ln=True, align="C")
            pdf.ln(10)
            
            # Contenu
            pdf.set_font("Arial", "", 12)
            for line in content.split('\n'):
                if line.strip():
                    if line.isupper() or line.startswith('#'):
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
            
            return f"📄 PDF créé avec succès : {pdf_path}"
            
        except Exception as e:
            return f"❌ Erreur génération PDF : {e}"
    
    def _generate_report_content(self, topic: str) -> str:
        """Génère le contenu d'un rapport"""
        prompt = f"""
Rédige un rapport structuré et informatif sur : {topic}

Structure du rapport :
1. INTRODUCTION
2. POINTS PRINCIPAUX  
3. APPLICATIONS PRATIQUES
4. AVANTAGES ET LIMITES
5. CONCLUSION

Sois informatif, clair et structuré. Utilise un ton professionnel.
"""
        
        try:
            from .ollama_client import OllamaClient
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
            print(f"Erreur génération contenu: {e}")
        
        # Contenu de fallback
        return f"""# RAPPORT SUR {topic.upper()}

## INTRODUCTION
Ce rapport présente une analyse de {topic}.

## POINTS PRINCIPAUX
- Concept et définition
- Fonctionnement général
- Caractéristiques importantes

## APPLICATIONS PRATIQUES
- Utilisations courantes
- Exemples concrets
- Domaines d'application

## AVANTAGES ET LIMITES
Avantages :
- Efficacité
- Polyvalence
- Innovation

Limites :
- Complexité
- Coûts
- Défis techniques

## CONCLUSION
{topic} représente un domaine important avec de nombreuses applications et perspectives d'évolution.
"""
    
    def execute_action(self, command_json: Dict[str, Any]) -> str:
        """Exécute l'action demandée"""
        action = command_json.get("action", "")
        logical_file = command_json.get("fichier", "")
        target_path = command_json.get("chemin", "")
        instruction = command_json.get("instruction", "")
        file_type = command_json.get("type_fichier", "")
        
        print(f"[FILE_MANAGER] Action: {action}, Fichier: {logical_file}")
        
        # Générer un PDF
        if action == "generer_pdf":
            if not instruction:
                return "❌ Sujet manquant pour le PDF"
            return self.generate_pdf_report(instruction, logical_file or "rapport.pdf")
        
        # Créer ou modifier du code
        elif action in ["creer", "modifier_code"]:
            if not instruction:
                return "❌ Instructions manquantes"
            
            # Générer le code
            code = self.generate_code(instruction, file_type)
            if not code:
                return "❌ Impossible de générer le code"
            
            # Définir le chemin
            if action == "creer":
                target_dir = os.path.join(self.base_directory, target_path) if target_path else self.base_directory
                os.makedirs(target_dir, exist_ok=True)
                file_path = os.path.join(target_dir, logical_file)
            else:
                file_path = self.find_file(logical_file)
                if not file_path:
                    return f"❌ Fichier '{logical_file}' non trouvé"
            
            # Écrire le fichier
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                self.last_file_logical = logical_file
                self.last_path_found = file_path
                
                action_text = "créé" if action == "creer" else "modifié"
                return f"📄 Fichier {action_text} : {os.path.basename(file_path)}"
                
            except Exception as e:
                return f"❌ Erreur écriture : {e}"
        
        # Lancer un fichier
        elif action == "lancer":
            file_path = self.find_file(logical_file)
            if not file_path:
                return f"❌ Fichier '{logical_file}' non trouvé"
            
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                else:  # Linux/Mac
                    subprocess.Popen(['xdg-open', file_path])
                return f"🚀 Ouverture de : {os.path.basename(file_path)}"
            except Exception as e:
                return f"❌ Impossible d'ouvrir : {e}"
        
        # Déplacer un fichier
        elif action == "deplacer":
            file_path = self.find_file(logical_file)
            if not file_path:
                return f"❌ Fichier '{logical_file}' non trouvé"
            
            if not target_path:
                return "❌ Destination manquante"
            
            try:
                destination_dir = os.path.join(self.base_directory, target_path)
                os.makedirs(destination_dir, exist_ok=True)
                
                new_path = os.path.join(destination_dir, os.path.basename(file_path))
                shutil.move(file_path, new_path)
                
                self.last_path_found = new_path
                return f"📁 Fichier déplacé vers : {target_path}"
                
            except Exception as e:
                return f"❌ Erreur déplacement : {e}"
        
        # Lister les fichiers
        elif action == "lister":
            return self.list_files(target_path)
        
        # Supprimer un fichier
        elif action == "supprimer":
            file_path = self.find_file(logical_file)
            if not file_path:
                return f"❌ Fichier '{logical_file}' non trouvé"
            
            try:
                os.remove(file_path)
                return f"🗑️ Fichier supprimé : {os.path.basename(file_path)}"
            except Exception as e:
                return f"❌ Erreur suppression : {e}"
        
        else:
            return f"❓ Action inconnue : {action}"
    
    def list_files(self, subdirectory: str = "") -> str:
        """Liste les fichiers dans un dossier"""
        target_dir = os.path.join(self.base_directory, subdirectory) if subdirectory else self.base_directory
        
        if not os.path.exists(target_dir):
            return f"❌ Dossier non trouvé : {subdirectory}"
        
        try:
            items = []
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isfile(item_path):
                    items.append(f"📄 {item}")
                elif os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
            
            if not items:
                return f"📂 Dossier vide : {subdirectory or 'racine'}"
            
            return f"📂 Contenu de {subdirectory or 'racine'} :\n" + "\n".join(items[:15])
            
        except Exception as e:
            return f"❌ Erreur listage : {e}"
    
    def process_command(self, command: str) -> str:
        """Traite une commande complète"""
        print(f"[FILE_MANAGER] Commande reçue: {command}")
        
        # Analyser la commande
        command_json = self.analyze_command(command)
        if not command_json:
            return "❌ Impossible de comprendre la commande"
        
        print(f"[FILE_MANAGER] Analyse: {command_json}")
        
        # Exécuter l'action
        result = self.execute_action(command_json)
        print(f"[FILE_MANAGER] Résultat: {result}")
        
        return result

    def scrape_wikipedia_content(self, topic: str) -> str:
        """Scrape Wikipedia pour obtenir du contenu frais sur un sujet"""
        try:
            print(f"🌐 Recherche Wikipedia sur : {topic}")
            
            # URLs Wikipedia à essayer
            urls_to_try = [
                f"https://fr.wikipedia.org/wiki/{quote(topic.replace(' ', '_'))}",
                f"https://fr.wikipedia.org/wiki/{quote(topic)}",
                f"https://en.wikipedia.org/wiki/{quote(topic.replace(' ', '_'))}"
            ]
            
            scraped_content = ""
            
            for url in urls_to_try:
                try:
                    print(f"📖 Tentative : {url}")
                    
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    
                    response = requests.get(url, timeout=10, headers=headers)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extraire le contenu principal de Wikipedia
                    content_div = soup.find('div', {'id': 'mw-content-text'})
                    if not content_div:
                        continue
                    
                    # Extraire les paragraphes
                    paragraphs = content_div.find_all('p')
                    
                    for p in paragraphs[:10]:  # Prendre les 10 premiers paragraphes
                        text = p.get_text().strip()
                        if len(text) > 50:  # Ignorer les paragraphes trop courts
                            scraped_content += text + "\n\n"
                    
                    if scraped_content:
                        print(f"✅ Contenu récupéré depuis : {url}")
                        break
                        
                    time.sleep(1)  # Pause respectueuse entre requêtes
                    
                except Exception as e:
                    print(f"⚠️ Erreur pour {url}: {e}")
                    continue
            
            if not scraped_content:
                print("❌ Aucun contenu Wikipedia trouvé")
                return f"Informations sur {topic} (contenu de base généré par IA)"
            
            return scraped_content.strip()
            
        except Exception as e:
            print(f"❌ Erreur web scraping : {e}")
            return f"Recherche sur {topic} (erreur d'accès web)"


    def generate_pdf_with_wikipedia(self, topic: str, filename: str) -> str:
        """Génère un PDF avec du contenu Wikipedia réel"""
        try:
            print(f"📄 Génération PDF avec Wikipedia : {topic}")
            
            # 1. Scraper Wikipedia
            wikipedia_content = self.scrape_wikipedia_content(topic)
            
            # 2. Enrichir avec l'IA pour structurer
            enriched_content = self._enhance_content_with_ai(wikipedia_content, topic)
            
            # 3. Créer le PDF
            pdf_path = os.path.join(self.base_directory, "documents", filename)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            
            # En-tête
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Rapport Wikipedia : {topic.title()}", ln=True, align="C")
            pdf.ln(5)
            
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, f"Source : Wikipédia - Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", ln=True, align="C")
            pdf.ln(10)
            
            # Contenu
            pdf.set_font("Arial", "", 12)
            
            # Diviser en sections
            sections = enriched_content.split('\n\n')
            for section in sections:
                if section.strip():
                    # Détecter les titres (lignes courtes en majuscules)
                    if len(section) < 100 and section.isupper():
                        pdf.set_font("Arial", "B", 12)
                        pdf.ln(5)
                        pdf.multi_cell(0, 8, section.strip())
                        pdf.ln(2)
                        pdf.set_font("Arial", "", 12)
                    else:
                        pdf.multi_cell(0, 6, section.strip())
                        pdf.ln(2)
            
            # Sources
            pdf.ln(10)
            pdf.set_font("Arial", "I", 10)
            pdf.multi_cell(0, 6, f"Sources : Wikipédia (fr.wikipedia.org), enrichi par IA locale")
            pdf.cell(0, 10, "Document généré par Clippy IA avec web scraping", ln=True, align="C")
            
            pdf.output(pdf_path)
            
            return f"📄 PDF Wikipedia créé : {pdf_path}"
            
        except Exception as e:
            return f"❌ Erreur génération PDF Wikipedia : {e}"


    def _enhance_content_with_ai(self, raw_content: str, topic: str) -> str:
        """Utilise l'IA pour structurer le contenu Wikipedia"""
        prompt = f"""
    Tu reçois du contenu brut de Wikipedia sur "{topic}".

    Réorganise ce contenu de manière claire et structurée :
    1. INTRODUCTION (résumé en 2-3 phrases)
    2. HISTOIRE (chronologie si applicable)
    3. CARACTÉRISTIQUES PRINCIPALES
    4. IMPORTANCE/IMPACT
    5. INFORMATIONS PRATIQUES (si applicable)

    Garde les faits exacts, améliore juste la structure.

    Contenu Wikipedia :
    {raw_content[:2000]}  # Limiter pour éviter les timeouts

    Contenu structuré :"""
        
        try:
            from .ollama_client import OllamaClient
            ollama = OllamaClient()
            
            if ollama.available:
                response = requests.post(
                    f"{ollama.base_url}/api/generate",
                    json={
                        "model": ollama.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.3, "num_predict": 800}
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    structured_content = response.json().get("response", "")
                    return structured_content if structured_content else raw_content
        
        except Exception as e:
            print(f"Erreur structuration IA : {e}")
        
        return raw_content  # Fallback au contenu brut


# Instance globale
file_manager = FileManager()