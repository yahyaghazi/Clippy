"""
Gestionnaire de fichiers avancé avec toutes les fonctionnalités Clippy
"""

import os
import json
import shutil
import re
import subprocess
import requests
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
import schedule
import dateparser

# Imports pour fonctionnalités avancées
try:
    from fpdf import FPDF
    from PIL import Image
    from bs4 import BeautifulSoup
    from duckduckgo_search import DDGS
    from urllib.parse import urlparse
    import fitz  # PyMuPDF
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    print("⚠️ Fonctionnalités avancées non disponibles - installez : pip install fpdf2 pillow beautifulsoup4 duckduckgo-search pymupdf")

try:
    from odf.opendocument import OpenDocumentText
    from odf.style import Style, TextProperties, ParagraphProperties
    from odf.text import P
    ODT_SUPPORT = True
except ImportError:
    ODT_SUPPORT = False

from ..config.settings import settings


class EnhancedFileManager:
    """Gestionnaire de fichiers intelligent avec toutes les fonctionnalités"""
    
    def __init__(self, base_directory: str = None):
        self.base_directory = base_directory or str(Path.home() / "Documents" / "AI_Assistant_Files")
        self.last_file_logical = None
        self.last_path_found = None
        
        # Système de rappels
        self.rappels = []
        self.historique_path = os.path.join(self.base_directory, "historique.json")
        
        # Configuration Ollama
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = settings.ollama.model
        self.model_general = "deepseek-coder-v2:16b"  # Modèle pour tâches créatives
        
        # Créer les dossiers nécessaires
        Path(self.base_directory).mkdir(parents=True, exist_ok=True)
        
        # Démarrer le système de rappels
        self._start_reminder_system()
        
        print(f"[ENHANCED_FILE_MANAGER] Dossier de base: {self.base_directory}")
        print(f"[ENHANCED_FILE_MANAGER] Fonctionnalités avancées: {'✅' if ADVANCED_FEATURES else '❌'}")
    
    def _start_reminder_system(self):
        """Démarre le système de rappels en arrière-plan"""
        def reminder_loop():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        threading.Thread(target=reminder_loop, daemon=True).start()
    
    def analyze_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Analyse une commande avec toutes les actions supportées"""
        prompt = f"""
Tu es un assistant IA local. Transforme la commande en français d'un utilisateur en JSON structuré.

Tu dois répondre avec un JSON **bien formé** et **sans aucune explication** contenant :
- "action" : doit être l'une des valeurs suivantes :
    • "lancer" – pour exécuter un fichier ou une app
    • "déplacer" – pour déplacer un fichier dans un dossier
    • "modifier_code" – pour remplacer le code d'un fichier existant
    • "creer" – pour créer un fichier avec un contenu spécifique
    • "webscrap_pdf" – rechercher un sujet sur le web et créer un PDF
    • "resumer_document" – résumer un document existant
    • "generer_document" – générer une lettre/document professionnel
    • "historique" – afficher l'historique des commandes
    • "traduire" – traduire un texte
    • "corriger" – corriger l'orthographe/grammaire
    • "ajouter_rappel" – programmer un rappel
    • "liste_fichiers" – lister les fichiers d'un dossier

- "fichier" : nom logique donné par l'utilisateur (ex : 'rapport IA', 'doc scraping')
- "chemin" : chemin relatif de destination (optionnel)
- "instruction" : contenu/sujet/texte selon l'action

⚠️ Réponds uniquement avec un JSON valide. Aucune explication.

