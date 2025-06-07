#!/usr/bin/env python3
"""
Correction des problèmes vocaux détectés
"""

import os
import sys
from pathlib import Path


def create_voice_command_engine():
    """Crée le fichier voice_command_engine.py"""
    voice_engine_code = '''"""
Moteur de commandes vocales pour l'Assistant IA
"""

import speech_recognition as sr
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any

# Import conditionnel
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio non disponible - certaines fonctionnalités limitées")


class VoiceCommandEngine:
    """Moteur de reconnaissance vocale et exécution de commandes"""
    
    def __init__(self, command_callback: Callable[[str], None] = None):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.command_callback = command_callback
        
        # État du système
        self.listening = False
        self.active = False
        self.paused = False
        
        # Configuration
        self.wake_word = "assistant"  # Mot de réveil
        self.language = "fr-FR"      # Français
        self.timeout = 5             # Timeout écoute
        self.phrase_timeout = 1      # Timeout phrase
        
        # Queue pour les commandes
        self.command_queue = queue.Queue()
        
        # Threads
        self.listen_thread = None
        self.process_thread = None
        
        # Statistiques
        self.stats = {
            'commands_recognized': 0,
            'commands_executed': 0,
            'wake_words_detected': 0,
            'errors': 0
        }
        
        self._initialize_microphone()
    
    def _initialize_microphone(self):
        """Initialise le microphone"""
        try:
            if PYAUDIO_AVAILABLE:
                self.microphone = sr.Microphone()
                
                # Calibrage automatique du bruit ambiant
                print("[VOICE] Calibrage microphone...")
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Réglages pour meilleure reconnaissance
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
                
                print(f"[VOICE] Microphone initialisé")
                print(f"[VOICE] Seuil énergie: {self.recognizer.energy_threshold}")
                return True
            else:
                print("[VOICE] PyAudio non disponible - mode dégradé")
                return False
                
        except Exception as e:
            print(f"[VOICE ERROR] Erreur initialisation microphone: {e}")
            return False
    
    def test_microphone_enhanced(self):
        """Test microphone amélioré"""
        if not self.microphone:
            print("[VOICE] Microphone non disponible")
            return False
        
        print("[VOICE] 🎤 Test microphone amélioré...")
        print("Parlez FORT et CLAIREMENT : 'BONJOUR ASSISTANT'")
        
        try:
            with self.microphone as source:
                print("[VOICE] Calibrage bruit ambiant...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                
                print("[VOICE] 🔴 PARLEZ MAINTENANT (10 secondes)...")
                # Plus de temps et meilleurs paramètres
                audio = self.recognizer.listen(
                    source, 
                    timeout=10, 
                    phrase_time_limit=5
                )
            
            print("[VOICE] Reconnaissance en cours...")
            
            # Essayer plusieurs moteurs
            results = []
            
            # Google FR
            try:
                text_fr = self.recognizer.recognize_google(audio, language="fr-FR")
                results.append(f"Google FR: '{text_fr}'")
            except:
                results.append("Google FR: échec")
            
            # Google EN (fallback)
            try:
                text_en = self.recognizer.recognize_google(audio, language="en-US")
                results.append(f"Google EN: '{text_en}'")
            except:
                results.append("Google EN: échec")
            
            print("Résultats reconnaissance:")
            for result in results:
                print(f"  {result}")
            
            return len([r for r in results if "échec" not in r]) > 0
            
        except sr.WaitTimeoutError:
            print("[VOICE] ⏰ Timeout - aucun son détecté")
            print("💡 Vérifiez que le microphone fonctionne")
            return False
        except Exception as e:
            print(f"[VOICE ERROR] Erreur test: {e}")
            return False
    
    def start_listening(self):
        """Démarre l'écoute vocale en continu"""
        if self.listening:
            print("[VOICE] Écoute déjà active")
            return
        
        if not self.microphone:
            print("[VOICE ERROR] Microphone non disponible")
            return
        
        self.listening = True
        self.active = True
        
        # Démarrer les threads
        self.listen_thread = threading.Thread(target=self._listen_worker, daemon=True)
        self.process_thread = threading.Thread(target=self._process_worker, daemon=True)
        
        self.listen_thread.start()
        self.process_thread.start()
        
        print(f"[VOICE] 🎤 Écoute démarrée - Dites '{self.wake_word}' pour activer")
    
    def stop_listening(self):
        """Arrête l'écoute vocale"""
        self.listening = False
        self.active = False
        print("[VOICE] 🔇 Écoute arrêtée")
    
    def _listen_worker(self):
        """Thread d'écoute en continu"""
        while self.listening:
            try:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # Écouter l'audio
                with self.microphone as source:
                    audio = self.recognizer.listen(
                        source, 
                        timeout=1, 
                        phrase_time_limit=3
                    )
                
                # Ajouter à la queue de traitement
                self.command_queue.put(audio)
                
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                if self.listening:
                    print(f"[VOICE ERROR] Erreur écoute: {e}")
                    time.sleep(0.1)
    
    def _process_worker(self):
        """Thread de traitement des commandes vocales"""
        while self.active:
            try:
                audio = self.command_queue.get(timeout=1)
                
                if self.paused:
                    self.command_queue.task_done()
                    continue
                
                # Reconnaissance vocale
                text = self._recognize_speech(audio)
                
                if text:
                    self._handle_recognized_text(text)
                
                self.command_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VOICE ERROR] Erreur traitement: {e}")
    
    def _recognize_speech(self, audio) -> Optional[str]:
        """Reconnaît la parole depuis l'audio"""
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text.lower().strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[VOICE ERROR] Erreur service reconnaissance: {e}")
            return None
        except Exception as e:
            print(f"[VOICE ERROR] Erreur reconnaissance: {e}")
            return None
    
    def _handle_recognized_text(self, text: str):
        """Traite le texte reconnu"""
        print(f"[VOICE] 👂 Entendu: '{text}'")
        
        # Vérifier le mot de réveil
        if self.wake_word in text:
            self.stats['wake_words_detected'] += 1
            print(f"[VOICE] 🎯 Mot de réveil détecté !")
            
            # Extraire la commande
            command = self._extract_command_after_wake_word(text)
            
            if command:
                self.stats['commands_recognized'] += 1
                print(f"[VOICE] 🎤 Commande: '{command}'")
                
                # Exécuter la commande
                if self.command_callback:
                    self.command_callback(command)
                    self.stats['commands_executed'] += 1
    
    def _extract_command_after_wake_word(self, text: str) -> Optional[str]:
        """Extrait la commande qui suit le mot de réveil"""
        try:
            wake_pos = text.find(self.wake_word)
            if wake_pos == -1:
                return None
            
            command_start = wake_pos + len(self.wake_word)
            command = text[command_start:].strip()
            
            # Enlever les mots de liaison
            filler_words = ['euh', 'alors', 'donc', 'voilà', 'bon']
            words = command.split()
            filtered_words = [w for w in words if w not in filler_words]
            
            return ' '.join(filtered_words) if filtered_words else None
            
        except Exception as e:
            print(f"[VOICE ERROR] Erreur extraction commande: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques"""
        return {
            **self.stats,
            "listening": self.listening,
            "active": self.active,
            "microphone_available": self.microphone is not None
        }


# Instance globale
voice_command_engine = VoiceCommandEngine()
'''
    
    # Créer le dossier si nécessaire
    voice_file = Path("src/utils/voice_command_engine.py")
    voice_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(voice_file, 'w', encoding='utf-8') as f:
        f.write(voice_engine_code)
    
    print(f"✅ Créé: {voice_file}")


