"""
Lanceur principal de l'Assistant Clippy IA Moderne
Version corrigée avec fix historique intégré
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.ui.main_window import MainWindow
from src.config.settings import settings
from src.utils.logger import setup_logger


def apply_enhanced_file_manager_patch():
    """Applique le patch corrigé pour l'historique - VERSION COMPLÈTE"""
    from src.core.enhanced_file_manager import enhanced_file_manager
    import json
    from datetime import datetime
    
    print("🔧 Application du patch historique COMPLET...")
    
    # Méthodes corrigées définies directement ici
    def save_to_history_fixed(self, command: str, json_result: dict):
        """Version corrigée de save_to_history avec logs"""
        print(f"[HISTORY SAVE] 💾 Sauvegarde: {command}")
        try:
            # Créer l'entrée
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
            
            # Charger l'historique existant
            history = []
            if os.path.exists(self.historique_path):
                try:
                    with open(self.historique_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            history = json.loads(content)
                            if not isinstance(history, list):
                                history = []
                except:
                    history = []
            
            # Ajouter et limiter
            history.append(entry)
            if len(history) > 100:
                history = history[-100:]
            
            # S'assurer que le dossier existe
            os.makedirs(os.path.dirname(self.historique_path), exist_ok=True)
            
            # Sauvegarder
            with open(self.historique_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            print(f"[HISTORY SAVE] ✅ Commande sauvegardée: {command[:50]}...")
            return True
        except Exception as e:
            print(f"[HISTORY SAVE] ❌ Erreur: {e}")
            return False
    
    def get_history_fixed(self, limit: int = 10):
        """Version corrigée de get_history"""
        try:
            if not os.path.exists(self.historique_path):
                return "📋 Aucun historique enregistré"
            
            with open(self.historique_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    return "📋 Historique vide"
            
            history = json.loads(content)
            if not isinstance(history, list) or not history:
                return "📋 Historique vide"
            
            recent_entries = history[-limit:]
            result = f"📋 Historique des commandes ({len(recent_entries)}/{len(history)}):\n\n"
            
            icons = {
                "creer": "📝", "lancer": "🚀", "modifier_code": "✏️",
                "webscrap_pdf": "🌐", "generer_document": "📄", 
                "liste_fichiers": "📁", "historique": "📋",
                "traduire": "🔤", "resumer_document": "📖",
                "generer_pdf": "📄"
            }
            
            for entry in reversed(recent_entries):
                date = entry.get("date_readable", "")[:19]
                command = entry.get("command", "")
                if len(command) > 60:
                    command = command[:57] + "..."
                
                action = entry.get("action", "")
                fichier = entry.get("fichier", "")
                icon = icons.get(action, "🔧")
                
                result += f"{icon} {date}\n   → {command}\n"
                if fichier:
                    result += f"   📄 {fichier}\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"❌ Erreur lecture historique: {e}"
    
    def generate_entry_id(self):
        """Génère un ID unique"""
        import hashlib
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{timestamp}_{len(str(timestamp))}".encode()).hexdigest()[:8]
    
    def process_command_fixed(self, command: str) -> str:
        """Version avec sauvegarde garantie - LE FIX PRINCIPAL"""
        print(f"[ENHANCED_FILE_MANAGER] 📥 Commande reçue: {command}")
        
        # Analyser la commande
        command_json = self.analyze_command(command)
        if not command_json:
            # Même en cas d'échec, sauvegarder
            error_json = {"action": "erreur", "fichier": "", "instruction": command}
            self.save_to_history(command, error_json)
            return "❌ Impossible de comprendre la commande"
        
        print(f"[ENHANCED_FILE_MANAGER] 🧠 Analyse: {command_json}")
        
        # ⭐ SAUVEGARDER AVANT L'EXÉCUTION - LE FIX PRINCIPAL! ⭐
        print(f"[ENHANCED_FILE_MANAGER] 💾 Sauvegarde en cours...")
        self.save_to_history(command, command_json)
        
        # Exécuter l'action
        result = self.execute_action(command_json)
        print(f"[ENHANCED_FILE_MANAGER] ✅ Résultat: {result[:100]}...")
        
        return result
    
    # Appliquer TOUS les patchs
    enhanced_file_manager.save_to_history = save_to_history_fixed.__get__(enhanced_file_manager)
    enhanced_file_manager.get_history = get_history_fixed.__get__(enhanced_file_manager)
    enhanced_file_manager._generate_entry_id = generate_entry_id.__get__(enhanced_file_manager)
    
    # ⭐ LE FIX PRINCIPAL - Remplacer process_command ⭐
    enhanced_file_manager.process_command = process_command_fixed.__get__(enhanced_file_manager)
    
    print("✅ Enhanced File Manager COMPLÈTEMENT patché avec fix d'historique!")
    
    # Test immédiat
    print("🧪 Test du patch...")
    test_result = enhanced_file_manager.process_command("test patch main_launcher")
    print(f"Test résultat: {test_result}")
    
    return enhanced_file_manager


def check_dependencies():
    """Vérifie les dépendances critiques"""
    missing_deps = []
    
    critical_deps = [("psutil", "psutil"), ("requests", "requests")]
    
    for module_name, pip_name in critical_deps:
        try:
            __import__(module_name)
        except ImportError:
            missing_deps.append(pip_name)
    
    if missing_deps:
        print("❌ Dépendances critiques manquantes:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print(f"\nInstallez avec: pip install {' '.join(missing_deps)}")
        return False
    
    print("✅ Dépendances principales vérifiées")
    return True


def check_ollama():
    """Vérifie la disponibilité d'Ollama"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama connecté - {len(models)} modèle(s) disponible(s)")
            return True
        else:
            print("❌ Ollama répond mais avec erreur")
            return False
    except:
        print("❌ Ollama non accessible - Démarrez avec: ollama serve")
        return False


def setup_directories():
    """Crée les dossiers nécessaires"""
    base_dir = Path.home() / "Documents" / "AI_Assistant_Files"
    subdirs = ["python", "html", "documents", "recherches", "backup"]
    
    for subdir in subdirs:
        (base_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Dossiers créés dans: {base_dir}")


def main():
    """Fonction principale"""
    print("="*60)
    print("📎 ASSISTANT CLIPPY IA MODERNE")
    print("="*60)
    print("🚀 Démarrage...")
    
    # Vérifications
    if not check_dependencies():
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    # Appliquer le patch pour l'historique
    patched_manager = apply_enhanced_file_manager_patch()
    
    # Fix supplémentaire pour les commandes d'historique
    original_analyze = patched_manager.analyze_command
    
    def analyze_command_with_history_fix(command: str):
        """Fix pour bien détecter les commandes d'historique"""
        command_lower = command.lower().strip()
        
        # Détecter historique en priorité
        if any(keyword in command_lower for keyword in [
            "affiche l'historique", "affiche historique", "historique", 
            "montre l'historique", "voir l'historique"
        ]):
            print("[FIX] Commande d'historique détectée")
            return {
                "action": "historique",
                "fichier": "",
                "chemin": "", 
                "instruction": ""
            }
        
        # Sinon, analyse normale
        return original_analyze(command)
    
    # Appliquer le fix
    patched_manager.analyze_command = analyze_command_with_history_fix
    print("✅ Fix commandes d'historique appliqué")
    
    # Configuration
    logger = setup_logger("clippy_ai")
    logger.info("Clippy IA démarré")
    
    # Vérifier Ollama (non bloquant)
    ollama_ok = check_ollama()
    if not ollama_ok:
        print("⚠️ Clippy fonctionnera en mode limité sans IA")
    
    # Créer dossiers
    setup_directories()
    
    print("\n🎉 Lancement de l'interface Clippy...")
    
    try:
        # Créer et lancer la fenêtre principale
        app = MainWindow()
        app.run()
        
    except KeyboardInterrupt:
        print("\n🔄 Arrêt demandé par l'utilisateur")
        
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        if settings.debug_mode:
            import traceback
            traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    finally:
        logger.info("Clippy IA arrêté")
        print("👋 Au revoir ! Clippy s'arrête.")


if __name__ == "__main__":
    main()