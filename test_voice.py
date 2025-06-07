"""
Script de test pour la synthèse vocale
Lance ce script pour vérifier que la synthèse vocale fonctionne
"""

def test_voice_simple():
    """Test simple de pyttsx3"""
    try:
        import pyttsx3
        print("✅ pyttsx3 trouvé")
        
        engine = pyttsx3.init()
        print("✅ Moteur initialisé")
        
        # Test de base
        engine.say("Test de synthèse vocale")
        engine.runAndWait()
        print("✅ Test vocal réussi")
        
        return True
        
    except ImportError:
        print("❌ pyttsx3 non installé")
        print("   Installez avec: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_voice_engine():
    """Test du moteur vocal de l'assistant"""
    try:
        import sys
        from pathlib import Path
        
        # Ajouter src au path
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        from src.utils.voice_engine import voice_engine
        print("✅ VoiceEngine importé")
        
        # Informations
        info = voice_engine.get_voice_info()
        print(f"Disponible: {info['available']}")
        print(f"Vitesse: {info['rate']} mots/min")
        print(f"Volume: {info['volume']}")
        
        # Voix disponibles
        voices = voice_engine.get_available_voices()
        print(f"Voix disponibles: {len(voices)}")
        for i, voice in enumerate(voices[:3]):  # Afficher les 3 premières
            print(f"  {i+1}. {voice['name']}")
        
        # Test vocal
        if info['available']:
            voice_engine.test_voice("Bonjour ! Je suis votre assistant IA.")
            print("✅ Test VoiceEngine réussi")
        else:
            print("❌ VoiceEngine non disponible")
        
        return info['available']
        
    except Exception as e:
        print(f"❌ Erreur VoiceEngine: {e}")
        return False


def main():
    """Test complet"""
    print("🔊 Test de la synthèse vocale")
    print("=" * 40)
    
    print("\n1. Test pyttsx3 direct:")
    simple_ok = test_voice_simple()
    
    print("\n2. Test VoiceEngine:")
    engine_ok = test_voice_engine()
    
    print("\n" + "=" * 40)
    if simple_ok and engine_ok:
        print("🎉 Synthèse vocale entièrement fonctionnelle !")
    elif simple_ok:
        print("⚠️ pyttsx3 fonctionne mais VoiceEngine a un problème")
    else:
        print("❌ Synthèse vocale non fonctionnelle")
        print("\nSolutions:")
        print("- pip install pyttsx3")
        print("- Vérifier les permissions audio")
        print("- Redémarrer l'ordinateur si nécessaire")


if __name__ == "__main__":
    main()