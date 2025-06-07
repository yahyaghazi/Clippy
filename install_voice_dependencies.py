#!/usr/bin/env python3
"""
Installation automatique des dépendances vocales
"""

import subprocess
import sys
import os
import platform


def install_package(package):
    """Installe un package Python"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True, check=True)
        print(f"✅ {package} installé")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation {package}: {e}")
        print(f"Sortie: {e.stdout}")
        print(f"Erreur: {e.stderr}")
        return False


def install_pyaudio_windows():
    """Installation spéciale de PyAudio sur Windows"""
    print("🔧 Installation PyAudio pour Windows...")
    
    # Essayer d'abord la méthode standard
    if install_package("pyaudio"):
        return True
    
    print("⚠️ Installation standard échouée, tentative méthode alternative...")
    
    # Méthode alternative avec wheel précompilé
    try:
        # Détecter l'architecture
        is_64bit = platform.machine().endswith('64')
        python_version = f"{sys.version_info.major}{sys.version_info.minor}"
        
        print(f"Python {python_version}, {'64-bit' if is_64bit else '32-bit'}")
        
        # URL wheel PyAudio (ajuster selon la version)
        base_url = "https://github.com/intxcc/pyaudio_portaudio/releases/download/v0.2.11"
        
        if is_64bit:
            wheel_name = f"PyAudio-0.2.11-cp{python_version}-cp{python_version}-win_amd64.whl"
        else:
            wheel_name = f"PyAudio-0.2.11-cp{python_version}-cp{python_version}-win32.whl"
        
        wheel_url = f"{base_url}/{wheel_name}"
        
        print(f"Tentative téléchargement: {wheel_name}")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", wheel_url
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyAudio installé via wheel précompilé")
            return True
        else:
            print("❌ Échec installation wheel")
            return False
            
    except Exception as e:
        print(f"❌ Erreur installation PyAudio: {e}")
        return False


def check_microphone_access():
    """Vérifie l'accès au microphone"""
    try:
        import pyaudio
        
        p = pyaudio.PyAudio()
        
        # Lister les micros
        mic_count = p.get_device_count()
        print(f"🎤 {mic_count} dispositifs audio détectés")
        
        # Chercher un micro par défaut
        default_input = None
        for i in range(mic_count):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"  Micro {i}: {device_info['name']}")
                if default_input is None:
                    default_input = i
        
        if default_input is not None:
            print(f"✅ Microphone par défaut trouvé: index {default_input}")
            
            # Test d'ouverture
            try:
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    input_device_index=default_input,
                    frames_per_buffer=1024
                )
                stream.close()
                print("✅ Test d'accès microphone réussi")
                success = True
            except Exception as e:
                print(f"❌ Erreur accès microphone: {e}")
                success = False
        else:
            print("❌ Aucun microphone d'entrée trouvé")
            success = False
        
        p.terminate()
        return success
        
    except ImportError:
        print("❌ PyAudio non disponible pour le test")
        return False
    except Exception as e:
        print(f"❌ Erreur test microphone: {e}")
        return False


def test_speech_recognition():
    """Test de la reconnaissance vocale"""
    print("\n🧪 Test reconnaissance vocale...")
    
    try:
        import speech_recognition as sr
        
        r = sr.Recognizer()
        
        # Test avec microphone
        with sr.Microphone() as source:
            print("🎤 Calibrage du bruit ambiant...")
            r.adjust_for_ambient_noise(source, duration=1)
            print(f"Seuil énergie: {r.energy_threshold}")
        
        print("✅ SpeechRecognition configuré")
        return True
        
    except ImportError:
        print("❌ SpeechRecognition non disponible")
        return False
    except Exception as e:
        print(f"❌ Erreur configuration SpeechRecognition: {e}")
        return False


