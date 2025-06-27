"""
Moteur de synthèse vocale pour l'Assistant IA
"""

import pyttsx3
import threading
import queue
import time
from typing import Optional
from ..config.settings import settings


class VoiceEngine:
    """Gestionnaire de synthèse vocale"""
    
    def __init__(self):
        self.engine: Optional[pyttsx3.Engine] = None
        self.available = False
        self.speaking = False
        self.voice_queue = queue.Queue()
        self.worker_thread = None
        
        # Configuration par défaut
        self.voice_config = {
            'rate': 180,        # Vitesse de parole (mots/minute)
            'volume': 0.8,      # Volume (0.0 à 1.0)
            'voice_id': None    # ID de la voix (None = par défaut)
        }
        
        self._initialize_engine()
        self._start_worker()
    
    def _initialize_engine(self):
        """Initialise le moteur de synthèse vocale"""
        try:
            self.engine = pyttsx3.init()
            
            # Configuration de base
            self.engine.setProperty('rate', self.voice_config['rate'])
            self.engine.setProperty('volume', self.voice_config['volume'])
            
            # Lister les voix disponibles
            voices = self.engine.getProperty('voices')
            print(f"[VOICE] {len(voices)} voix disponibles:")
            
            for i, voice in enumerate(voices):
                print(f"  {i}: {voice.name} ({voice.languages})")
                
                # Sélectionner une voix française si disponible
                if 'french' in voice.name.lower() or 'fr' in str(voice.languages).lower():
                    self.voice_config['voice_id'] = voice.id
                    self.engine.setProperty('voice', voice.id)
                    print(f"  ✅ Voix française sélectionnée: {voice.name}")
                    break
            
            self.available = True
            print("✅ Moteur vocal initialisé")
            
        except Exception as e:
            print(f"❌ Erreur initialisation moteur vocal: {e}")
            self.available = False
    
    def _start_worker(self):
        """Démarre le thread worker pour la synthèse vocale"""
        if self.available:
            self.worker_thread = threading.Thread(target=self._voice_worker, daemon=True)
            self.worker_thread.start()
    
    def _voice_worker(self):
        """Worker thread pour gérer la queue de synthèse vocale"""
        while self.available:
            try:
                # Attendre un message dans la queue
                message = self.voice_queue.get(timeout=1)
                
                if message == "STOP":
                    break
                
                # Synthèse vocale
                self.speaking = True
                print(f"[VOICE] Synthèse: {message[:50]}...")
                
                self.engine.say(message)
                self.engine.runAndWait()
                
                self.speaking = False
                self.voice_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ERROR VOICE] Erreur synthèse: {e}")
                self.speaking = False
    
    def speak(self, text: str, priority: bool = False):
        """
        Fait parler l'assistant
        
        Args:
            text: Texte à synthétiser
            priority: Si True, vide la queue et parle immédiatement
        """
        if not self.available:
            print("[VOICE] Moteur vocal non disponible")
            return
        
        # Nettoyer le texte (enlever émojis et markdown)
        clean_text = self._clean_text(text)
        
        if not clean_text.strip():
            return
        
        if priority:
            # Vider la queue et arrêter la synthèse en cours
            self.stop()
            time.sleep(0.1)
        
        # Ajouter à la queue
        self.voice_queue.put(clean_text)
        print(f"[VOICE] Ajouté à la queue: {clean_text[:50]}...")
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte pour la synthèse vocale"""
        import re
        
        # Enlever les émojis
        emoji_pattern = re.compile("["
                                 u"\U0001F600-\U0001F64F"  # emoticons
                                 u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                 u"\U0001F680-\U0001F6FF"  # transport & map
                                 u"\U0001F1E0-\U0001F1FF"  # flags
                                 u"\U00002702-\U000027B0"
                                 u"\U000024C2-\U0001F251"
                                 "]+", flags=re.UNICODE)
        
        text = emoji_pattern.sub('', text)
        
        # Enlever les préfixes d'interface
        text = re.sub(r'^📱.*?\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'^🕒.*?\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'^💡\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^🤔.*?\n', '', text, flags=re.MULTILINE)
        
        # Nettoyer les caractères spéciaux
        text = text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def stop(self):
        """Arrête la synthèse vocale en cours"""
        if self.available and self.engine:
            try:
                self.engine.stop()
                
                # Vider la queue
                while not self.voice_queue.empty():
                    try:
                        self.voice_queue.get_nowait()
                    except queue.Empty:
                        break
                
                self.speaking = False
                print("[VOICE] Synthèse vocale arrêtée")
                
            except Exception as e:
                print(f"[ERROR VOICE] Erreur arrêt: {e}")
    
    def is_speaking(self) -> bool:
        """Retourne True si l'assistant est en train de parler"""
        return self.speaking
    
    def set_voice_properties(self, rate: int = None, volume: float = None, voice_id: str = None):
        """Configure les propriétés de la voix"""
        if not self.available:
            return
        
        try:
            if rate is not None:
                self.voice_config['rate'] = rate
                self.engine.setProperty('rate', rate)
                print(f"[VOICE] Vitesse: {rate} mots/min")
            
            if volume is not None:
                self.voice_config['volume'] = max(0.0, min(1.0, volume))
                self.engine.setProperty('volume', self.voice_config['volume'])
                print(f"[VOICE] Volume: {self.voice_config['volume']}")
            
            if voice_id is not None:
                self.voice_config['voice_id'] = voice_id
                self.engine.setProperty('voice', voice_id)
                print(f"[VOICE] Voix changée: {voice_id}")
                
        except Exception as e:
            print(f"[ERROR VOICE] Erreur configuration: {e}")
    
    def get_available_voices(self) -> list:
        """Retourne la liste des voix disponibles"""
        if not self.available:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            return [{'id': voice.id, 'name': voice.name, 'languages': voice.languages} 
                   for voice in voices]
        except:
            return []
    
    def test_voice(self, text: str = "Bonjour, je suis votre assistant IA !"):
        """Teste la synthèse vocale"""
        self.speak(text, priority=True)
    
    def shutdown(self):
        """Arrête proprement le moteur vocal"""
        if self.available:
            self.voice_queue.put("STOP")
            self.stop()
            self.available = False
            
            if self.worker_thread and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=2)
            
            print("[VOICE] Moteur vocal arrêté")


# Instance globale
voice_engine = VoiceEngine()