Exemples :
- "crée un script python qui calcule les nombres premiers" → {{"action": "creer", "fichier": "nombres_premiers.py", "chemin": "python", "instruction": "script qui calcule et affiche les nombres premiers jusqu'à 100"}}
- "résume le document rapport.pdf" → {{"action": "resumer_document", "fichier": "rapport", "chemin": "", "instruction": ""}}
- "cherche des infos sur l'IA et fais un PDF" → {{"action": "webscrap_pdf", "fichier": "rapport_ia.pdf", "chemin": "recherches", "instruction": "intelligence artificielle"}}
- "génère une lettre de motivation pour développeur" → {{"action": "generer_document", "fichier": "lettre_motivation.odt", "chemin": "documents", "instruction": "lettre de motivation pour poste de développeur Python"}}

Commande : {command}
"""
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 200}
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                return self._extract_json(text)
            else:
                print(f"[ENHANCED_FILE_MANAGER] Erreur API: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[ENHANCED_FILE_MANAGER] Erreur analyse: {e}")
            return None
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extrait le JSON de la réponse"""
        match = re.search(r'\{[\s\S]+\}', text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as e:
                print(f"[ENHANCED_FILE_MANAGER] JSON mal formé: {e}")
        return None
    
    def find_file(self, logical_name: str) -> Optional[str]:
        """Recherche intelligente de fichier"""
        if not logical_name:
            return None
        
        keywords = logical_name.lower().split()
        candidates = []
        
        for root, dirs, files in os.walk(self.base_directory):
            for file in files:
                file_lower = file.lower()
                if all(keyword in file_lower for keyword in keywords):
                    candidates.append(os.path.join(root, file))
        
        return candidates[0] if candidates else None
    
    def generate_code(self, instruction: str, file_type: str = "") -> Optional[str]:
        """Génère du code avec l'IA"""
        language_hints = {
            "py": "Python", "js": "JavaScript", "html": "HTML",
            "css": "CSS", "java": "Java", "cpp": "C++"
        }
        
        language = language_hints.get(file_type.lower(), "")
        
        prompt = f"""
Tu es un expert en programmation. Génère UNIQUEMENT le code pour cette consigne, sans aucune explication :

Consigne : {instruction}
Langage : {language}

IMPORTANT :
- Réponds UNIQUEMENT avec le code
- Aucune explication avant, pendant ou après
- Pas de balises markdown
- Code prêt à être exécuté

Code :"""

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.5, "num_predict": 400}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_code = result.get("response", "").strip()
                return self._clean_code(raw_code)
            else:
                print(f"[ENHANCED_FILE_MANAGER] Erreur génération: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[ENHANCED_FILE_MANAGER] Erreur: {e}")
            return None
    
    def _clean_code(self, raw_code: str) -> str:
        """Nettoie le code généré"""
        code = raw_code.strip()
        
        # Supprimer les balises markdown
        if '```' in code:
            code = re.sub(r'^```[a-z]*\n?', '', code, flags=re.MULTILINE)
            code = re.sub(r'\n?```$', '', code, flags=re.MULTILINE)
        
        # Supprimer les préfixes d'explication
        prefixes = ["Voici le code :", "Code :", "Résultat :"]
        for prefix in prefixes:
            if code.startswith(prefix):
                code = code[len(prefix):].strip()
        
        return code.strip()
    
    # === NOUVELLES FONCTIONNALITÉS AVANCÉES ===
    
    def webscrap_and_create_pdf(self, query: str, filename: str) -> str:
        """Recherche web et création de PDF"""
        if not ADVANCED_FEATURES:
            return "❌ Fonctionnalités de webscraping non disponibles"
        
        try:
            # Clarification automatique du sujet
            clarified_query = self._clarify_query(query)
            print(f"🔍 Recherche sur : {clarified_query}")
            
            # Recherche web
            with DDGS() as ddgs:
                results = ddgs.text(clarified_query, region="fr-fr", max_results=10) or []
            
            # URLs à scraper
            urls = [f"https://fr.wikipedia.org/wiki/{clarified_query.replace(' ', '_')}"]
            urls += [r.get("href") or r.get("url") for r in results if (r.get("href") or r.get("url"))][:4]
            
            # Scraping du contenu
            content = ""
            valid_urls = []
            
            for url in urls:
                try:
                    if not url.startswith("http"):
                        continue
                    
                    r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                    soup = BeautifulSoup(r.text, "html.parser")
                    paragraphs = soup.find_all("p")
                    text = "\n".join(p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40)
                    
                    if text:
                        content += f"\n\n### Source : {url}\n{text}"
                        valid_urls.append(url)
                        
                except Exception as e:
                    print(f"⚠️ Erreur scraping {url}: {e}")
            
            if not content.strip():
                return "❌ Aucun contenu récupéré du web"
            
            # Résumé avec IA
            summary = self._generate_summary(content, clarified_query)
            
            # Création du PDF
            pdf_path = os.path.join(self.base_directory, filename)
            self._create_styled_pdf(summary, valid_urls, clarified_query, pdf_path)
            
            return f"📄 PDF créé avec succès : {pdf_path}"
            
        except Exception as e:
            return f"❌ Erreur webscraping : {e}"
    
    def _clarify_query(self, query: str) -> str:
        """Clarifie un sujet flou"""
        prompt = f"""
Tu es un assistant intelligent qui ne parle uniquement en français.

« {query} »

Réponds uniquement par une courte reformulation, sans introduction.
Exemples :
- « f1 » → « Formule 1 (sport automobile) »
- « ia » → « intelligence artificielle »
- « python » → « langage de programmation Python »
"""
        
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.model_general, "prompt": prompt, "stream": False},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()["response"].strip()
        except:
            pass
        
        return query  # Fallback
    
    def _generate_summary(self, content: str, topic: str) -> str:
        """Génère un résumé structuré"""
        prompt = f"""
Tu vas résumer des textes web sur : **{topic}**

Ta mission :
- Résume en un texte fluide et cohérent
- Structure avec des titres clairs
- Ton pédagogique et informatif
- Commence par un titre principal, introduction, sections, conclusion

Contenu :
{content}
"""
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_general,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"].strip()
        except Exception as e:
            print(f"Erreur résumé : {e}")
        
        return f"Résumé sur {topic}\n\n" + content[:2000] + "..."
    
    def _create_styled_pdf(self, summary: str, urls: list, topic: str, output_path: str):
        """Crée un PDF stylé"""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # En-tête
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, f"Rapport sur {topic.title()}", ln=True, align="C")
        pdf.ln(10)
        
        # Contenu principal
        pdf.set_font("Arial", "", 12)
        for line in summary.split('\n'):
            if line.strip():
                pdf.multi_cell(0, 10, line.strip())
        
        pdf.ln(10)
        
        # Sources
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 10, "Sources utilisées :", ln=True)
        pdf.set_font("Arial", "", 11)
        for url in urls:
            pdf.multi_cell(0, 10, f"- {url}")
        
        pdf.output(output_path)
    
    def summarize_document(self, file_path: str) -> str:
        """Résume un document local"""
        if not ADVANCED_FEATURES:
            return "❌ Fonction de résumé non disponible"
        
        try:
            text = ""
            
            if file_path.endswith(".pdf"):
                with fitz.open(file_path) as doc:
                    text = "\n".join(page.get_text() for page in doc)
            elif file_path.endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif file_path.endswith(".docx"):
                try:
                    import docx
                    doc = docx.Document(file_path)
                    text = "\n".join(p.text for p in doc.paragraphs)
                except ImportError:
                    return "❌ Support .docx non disponible (pip install python-docx)"
            else:
                return "❌ Format de fichier non supporté"
            
            if not text.strip():
                return "❌ Aucun texte trouvé dans le document"
            
            # Résumé avec IA
            prompt = f"Résume ce document de façon claire et structurée :\n{text[:3000]}"
            response = requests.post(
                self.ollama_url,
                json={"model": self.model_general, "prompt": prompt, "stream": False},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return "❌ Erreur lors du résumé"
                
        except Exception as e:
            return f"❌ Erreur : {e}"
    
    def generate_document(self, instruction: str, output_path: str) -> str:
        """Génère un document professionnel"""
        if not ODT_SUPPORT:
            # Fallback en TXT
            prompt = f"Rédige un document professionnel basé sur : {instruction}"
            try:
                response = requests.post(
                    self.ollama_url,
                    json={"model": self.model_general, "prompt": prompt, "stream": False},
                    timeout=30
                )
                
                if response.status_code == 200:
                    content = response.json()["response"]
                    with open(output_path.replace('.odt', '.txt'), 'w', encoding='utf-8') as f:
                        f.write(content)
                    return f"📄 Document TXT généré : {output_path.replace('.odt', '.txt')}"
            except Exception as e:
                return f"❌ Erreur génération : {e}"
        
        try:
            # Génération du contenu
            prompt = f"Rédige un document professionnel sans mentionner l'IA : {instruction}"
            response = requests.post(
                self.ollama_url,
                json={"model": self.model_general, "prompt": prompt, "stream": False},
                timeout=30
            )
            
            if response.status_code != 200:
                return "❌ Erreur génération contenu"
            
            content = response.json()["response"]
            
            # Création ODT
            doc = OpenDocumentText()
            
            body_style = Style(name="Body", family="paragraph")
            body_style.addElement(ParagraphProperties(margintop="0.2cm", marginbottom="0.2cm"))
            body_style.addElement(TextProperties(attributes={"fontsize": "12pt"}))
            doc.styles.addElement(body_style)
            
            for line in content.splitlines():
                if line.strip():
                    doc.text.addElement(P(stylename=body_style, text=line.strip()))
            
            odt_path = output_path.replace('.txt', '.odt')
            doc.save(odt_path)
            return f"📄 Document ODT généré : {odt_path}"
            
        except Exception as e:
            return f"❌ Erreur génération ODT : {e}"
    
    def translate_or_correct(self, text: str, action: str) -> str:
        """Traduit ou corrige un texte"""
        action_word = "Traduis en français" if action == "traduire" else "Corrige l'orthographe et la grammaire de"
        prompt = f"{action_word} ce texte :\n{text}"
        
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.model_general, "prompt": prompt, "stream": False},
                timeout=20
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return "❌ Erreur de traitement"
                
        except Exception as e:
            return f"❌ Erreur : {e}"
    
    def add_reminder(self, instruction: str) -> str:
        """Ajoute un rappel programmé"""
        try:
            # Analyser la date avec dateparser
            date = dateparser.parse(
                instruction,
                settings={"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.now()},
                languages=["fr"]
            )
            
            if not date:
                return "❌ Date non reconnue dans l'instruction"
            
            def alert():
                print(f"🔔 RAPPEL : {instruction}")
                # Ici on pourrait déclencher une notification système
            
            schedule.every().day.at(date.strftime("%H:%M")).do(alert)
            self.rappels.append({"date": date.isoformat(), "text": instruction})
            
            return f"⏰ Rappel programmé pour {date.strftime('%d/%m/%Y à %H:%M')}"
            
        except Exception as e:
            return f"❌ Erreur programmation rappel : {e}"
    
    def save_to_history_fixed(self, command: str, json_result: Dict[str, Any]):
        """Version corrigée de save_to_history avec gestion d'erreurs complète"""
        print(f"[HISTORY DEBUG] === DEBUT SAUVEGARDE ===")
        print(f"[HISTORY DEBUG] Commande: {command}")
        print(f"[HISTORY DEBUG] JSON: {json_result}")
        print(f"[HISTORY DEBUG] Chemin historique: {self.historique_path}")
        
        try:
            # Vérifier et créer le dossier de base
            base_dir = os.path.dirname(self.historique_path)
            if not os.path.exists(base_dir):
                print(f"[HISTORY DEBUG] Création du dossier: {base_dir}")
                os.makedirs(base_dir, exist_ok=True)
            
            # Créer l'entrée avec plus d'informations
            entry = {
                "id": self._generate_entry_id(),
                "timestamp": datetime.now().isoformat(),
                "date_readable": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "command": command,
                "action": json_result.get("action", "unknown"),
                "fichier": json_result.get("fichier", ""),
                "chemin": json_result.get("chemin", ""),
                "instruction": json_result.get("instruction", ""),
                "success": not str(json_result).startswith("❌"),
                "details": json_result
            }
            print(f"[HISTORY DEBUG] Entrée créée: {entry}")
            
            # Charger l'historique existant avec gestion d'erreurs
            history = []
            if os.path.exists(self.historique_path):
                try:
                    with open(self.historique_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            history = json.loads(content)
                            if not isinstance(history, list):
                                print("[HISTORY WARNING] Le fichier n'est pas une liste, création d'une nouvelle")
                                history = []
                        else:
                            print("[HISTORY DEBUG] Fichier vide, création d'une nouvelle liste")
                            history = []
                except json.JSONDecodeError as e:
                    print(f"[HISTORY ERROR] JSON corrompu: {e}")
                    # Créer un backup du fichier corrompu
                    backup_path = f"{self.historique_path}.corrupted.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    try:
                        import shutil
                        shutil.copy2(self.historique_path, backup_path)
                        print(f"[HISTORY DEBUG] Backup créé: {backup_path}")
                    except:
                        pass
                    history = []
                except Exception as e:
                    print(f"[HISTORY ERROR] Erreur lecture: {e}")
                    history = []
            else:
                print("[HISTORY DEBUG] Fichier n'existe pas, création d'une nouvelle liste")
            
            print(f"[HISTORY DEBUG] Historique chargé: {len(history)} entrées")
            
            # Ajouter la nouvelle entrée
            history.append(entry)
            
            # Limiter à 100 entrées (garder les plus récentes)
            if len(history) > 100:
                history = history[-100:]
                print(f"[HISTORY DEBUG] Historique tronqué à 100 entrées")
            
            # Sauvegarder avec vérification
            print(f"[HISTORY DEBUG] Sauvegarde de {len(history)} entrées...")
            
            # Écriture atomique (écrire dans un fichier temporaire puis renommer)
            temp_path = f"{self.historique_path}.tmp"
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
                
                # Vérifier que le fichier temporaire est valide
                with open(temp_path, 'r', encoding='utf-8') as f:
                    test_load = json.load(f)
                    if not isinstance(test_load, list):
                        raise ValueError("Le fichier sauvegardé n'est pas une liste valide")
                
                # Remplacer l'ancien fichier
                if os.path.exists(self.historique_path):
                    os.remove(self.historique_path)
                os.rename(temp_path, self.historique_path)
                
                print(f"[HISTORY DEBUG] ✅ Sauvegarde réussie ({len(history)} entrées)")
                
                # Vérification finale
                final_size = os.path.getsize(self.historique_path)
                print(f"[HISTORY DEBUG] Taille fichier final: {final_size} bytes")
                
            except Exception as write_error:
                print(f"[HISTORY ERROR] Erreur écriture: {write_error}")
                # Nettoyer le fichier temporaire en cas d'erreur
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                raise
                
        except Exception as e:
            print(f"[HISTORY ERROR] Erreur générale: {e}")
            print(f"[HISTORY ERROR] Type: {type(e)}")
            import traceback
            print(f"[HISTORY ERROR] Traceback: {traceback.format_exc()}")
            return False
        
        print(f"[HISTORY DEBUG] === FIN SAUVEGARDE ===")
        return True
    
    def _generate_entry_id(self) -> str:
        """Génère un ID unique pour une entrée"""
        import hashlib
        timestamp = datetime.now().isoformat()
        command_hash = hashlib.md5(f"{timestamp}".encode()).hexdigest()[:8]
        return command_hash

    def get_history_fixed(self, limit: int = 10) -> str:
        """Version corrigée de get_history avec plus de diagnostics"""
        print(f"[HISTORY DEBUG] === LECTURE HISTORIQUE ===")
        print(f"[HISTORY DEBUG] Chemin: {self.historique_path}")
        print(f"[HISTORY DEBUG] Limite: {limit}")
        
        try:
            # Vérifier existence du fichier
            if not os.path.exists(self.historique_path):
                print(f"[HISTORY DEBUG] Fichier n'existe pas")
                return "📋 Aucun historique enregistré (fichier inexistant)"
            
            # Vérifier taille du fichier
            file_size = os.path.getsize(self.historique_path)
            print(f"[HISTORY DEBUG] Taille fichier: {file_size} bytes")
            
            if file_size == 0:
                return "📋 Fichier d'historique vide"
            
            # Lire le contenu
            with open(self.historique_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[HISTORY DEBUG] Contenu lu: {len(content)} caractères")
                print(f"[HISTORY DEBUG] Aperçu: {content[:200]}...")
            
            # Parser le JSON
            try:
                history = json.loads(content)
                print(f"[HISTORY DEBUG] JSON parsé: {type(history)}")
            except json.JSONDecodeError as e:
                print(f"[HISTORY ERROR] JSON invalide: {e}")
                return f"❌ Fichier d'historique corrompu: {e}"
            
            if not isinstance(history, list):
                print(f"[HISTORY ERROR] Pas une liste: {type(history)}")
                return "❌ Format d'historique invalide"
            
            print(f"[HISTORY DEBUG] Nombre d'entrées: {len(history)}")
            
            if not history:
                return "📋 Historique vide"
            
            # Prendre les dernières entrées
            recent_entries = history[-limit:] if len(history) > limit else history
            print(f"[HISTORY DEBUG] Entrées récentes: {len(recent_entries)}")
            
            # Formater pour l'affichage
            result = f"📋 Historique des commandes ({len(recent_entries)}/{len(history)}):\n\n"
            
            for i, entry in enumerate(reversed(recent_entries)):  # Plus récent en premier
                print(f"[HISTORY DEBUG] Traitement entrée {i}: {entry}")
                
                date = entry.get("date_readable", entry.get("timestamp", "Date inconnue"))
                if len(date) > 19:
                    date = date[:19]
                
                command = entry.get("command", "Commande inconnue")
                if len(command) > 60:
                    command = command[:57] + "..."
                
                action = entry.get("action", "unknown")
                fichier = entry.get("fichier", "")
                
                # Icône selon l'action
                icons = {
                    "creer": "📝",
                    "lancer": "🚀", 
                    "modifier_code": "✏️",
                    "webscrap_pdf": "🌐",
                    "generer_document": "📄",
                    "liste_fichiers": "📁",
                    "historique": "📋",
                    "traduire": "🔤",
                    "resumer_document": "📖"
                }
                icon = icons.get(action, "🔧")
                
                result += f"{icon} {date}\n"
                result += f"   → {command}\n"
                if fichier:
                    result += f"   📄 {fichier}\n"
                result += "\n"
            
            print(f"[HISTORY DEBUG] Résultat formaté: {len(result)} caractères")
            return result
            
        except Exception as e:
            print(f"[HISTORY ERROR] Erreur lecture: {e}")
            import traceback
            print(f"[HISTORY ERROR] Traceback: {traceback.format_exc()}")
            return f"❌ Erreur lecture historique: {e}"
    
    def list_files(self, subdirectory: str = "") -> str:
        """Liste les fichiers"""
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
            
            return f"📂 Contenu de {subdirectory or 'racine'} :\n" + "\n".join(items[:20])
            
        except Exception as e:
            return f"❌ Erreur listage : {e}"
    
    def execute_action(self, command_json: Dict[str, Any]) -> str:
        """Exécute l'action demandée avec toutes les fonctionnalités"""
        action = command_json.get("action", "")
        logical_file = command_json.get("fichier", "")
        target_path = command_json.get("chemin", "")
        instruction = command_json.get("instruction", "")
        
        print(f"[ENHANCED_FILE_MANAGER] Action: {action}, Fichier: {logical_file}")
        
        # Actions avancées
        if action == "webscrap_pdf":
            if not instruction:
                return "❌ Sujet de recherche manquant"
            return self.webscrap_and_create_pdf(instruction, logical_file or "recherche.pdf")
        
        elif action == "resumer_document":
            file_path = self.find_file(logical_file)
            if not file_path:
                return f"❌ Document '{logical_file}' non trouvé"
            return self.summarize_document(file_path)
        
        elif action == "generer_document":
            if not instruction:
                return "❌ Instructions manquantes pour la génération"
            
            target_dir = os.path.join(self.base_directory, target_path) if target_path else self.base_directory
            os.makedirs(target_dir, exist_ok=True)
            output_path = os.path.join(target_dir, logical_file or "document.odt")
            
            return self.generate_document(instruction, output_path)
        
        elif action in ["traduire", "corriger"]:
            if not instruction:
                return f"❌ Texte manquant pour {action}"
            return self.translate_or_correct(instruction, action)
        
        elif action == "ajouter_rappel":
            if not instruction:
                return "❌ Instructions manquantes pour le rappel"
            return self.add_reminder(instruction)
        
        elif action == "historique":
            return self.get_history()
        
        elif action == "liste_fichiers":
            return self.list_files(target_path)
        
        # Actions standard (code original)
        elif action in ["modifier_code", "creer"]:
            if not instruction:
                return "❌ Aucune instruction pour générer le code"
            
            # Détecter extension
            file_type = ""
            if "." in logical_file:
                file_type = logical_file.split(".")[-1]
            
            code = self.generate_code(instruction, file_type)
            if not code:
                return "❌ Impossible de générer le code"
            
            if action == "creer":
                target_dir = os.path.join(self.base_directory, target_path) if target_path else self.base_directory
                os.makedirs(target_dir, exist_ok=True)
                file_path = os.path.join(target_dir, logical_file)
            else:
                file_path = self.find_file(logical_file)
                if not file_path:
                    return f"❌ Fichier '{logical_file}' non trouvé"
            
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                self.last_file_logical = logical_file
                self.last_path_found = file_path
                
                action_text = "créé" if action == "creer" else "modifié"
                return f"📄 Fichier {action_text} : {os.path.basename(file_path)}"
                
            except Exception as e:
                return f"❌ Erreur d'écriture : {e}"
        
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
        
        elif action == "déplacer":
            file_path = self.find_file(logical_file)
            if not file_path:
                return f"❌ Fichier '{logical_file}' non trouvé"
            
            if not target_path:
                return "❌ Destination non précisée"
            
            try:
                destination_dir = os.path.join(self.base_directory, target_path)
                os.makedirs(destination_dir, exist_ok=True)
                
                new_path = os.path.join(destination_dir, os.path.basename(file_path))
                shutil.move(file_path, new_path)
                
                self.last_path_found = new_path
                return f"📁 Fichier déplacé vers : {target_path}"
                
            except Exception as e:
                return f"❌ Erreur déplacement : {e}"
        
        else:
            return f"❓ Action inconnue : {action}"
    
    def process_command(self, command: str) -> str:
        """Traite une commande complète avec historique"""
        print(f"[ENHANCED_FILE_MANAGER] Commande reçue: {command}")
        
        # Analyser la commande
        command_json = self.analyze_command(command)
        if not command_json:
            return "❌ Impossible de comprendre la commande"
        
        print(f"[ENHANCED_FILE_MANAGER] Analyse: {command_json}")
        
        # Sauvegarder dans l'historique
        self.save_to_history(command, command_json)
        
        # Exécuter l'action
        result = self.execute_action(command_json)
        print(f"[ENHANCED_FILE_MANAGER] Résultat: {result}")
        
        return result
    
    def diagnostic_historique_complete(self):
        """Diagnostic complet du système d'historique"""
        print("\n" + "="*60)
        print("🔍 DIAGNOSTIC COMPLET DE L'HISTORIQUE")
        print("="*60)
        
        # 1. Informations de base
        print("📁 Informations de base:")
        print(f"   Dossier base: {self.base_directory}")
        print(f"   Chemin historique: {self.historique_path}")
        print(f"   Dossier existe: {os.path.exists(self.base_directory)}")
        print(f"   Fichier existe: {os.path.exists(self.historique_path)}")
        
        # 2. Permissions
        print("\n🔐 Permissions:")
        try:
            print(f"   Lecture dossier: {os.access(self.base_directory, os.R_OK)}")
            print(f"   Écriture dossier: {os.access(self.base_directory, os.W_OK)}")
            if os.path.exists(self.historique_path):
                print(f"   Lecture fichier: {os.access(self.historique_path, os.R_OK)}")
                print(f"   Écriture fichier: {os.access(self.historique_path, os.W_OK)}")
        except Exception as e:
            print(f"   ❌ Erreur vérification permissions: {e}")
        
        # 3. Contenu du fichier
        if os.path.exists(self.historique_path):
            print("\n📄 Analyse du fichier:")
            try:
                file_size = os.path.getsize(self.historique_path)
                print(f"   Taille: {file_size} bytes")
                
                with open(self.historique_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"   Contenu longueur: {len(content)} caractères")
                    print(f"   Aperçu: {content[:100]}...")
                    
                    if content.strip():
                        try:
                            data = json.loads(content)
                            print(f"   ✅ JSON valide: {type(data)}")
                            if isinstance(data, list):
                                print(f"   Nombre d'entrées: {len(data)}")
                                if data:
                                    print(f"   Première entrée: {data[0]}")
                                    print(f"   Dernière entrée: {data[-1]}")
                            else:
                                print(f"   ⚠️ Pas une liste: {type(data)}")
                        except json.JSONDecodeError as e:
                            print(f"   ❌ JSON invalide: {e}")
                    else:
                        print("   ⚠️ Fichier vide")
                        
            except Exception as e:
                print(f"   ❌ Erreur lecture: {e}")
        
        # 4. Test de sauvegarde
        print("\n🧪 Test de sauvegarde:")
        try:
            test_command = "test diagnostic"
            test_json = {"action": "test", "fichier": "diagnostic.txt", "instruction": "test"}
            
            print("   Tentative de sauvegarde...")
            result = self.save_to_history(test_command, test_json)
            print(f"   Résultat: {'✅ Succès' if result else '❌ Échec'}")
            
            # Vérifier que ça a marché
            if os.path.exists(self.historique_path):
                with open(self.historique_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if test_command in content:
                        print("   ✅ Test retrouvé dans le fichier")
                    else:
                        print("   ❌ Test non retrouvé dans le fichier")
            
        except Exception as e:
            print(f"   ❌ Erreur test: {e}")
        
        # 5. Test de lecture
        print("\n📖 Test de lecture:")
        try:
            result = self.get_history(3)
            print(f"   Longueur résultat: {len(result)} caractères")
            print(f"   Aperçu: {result[:200]}...")
            if "diagnostic" in result:
                print("   ✅ Test retrouvé dans l'historique")
            else:
                print("   ⚠️ Test non retrouvé dans l'historique")
        except Exception as e:
            print(f"   ❌ Erreur lecture: {e}")
        
        print("="*60)
        print("🏁 Fin du diagnostic")


# Instance globale
enhanced_file_manager = EnhancedFileManager()