def install_voice_dependencies():
    """Installation complète des dépendances vocales"""
    print("🎤 INSTALLATION DÉPENDANCES VOCALES")
    print("=" * 50)
    
    system = platform.system()
    print(f"Système: {system}")
    
    success_count = 0
    total_deps = 2
    
    # 1. SpeechRecognition (plus facile)
    print("\n📦 Installation SpeechRecognition...")
    if install_package("speechrecognition"):
        success_count += 1
    
    # 2. PyAudio (plus complexe)
    print("\n📦 Installation PyAudio...")
    if system == "Windows":
        if install_pyaudio_windows():
            success_count += 1
    else:
        # Linux/Mac
        print("ℹ️ Sur Linux/Mac, vous devrez peut-être installer des dépendances système:")
        print("  Ubuntu/Debian: sudo apt-get install portaudio19-dev")
        print("  macOS: brew install portaudio")
        
        if install_package("pyaudio"):
            success_count += 1
    
    print(f"\n📊 RÉSULTAT: {success_count}/{total_deps} dépendances installées")
    
    if success_count == total_deps:
        print("🎉 Toutes les dépendances vocales sont installées !")
        
        # Tests de validation
        print("\n🧪 Tests de validation...")
        mic_ok = check_microphone_access()
        sr_ok = test_speech_recognition()
        
        if mic_ok and sr_ok:
            print("\n✅ SYSTÈME VOCAL PRÊT !")
            print("🚀 Lancez: python main_vocal.py")
        else:
            print("\n⚠️ Installation réussie mais tests partiels")
            print("Vérifiez les permissions microphone")
    
    else:
        print("\n❌ Installation incomplète")
        print("\n🔧 Solutions manuelles:")
        print("1. SpeechRecognition: pip install speechrecognition")
        print("2. PyAudio Windows: télécharger wheel depuis:")
        print("   https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        print("3. PyAudio Linux: sudo apt-get install portaudio19-dev python3-pyaudio")
    
    return success_count == total_deps


def create_voice_test_script():
    """Crée un script de test vocal simple"""
    test_script = '''#!/usr/bin/env python3
"""
Test simple du système vocal
"""

def test_microphone():
    """Test microphone uniquement"""
    try:
        import speech_recognition as sr
        
        r = sr.Recognizer()
        
        print("🎤 Test microphone - Parlez après le bip...")
        
        with sr.Microphone() as source:
            print("Calibrage...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("PARLEZ MAINTENANT (5 secondes)...")
            audio = r.listen(source, timeout=5, phrase_time_limit=3)
        
        print("Reconnaissance en cours...")
        text = r.recognize_google(audio, language="fr-FR")
        print(f"✅ Reconnu: '{text}'")
        
        return True
        
    except sr.UnknownValueError:
        print("❓ Parole non comprise")
        return False
    except sr.RequestError as e:
        print(f"❌ Erreur service: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TEST VOCAL SIMPLE")
    print("=" * 30)
    
    success = test_microphone()
    
    if success:
        print("🎉 Test vocal réussi ! Système opérationnel.")
    else:
        print("⚠️ Test vocal échoué. Vérifiez microphone et connexion.")
'''
    
    try:
        with open("test_vocal_simple.py", "w", encoding="utf-8") as f:
            f.write(test_script)
        print("✅ Script test_vocal_simple.py créé")
    except Exception as e:
        print(f"❌ Erreur création script test: {e}")


def main():
    """Installation principale"""
    print("🎤 ASSISTANT VOCAL - INSTALLATION")
    print("=" * 60)
    
    print("Ce script va installer les dépendances pour:")
    print("  🎤 Reconnaissance vocale (SpeechRecognition)")
    print("  🔊 Accès microphone (PyAudio)")
    
    choice = input("\nContinuer l'installation ? (o/N): ").lower()
    
    if choice not in ['o', 'oui', 'y', 'yes']:
        print("❌ Installation annulée")
        return
    
    # Installation
    success = install_voice_dependencies()
    
    # Créer script de test
    create_voice_test_script()
    
    print("\n" + "=" * 60)
    print("📋 PROCHAINES ÉTAPES:")
    
    if success:
        print("1. 🧪 python test_vocal_simple.py    # Test rapide")
        print("2. 🎤 python main_vocal.py           # Assistant vocal")
        print("3. 🗣️ Dites 'assistant [commande]'    # Utilisation")
    else:
        print("1. 🔧 Corriger les erreurs d'installation")
        print("2. 🧪 python test_vocal_simple.py    # Tester quand même")
    
    print("\n💡 COMMANDES VOCALES EXEMPLES:")
    print("  'Assistant, prends une capture d'écran'")
    print("  'Assistant, clique à 500, 300'")
    print("  'Assistant, écris bonjour le monde'")
    print("  'Assistant, scroll vers le bas'")


if __name__ == "__main__":
    main()