def fix_main_vocal():
    """Corrige le fichier main_vocal.py pour les imports"""
    main_vocal_code = '''#!/usr/bin/env python3
"""
main_vocal.py - Assistant IA avec commandes vocales intégrées
"""

import sys
import time
import threading
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path("src")))

# Imports corrigés
from ui.main_window import MainWindow
from utils.voice_command_engine import voice_command_engine
from ai_system.command_parser import command_parser
from vision.screen_capture import screen_capture
from control.mouse_controller import mouse_controller
from control.keyboard_controller import keyboard_controller
from utils.voice_engine import voice_engine


class VoiceAssistant:
    """Assistant IA avec commandes vocales"""
    
    def __init__(self):
        self.main_window = None
        self.voice_active = False
        self.command_history = []
        
        # Configuration vocale
        self.setup_voice_engine()
        print("🎤 Assistant vocal initialisé")
    
    def setup_voice_engine(self):
        """Configure le moteur de commandes vocales"""
        voice_command_engine.command_callback = self.handle_voice_command
        
        # Configuration personnalisée
        voice_command_engine.wake_word = "assistant"
        voice_command_engine.language = "fr-FR"
        voice_command_engine.timeout = 3
    
    def handle_voice_command(self, command: str):
        """Traite une commande vocale reconnue"""
        print(f"[ASSISTANT] 🎯 Commande reçue: '{command}'")
        
        # Ajouter à l'historique
        self.command_history.append({
            'command': command,
            'timestamp': time.time(),
            'source': 'voice'
        })
        
        # Annoncer la réception
        if voice_engine.available:
            voice_engine.speak(f"Commande reçue: {command}", priority=True)
        
        # Parser la commande
        actions = command_parser.parse_command(command)
        
        if not actions:
            if voice_engine.available:
                voice_engine.speak("Je n'ai pas compris cette commande")
            print("❌ Commande non reconnue")
            return
        
        # Prendre la meilleure action
        best_action = actions[0]
        print(f"[ASSISTANT] Action: {best_action.description}")
        
        # Validation sécurité
        valid, msg = command_parser.validate_action(best_action)
        if not valid:
            if voice_engine.available:
                voice_engine.speak(f"Action non autorisée: {msg}")
            print(f"⚠️ Action bloquée: {msg}")
            return
        
        # Annoncer l'exécution
        if voice_engine.available:
            voice_engine.speak(f"Exécution de {best_action.description}")
        
        # Exécuter l'action
        success = self.execute_action(best_action)
        
        if success:
            if voice_engine.available:
                voice_engine.speak("Action réalisée avec succès")
            print("✅ Action réussie")
        else:
            if voice_engine.available:
                voice_engine.speak("Échec de l'action")
            print("❌ Action échouée")
    
    def execute_action(self, action) -> bool:
        """Exécute une action parsée"""
        try:
            action_type = action.action_type.value
            params = action.parameters
            
            if action_type == "screenshot":
                screenshot = screen_capture.capture_full_screen()
                return screenshot is not None
            
            elif action_type == "click":
                if 'x' in params and 'y' in params:
                    return mouse_controller.click(params['x'], params['y'])
                return False
            
            elif action_type == "type":
                text = params.get('text', '')
                return keyboard_controller.type_text(text)
            
            elif action_type == "key_press":
                if 'keys' in params:
                    return keyboard_controller.hotkey(*params['keys'])
                else:
                    key = params.get('key', '')
                    return keyboard_controller.press_key(key)
            
            elif action_type == "scroll":
                clicks = params.get('clicks', 1)
                return mouse_controller.scroll(clicks)
            
            elif action_type == "mouse_move":
                if 'x' in params and 'y' in params:
                    return mouse_controller.move_to(params['x'], params['y'])
                return False
            
            elif action_type == "wait":
                seconds = params.get('seconds', 1)
                time.sleep(seconds)
                return True
            
            else:
                print(f"[ASSISTANT] Action non implémentée: {action_type}")
                return False
                
        except Exception as e:
            print(f"[ASSISTANT ERROR] Erreur exécution: {e}")
            return False
    
    def start_voice_mode(self):
        """Démarre le mode vocal"""
        if self.voice_active:
            print("[ASSISTANT] Mode vocal déjà actif")
            return
        
        print("[ASSISTANT] 🎤 Démarrage du mode vocal...")
        
        # Démarrer l'écoute
        voice_command_engine.start_listening()
        self.voice_active = True
        
        # Annoncer le démarrage
        if voice_engine.available:
            voice_engine.speak("Mode vocal activé. Dites 'assistant' suivi de votre commande.")
        
        print("🎤 Mode vocal ACTIF")
        print("🗣️ Dites: 'assistant [commande]'")
    
    def stop_voice_mode(self):
        """Arrête le mode vocal"""
        if not self.voice_active:
            return
        
        print("[ASSISTANT] 🔇 Arrêt du mode vocal...")
        voice_command_engine.stop_listening()
        self.voice_active = False
        
        if voice_engine.available:
            voice_engine.speak("Mode vocal désactivé")
    
    def toggle_voice_mode(self):
        """Bascule le mode vocal"""
        if self.voice_active:
            self.stop_voice_mode()
        else:
            self.start_voice_mode()
    
    def test_voice_system(self):
        """Test complet du système vocal"""
        print("[ASSISTANT] 🧪 Test du système vocal...")
        
        # Test microphone amélioré
        print("1. Test microphone...")
        mic_test = voice_command_engine.test_microphone_enhanced()
        
        # Test synthèse
        print("2. Test synthèse vocale...")
        if voice_engine.available:
            voice_engine.test_voice("Test du système vocal")
            synth_test = True
        else:
            synth_test = False
        
        print(f"Microphone: {'✅' if mic_test else '❌'}")
        print(f"Synthèse: {'✅' if synth_test else '❌'}")
        
        return mic_test
    
    def run_simple(self):
        """Lance l'assistant en mode console simple"""
        print("🎤 ASSISTANT VOCAL - MODE CONSOLE")
        print("=" * 50)
        
        # Test système vocal
        voice_ok = self.test_voice_system()
        
        if not voice_ok:
            print("⚠️ Problèmes détectés avec le microphone")
            choice = input("Continuer quand même ? (o/N): ")
            if choice.lower() not in ['o', 'oui']:
                return
        
        # Démarrer le mode vocal
        self.start_voice_mode()
        
        print("\\n📋 COMMANDES DISPONIBLES:")
        print("  'Assistant, prends une capture'")
        print("  'Assistant, clique à 500, 300'")
        print("  'Assistant, écris bonjour'")
        print("  'Assistant, scroll vers le bas'")
        print("\\nAppuyez sur Ctrl+C pour quitter")
        
        try:
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\\n[ASSISTANT] Arrêt demandé")
        finally:
            self.stop_voice_mode()
    
    def run(self):
        """Lance l'assistant avec interface graphique"""
        print("🚀 Lancement de l'assistant vocal avec interface...")
        
        try:
            # Créer l'interface principale
            self.main_window = MainWindow()
            
            # Test vocal
            voice_ok = self.test_voice_system()
            
            if voice_ok:
                # Démarrer en mode vocal après 3 secondes
                self.main_window.root.after(3000, self.start_voice_mode)
            
            # Lancer l'interface
            self.main_window.run()
            
        except Exception as e:
            print(f"Erreur interface graphique: {e}")
            print("Basculement en mode console...")
            self.run_simple()
        finally:
            self.stop_voice_mode()


def main():
    """Point d'entrée principal"""
    print("🎤 ASSISTANT IA VOCAL")
    print("=" * 50)
    
    # Vérifier les dépendances vocales
    try:
        import speech_recognition
        print("✅ SpeechRecognition disponible")
    except ImportError:
        print("❌ SpeechRecognition manquant")
        print("Installez avec: pip install speechrecognition")
        return
    
    try:
        import pyaudio
        print("✅ PyAudio disponible")
    except ImportError:
        print("⚠️ PyAudio manquant - mode dégradé")
    
    # Mode de lancement
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        # Mode console uniquement
        assistant = VoiceAssistant()
        assistant.run_simple()
    else:
        # Mode interface graphique (avec fallback console)
        assistant = VoiceAssistant()
        assistant.run()


if __name__ == "__main__":
    main()
'''
    
    with open("main_vocal.py", 'w', encoding='utf-8') as f:
        f.write(main_vocal_code)
    
    print("✅ main_vocal.py corrigé")


