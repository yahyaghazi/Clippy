"""
Point d'entrée principal de l'Assistant Clippy IA Moderne
Version corrigée et optimisée
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
from src.core.enhanced_file_manager import EnhancedFileManager
from src.ui.main_window import MainWindow
from src.config.settings import settings
from src.utils.logger import setup_logger


def check_dependencies():
    """Vérifie que les dépendances critiques sont installées"""
    missing_deps = []
    optional_missing = []
    
    # Dépendances critiques
    critical_deps = [
        ("psutil", "psutil"),
        ("requests", "requests"),
        ("tkinter", "tkinter (inclus avec Python)")
    ]
    
    for module_name, pip_name in critical_deps:
        try:
            if module_name == "tkinter":
                import tkinter
            else:
                __import__(module_name)
        except ImportError:
            missing_deps.append(pip_name)
    
    # Dépendances optionnelles
    optional_deps = [
        ("PIL", "Pillow"),
        ("fpdf", "fpdf2"),
        ("pyttsx3", "pyttsx3"),
        ("speech_recognition", "SpeechRecognition")
    ]
    
    for module_name, pip_name in optional_deps:
        try:
            __import__(module_name)
        except ImportError:
            optional_missing.append(pip_name)
    
    # Affichage des résultats
    if missing_deps:
        print("❌ Dépendances critiques manquantes:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print(f"\nInstallez avec: pip install {' '.join([d for d in missing_deps if d != 'tkinter (inclus avec Python)'])}")
        return False
    
    if optional_missing:
        print("⚠️ Dépendances optionnelles manquantes (fonctionnalités limitées):")
        for dep in optional_missing:
            print(f"   - {dep}")
        print("L'assistant fonctionnera avec les fonctionnalités de base.\n")
    
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
            
            # Vérifier le modèle configuré
            model_names = [m["name"] for m in models]
            if settings.ollama.model in model_names:
                print(f"✅ Modèle '{settings.ollama.model}' prêt")
            else:
                print(f"⚠️ Modèle '{settings.ollama.model}' non trouvé")
                if model_names:
                    print("Modèles disponibles:", model_names[:3])
                print(f"Téléchargez avec: ollama pull {settings.ollama.model}")
            
            return True
        else:
            print("❌ Ollama répond mais avec erreur")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama non accessible sur http://localhost:11434")
        print("Démarrez Ollama avec: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Erreur vérification Ollama: {e}")
        return False


def setup_directories():
    """Crée les dossiers nécessaires"""
    base_dir = Path.home() / "Documents" / "AI_Assistant_Files"
    subdirs = ["python", "html", "documents", "recherches", "backup"]
    
    for subdir in subdirs:
        (base_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Dossiers créés dans: {base_dir}")


def show_startup_info():
    """Affiche les informations de démarrage"""
    print("="*60)
    print("📎 ASSISTANT CLIPPY IA MODERNE")
    print("="*60)
    print("🤖 Version simplifiée et stable")
    print("🎯 Fonctionnalités disponibles:")
    print("   • 💬 Chat intelligent avec IA")
    print("   • 📁 Gestion de fichiers")
    print("   • 🎤 Reconnaissance vocale (si disponible)")
    print("   • 🔊 Synthèse vocale")
    print("   • 🔍 Surveillance des applications")
    print("   • 📄 Génération de documents")
    print("="*60)


def main():
    """Fonction principale"""
    show_startup_info()
    
    print("🚀 Démarrage de Clippy...")
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Impossible de démarrer sans les dépendances critiques")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    # Configurer les logs
    logger = setup_logger("clippy_ai")
    logger.info("Clippy IA démarré")
    
    # Vérifier Ollama (non bloquant)
    ollama_ok = check_ollama()
    if not ollama_ok:
        print("⚠️ Clippy fonctionnera en mode limité sans IA")
        print("Démarrez Ollama pour toutes les fonctionnalités")
    
    # Créer les dossiers
    setup_directories()
    
    print("\n🎉 Lancement de l'interface...")
    
    try:
        # Créer et lancer la fenêtre principale
        app = MainWindow()
        app.run()
        
    except KeyboardInterrupt:
        print("\n🔄 Arrêt demandé par l'utilisateur")
        logger.info("Arrêt demandé par l'utilisateur")
        
    except ImportError as e:
        print(f"\n❌ Erreur d'import: {e}")
        print("Vérifiez l'installation des dépendances")
        logger.error(f"Erreur d'import: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        logger.error(f"Erreur fatale: {e}", exc_info=True)
        
        # Afficher des infos de debug en mode développement
        if settings.debug_mode:
            import traceback
            traceback.print_exc()
        
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    finally:
        logger.info("Clippy IA arrêté")
        print("👋 Au revoir ! Clippy s'arrête.")

def patch_enhanced_file_manager():
    """Patch rapide pour tester le fix"""
    from src.core.enhanced_file_manager import enhanced_file_manager
    
    # Remplacer les méthodes
    enhanced_file_manager.save_to_history = EnhancedFileManager.save_to_history_fixed.__get__(enhanced_file_manager)
    enhanced_file_manager.get_history = EnhancedFileManager.get_history_fixed.__get__(enhanced_file_manager)
    enhanced_file_manager._generate_entry_id = EnhancedFileManager._generate_entry_id.__get__(enhanced_file_manager)
    enhanced_file_manager.diagnostic_historique_complete = EnhancedFileManager.diagnostic_historique_complete.__get__(enhanced_file_manager)
    
    print("✅ Enhanced File Manager patché avec le fix d'historique")
    
    # Test immédiat
    enhanced_file_manager.diagnostic_historique_complete()
    
    return enhanced_file_manager

if __name__ == "__main__":
    # Pour tester le patch
    patched_manager = patch_enhanced_file_manager()
    
    # Test d'une commande
    result = patched_manager.process_command("crée un fichier test pour historique")
    print(f"\nRésultat test: {result}")
    
    # Vérifier l'historique
    print("\nHistorique après test:")
    print(patched_manager.get_history())