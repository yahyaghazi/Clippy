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
    optional_deps = []
    
    # Dépendances obligatoires
    try:
        import psutil
        print(f"✅ psutil {psutil.__version__}")
    except ImportError:
        missing_deps.append("psutil")
    
    try:
        import requests
        print(f"✅ requests {requests.__version__}")
    except ImportError:
        missing_deps.append("requests")
    
    # Dépendances optionnelles
    try:
        import pyttsx3
        version = getattr(pyttsx3, '__version__', 'version inconnue')
        print(f"✅ pyttsx3 {version} (synthèse vocale)")
    except ImportError:
        optional_deps.append("pyttsx3")
        print("⚠️ pyttsx3 non installé (synthèse vocale désactivée)")
    
    try:
        import win32gui
        print("✅ pywin32 (détection fenêtre Windows)")
    except ImportError:
        optional_deps.append("pywin32")
        print("⚠️ pywin32 non installé (détection fenêtre limitée)")
    
    if missing_deps:
        print("\n❌ Dépendances OBLIGATOIRES manquantes:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print(f"\nInstallez avec: pip install {' '.join(missing_deps)}")
        return False
    
    if optional_deps:
        print(f"\n💡 Dépendances optionnelles manquantes: {', '.join(optional_deps)}")
        print("L'assistant fonctionnera avec des fonctionnalités limitées.")
    
    return True


def test_voice_engine():
    """Test rapide du moteur vocal"""
    try:
        from src.utils.voice_engine import voice_engine
        
        print("\n🔊 Test du moteur vocal...")
        voice_info = voice_engine.get_voice_info()
        
        print(f"- Disponible: {'✅' if voice_info['available'] else '❌'}")
        print(f"- pyttsx3: {'✅' if voice_info['pyttsx3_available'] else '❌'}")
        
        if voice_info['available']:
            print(f"- Vitesse: {voice_info['rate']} mots/min")
            print(f"- Volume: {voice_info['volume']}")
            
            voices = voice_engine.get_available_voices()
            print(f"- Voix disponibles: {len(voices)}")
            
            # Test vocal court
            voice_engine.test_voice("Test vocal réussi")
            
        return voice_info['available']
        
    except Exception as e:
        print(f"❌ Erreur test vocal: {e}")
        return False


def main():
    """Fonction principale"""
    print("🚀 Démarrage de l'Assistant IA avec synthèse vocale...")
    print("=" * 50)
    
    # Vérifier les dépendances
    if not check_dependencies():
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    # Test vocal
    voice_available = test_voice_engine()
    
    # Configurer les logs
    logger = setup_logger()
    logger.info("Assistant IA démarré")
    
    print("\n" + "=" * 50)
    print("🎭 Lancement de l'interface...")
    
    try:
        # Créer et lancer la fenêtre principale
        app = MainWindow()
        
        print("✅ Interface créée")
        print("🎯 Fonctionnalités disponibles:")
        print(f"   - Surveillance système: ✅")
        print(f"   - IA Ollama: {'✅ si démarré' if app.ollama_client else '❌'}")
        print(f"   - Synthèse vocale: {'✅' if voice_available else '❌'}")
        print(f"   - Apprentissage: ✅")
        print(f"   - Thèmes: ✅")
        
        print("\n🎮 Contrôles:")
        print("   - 🎨 Changer de thème")
        print("   - 🔊 Activer/désactiver la voix") 
        print("   - ⚙️ Voir les paramètres")
        print("   - Glisser la barre pour déplacer")
        
        print("\n🚀 Interface lancée !")
        app.run()
        
    except KeyboardInterrupt:
        print("\n🔄 Arrêt demandé par l'utilisateur")
        logger.info("Arrêt demandé par l'utilisateur")
        
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        logger.error(f"Erreur fatale: {e}", exc_info=True)
        
        # Debug détaillé en cas d'erreur
        print("\n🔍 Informations de debug:")
        print(f"   - Python: {sys.version}")
        print(f"   - Plateforme: {sys.platform}")
        print(f"   - Dossier de travail: {os.getcwd()}")
        
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    finally:
        logger.info("Assistant IA arrêté")
        print("👋 Au revoir !")


if __name__ == "__main__":
    main()