def create_enhanced_voice_test():
    """Crée un test vocal amélioré"""
    test_code = '''#!/usr/bin/env python3
"""
Test vocal amélioré avec calibrage et diagnostics
"""

import speech_recognition as sr
import time

def test_microphone_detailed():
    """Test microphone avec diagnostics détaillés"""
    print("🎤 TEST MICROPHONE DÉTAILLÉ")
    print("=" * 40)
    
    try:
        r = sr.Recognizer()
        
        # Lister les micros
        print("📋 Micros disponibles:")
        for i, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {i}: {name}")
        
        # Utiliser le micro par défaut
        with sr.Microphone() as source:
            print("\\n🔧 Calibrage avancé...")
            r.adjust_for_ambient_noise(source, duration=3)
            
            # Paramètres optimaux
            r.energy_threshold = 300
            r.dynamic_energy_threshold = True
            r.pause_threshold = 0.8
            
            print(f"Seuil énergie: {r.energy_threshold}")
            print(f"Seuil dynamique: {r.dynamic_energy_threshold}")
            print(f"Pause threshold: {r.pause_threshold}")
            
            print("\\n🔴 PARLEZ MAINTENANT - dites 'BONJOUR ASSISTANT' (10 sec)")
            print("Parlez FORT et CLAIREMENT près du microphone...")
            
            # Écoute prolongée
            audio = r.listen(source, timeout=10, phrase_time_limit=5)
        
        print("\\n🤖 Reconnaissance en cours...")
        
        # Test plusieurs langues
        results = []
        
        # Français
        try:
            text_fr = r.recognize_google(audio, language="fr-FR")
            results.append(("Français", text_fr))
            print(f"🇫🇷 Français: '{text_fr}'")
        except sr.UnknownValueError:
            print("🇫🇷 Français: non compris")
        except sr.RequestError as e:
            print(f"🇫🇷 Français: erreur service - {e}")
        
        # Anglais (fallback)
        try:
            text_en = r.recognize_google(audio, language="en-US")
            results.append(("Anglais", text_en))
            print(f"🇺🇸 Anglais: '{text_en}'")
        except sr.UnknownValueError:
            print("🇺🇸 Anglais: non compris")
        except sr.RequestError as e:
            print(f"🇺🇸 Anglais: erreur service - {e}")
        
        if results:
            print(f"\\n✅ Reconnaissance réussie ! {len(results)} résultat(s)")
            return True
        else:
            print("\\n❌ Aucune reconnaissance réussie")
            return False
            
    except sr.WaitTimeoutError:
        print("\\n⏰ Timeout - aucun son détecté")
        print("💡 Vérifiez:")
        print("  - Microphone branché et allumé")
        print("  - Permissions microphone accordées")
        print("  - Volume d'entrée suffisant")
        return False
        
    except Exception as e:
        print(f"\\n❌ Erreur: {e}")
        return False

def main():
    """Test principal"""
    print("🧪 TEST VOCAL AMÉLIORÉ")
    print("=" * 50)
    
    success = test_microphone_detailed()
    
    print("\\n" + "=" * 50)
    if success:
        print("🎉 TEST RÉUSSI ! Système vocal opérationnel.")
        print("\\n🚀 Prochaines étapes:")
        print("  python main_vocal.py --console    # Mode console")
        print("  python main_vocal.py             # Mode graphique")
    else:
        print("⚠️ TEST ÉCHOUÉ. Vérifiez la configuration.")
        print("\\n🔧 Solutions possibles:")
        print("  1. Vérifier permissions microphone")
        print("  2. Ajuster volume d'entrée Windows")
        print("  3. Tester avec un autre microphone")
        print("  4. Redémarrer l'application")

if __name__ == "__main__":
    main()
'''
    
    with open("test_vocal_ameliore.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ test_vocal_ameliore.py créé")


