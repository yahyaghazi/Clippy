"""
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
