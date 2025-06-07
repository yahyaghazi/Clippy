"""
Point d'entrée principal de l'Assistant IA
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


def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    missing_deps = []
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    if missing_deps:
        print("❌ Dépendances manquantes:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstallez avec: pip install " + " ".join(missing_deps))
        return False
    
    return True


def main():
    """Fonction principale"""
    print("🚀 Démarrage de l'Assistant IA...")
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Configurer les logs
    logger = setup_logger()
    logger.info("Assistant IA démarré")
    
    try:
        # Créer et lancer la fenêtre principale
        app = MainWindow()
        app.run()
        
    except KeyboardInterrupt:
        print("\n🔄 Arrêt demandé par l'utilisateur")
        logger.info("Arrêt demandé par l'utilisateur")
        
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        logger.error(f"Erreur fatale: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        logger.info("Assistant IA arrêté")
        print("👋 Au revoir !")


if __name__ == "__main__":
    main()