"""
Moteur de reconnaissance vocale pour l'Assistant IA
"""

import threading
import queue
import time
from typing import Optional, Callable
import speech_recognition as sr


class SpeechRecognitionEngine:
    """Gestionnaire de reconnaissance vocale"""
    
    def __init__(self, on_speech_callback: Callable[[str], None] = None):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.available = False
        self.listening = False
        self.continuous_mode = False
        
        self.on_speech_callback = on_speech_callback
        self.speech_queue = queue.Queue()
        self.worker_thread = None
        
        # Configuration
        self.language = "fr-FR"
        self.timeout = 5  # secondes
        self.phrase_timeout = 2  # secondes
        
        self._initialize_microphone()
        
    def _initialize_microphone(self):
        """Initialise le microphone"""
        try:
            # Tester la disponibilité du microphone
            self.microphone = sr.Microphone()
            
            # Calibrer le microphone pour le bruit ambiant
            with self.microphone as source:
                print("[SPEECH] Calibrage du microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.available = True
            print("✅ Microphone initialisé et calibré")
            
        except Exception as e:
            print(f"❌ Erreur initialisation microphone: {e}")
            self.available = False
    
    def listen_once(self) -> Optional[str]:
        """Écoute une seule fois et retourne le texte reconnu"""
        if not self.available:
            print("[SPEECH] Microphone non disponible")
            return None
        
        try:
            print("🎤 Parlez maintenant...")
            with self.microphone as source:
                # Ajuster pour le bruit ambiant
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Écouter avec timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_timeout
                )
            
            print("🔄 Reconnaissance en cours...")
            
            # Reconnaître le texte
            text = self.recognizer.recognize_google(
                audio, 
                language=self.language
            )
            
            print(f"📝 Reconnu: {text}")
            return text.strip()
            
        except sr.WaitTimeoutError:
            print("⏱️ Timeout - aucun son détecté")
            return None
        except sr.UnknownValueError:
            print("❌ Parole non comprise")
            return None
        except sr.RequestError as e:
            print(f"❌ Erreur service reconnaissance: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return None
    
    def start_continuous_listening(self):
        """Démarre l'écoute continue en arrière-plan"""
        if not self.available:
            print("[SPEECH] Impossible de démarrer - microphone non disponible")
            return False
        
        if self.listening:
            print("[SPEECH] Écoute déjà en cours")
            return True
        
        self.continuous_mode = True
        self.listening = True
        
        # Démarrer le thread d'écoute
        self.worker_thread = threading.Thread(
            target=self._continuous_listen_worker, 
            daemon=True
        )
        self.worker_thread.start()
        
        print("🎤 Écoute continue démarrée")
        return True
    
    def stop_continuous_listening(self):
        """Arrête l'écoute continue"""
        self.continuous_mode = False
        self.listening = False
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)
        
        print("🔇 Écoute continue arrêtée")
    
    def _continuous_listen_worker(self):
        """Worker thread pour l'écoute continue"""
        print("[SPEECH] Worker d'écoute continue démarré")
        
        while self.continuous_mode and self.available:
            try:
                # Écouter un échantillon
                text = self.listen_once()
                
                if text:
                    # Vérifier les mots d'arrêt
                    if self._is_stop_command(text):
                        print("🛑 Commande d'arrêt détectée")
                        self.stop_continuous_listening()
                        break
                    
                    # Envoyer via callback
                    if self.on_speech_callback:
                        try:
                            self.on_speech_callback(text)
                        except Exception as e:
                            print(f"[SPEECH ERROR] Erreur callback: {e}")
                
                # Petite pause pour éviter la surcharge
                time.sleep(0.5)
                
            except Exception as e:
                print(f"[SPEECH ERROR] Erreur dans worker: {e}")
                time.sleep(1)
        
        print("[SPEECH] Worker d'écoute terminé")
    
    def _is_stop_command(self, text: str) -> bool:
        """Vérifie si le texte contient une commande d'arrêt"""
        stop_words = [
            "stop", "arrête", "arrêt", "arrêter", "stop écoute",
            "silence", "chut", "tais-toi", "ferme", "fini"
        ]
        
        text_lower = text.lower()
        return any(word in text_lower for word in stop_words)
    
    def toggle_listening(self) -> bool:
        """Bascule entre écoute active et inactive"""
        if self.listening:
            self.stop_continuous_listening()
            return False
        else:
            return self.start_continuous_listening()
    
    def is_listening(self) -> bool:
        """Retourne True si en cours d'écoute"""
        return self.listening
    
    def set_language(self, language_code: str):
        """Change la langue de reconnaissance"""
        self.language = language_code
        print(f"[SPEECH] Langue changée: {language_code}")
    
    def set_timeouts(self, listen_timeout: int, phrase_timeout: int):
        """Configure les timeouts"""
        self.timeout = listen_timeout
        self.phrase_timeout = phrase_timeout
        print(f"[SPEECH] Timeouts: écoute={listen_timeout}s, phrase={phrase_timeout}s")
    
    def test_microphone(self) -> bool:
        """Teste le microphone avec un échantillon rapide"""
        if not self.available:
            return False
        
        print("🧪 Test du microphone - dites quelque chose...")
        text = self.listen_once()
        
        if text:
            print(f"✅ Test réussi: '{text}'")
            return True
        else:
            print("❌ Test échoué")
            return False
    
    def get_microphone_list(self) -> list:
        """Retourne la liste des microphones disponibles"""
        try:
            mic_list = []
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                mic_list.append(f"{index}: {name}")
            return mic_list
        except Exception as e:
            print(f"[SPEECH ERROR] Erreur listage micros: {e}")
            return []
    
    def set_microphone(self, device_index: int):
        """Change le microphone utilisé"""
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            print(f"[SPEECH] Microphone changé: index {device_index}")
            
            # Recalibrer
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            return True
        except Exception as e:
            print(f"[SPEECH ERROR] Erreur changement micro: {e}")
            return False


# Instance globale (sera initialisée dans main_window)
speech_engine: Optional[SpeechRecognitionEngine] = None