def main():
    """Correction principale"""
    print("🔧 CORRECTION PROBLÈMES VOCAUX")
    print("=" * 50)
    
    print("Problèmes détectés:")
    print("1. ❌ Imports relatifs dans main_vocal.py")
    print("2. ❌ Fichier voice_command_engine.py manquant")
    print("3. ⚠️ Reconnaissance vocale imprécise")
    
    # Corrections
    print("\\n🔧 Application des corrections...")
    
    create_voice_command_engine()
    fix_main_vocal()
    create_enhanced_voice_test()
    
    print("\\n✅ CORRECTIONS APPLIQUÉES")
    print("\\n🧪 TESTS RECOMMANDÉS:")
    print("1. python test_vocal_ameliore.py     # Test micro amélioré")
    print("2. python main_vocal.py --console    # Mode console")
    print("3. python main_vocal.py             # Mode graphique")
    
    print("\\n💡 CONSEILS RECONNAISSANCE VOCALE:")
    print("  • Parlez FORT et CLAIREMENT")
    print("  • Dites 'ASSISTANT' distinctement")
    print("  • Réduisez le bruit ambiant")
    print("  • Rapprochez-vous du microphone")
    
    print("\\n🎤 COMMANDES VOCALES:")
    print("  'Assistant, prends une capture d'écran'")
    print("  'Assistant, clique à cinq cents, trois cents'")
    print("  'Assistant, écris bonjour le monde'")


if __name__ == "__main__":
    main()
