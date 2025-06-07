"""
Moteur de synthèse vocale pour l'Assistant IA
"""

import threading
import queue
import time
from typing import Optional

# Import conditionnel pour éviter les erreurs si pyttsx3 n'est pas installé
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("⚠️ pyttsx3 non installé - synthèse vocale désactivée")

from ..config.settings import settings


class VoiceEngine:
    """Gestionnaire de synthèse vocale"""
    
    def __init__(self):
        self.engine: Optional = None
        self.available = False
        self.speaking = False
        self.voice_queue = queue.Queue()
        self.worker_thread = None
        self._shutdown_requested = False
        
        # Configuration par défaut
        self.voice_config = {
            'rate': 180,        # Vitesse de parole (mots/minute)
            'volume': 0.8,      # Volume (0.0 à 1.0)
            'voice_id': None    # ID de la voix (None = par défaut)
        }
        
        if PYTTSX3_AVAILABLE:
            self._initialize_engine()
            self._start_worker()
        else:
            print("[VOICE] pyttsx3 non disponible")
    
    def _initialize_engine(self):
        """Initialise le moteur de synthèse vocale"""
        try:
            self.engine = pyttsx3.init()
            
            # Configuration de base
            self.engine.setProperty('rate', self.voice_config['rate'])
            self.engine.setProperty('volume', self.voice_config['volume'])
            
            # Lister les voix disponibles
            voices = self.engine.getProperty('voices')
            if voices:
                print(f"[VOICE] {len(voices)} voix disponibles:")
                
                for i, voice in enumerate(voices[:3]):  # Limiter l'affichage
                    name = getattr(voice, 'name', f'Voix {i}')
                    lang = getattr(voice, 'languages', 'Inconnue')
                    print(f"  {i}: {name} ({lang})")
                    
                    # Sélectionner une voix française si disponible
                    name_lower = str(name).lower()
                    lang_str = str(lang).lower()
                    if ('french' in name_lower or 'fr' in lang_str or 
                        'france' in name_lower or 'français' in name_lower):
                        self.voice_config['voice_id'] = voice.id
                        self.engine.setProperty('voice', voice.id)
                        print(f"  ✅ Voix française sélectionnée: {name}")
                        break
            
            self.available = True
            print("✅ Moteur vocal initialisé")
            
        except Exception as e:
            print(f"❌ Erreur initialisation moteur vocal: {e}")
            self.available = False
    
    def _start_worker(self):
        """Démarre le thread worker pour la synthèse vocale"""
        if self.available and not self._shutdown_requested:
            self.worker_thread = threading.Thread(target=self._voice_worker, daemon=True)
            self.worker_thread.start()
    
    def _voice_worker(self):
        """Worker thread pour gérer la queue de synthèse vocale"""
        while self.available and not self._shutdown_requested:
            try:
                # Attendre un message dans la queue
                message = self.voice_queue.get(timeout=1)
                
                if message == "STOP" or self._shutdown_requested:
                    break
                
                # Synthèse vocale
                self.speaking = True
                print(f"[VOICE] Synthèse: {message[:50]}...")
                
                if self.engine:
                    self.engine.say(message)
                    self.engine.runAndWait()
                
                self.speaking = False
                self.voice_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ERROR VOICE] Erreur synthèse: {e}")
                self.speaking = False
        
        print("[VOICE] Worker thread arrêté")
    
    def speak(self, text: str, priority: bool = False):
        """
        Fait parler l'assistant
        
        Args:
            text: Texte à synthétiser
            priority: Si True, vide la queue et parle immédiatement
        """
        if not self.available or self._shutdown_requested:
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
        try:
            self.voice_queue.put(clean_text, timeout=1)
            print(f"[VOICE] Ajouté à la queue: {clean_text[:50]}...")
        except queue.Full:
            print("[VOICE] Queue pleine, message ignoré")
    
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
        text = re.sub(r'^🤖\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^👤\s*', '', text, flags=re.MULTILINE)
        
        # Nettoyer les caractères spéciaux
        text = text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def stop(self):
        """Arrête la synthèse vocale en cours"""
        if self.available and self.engine:
            try:
                if hasattr(self.engine, 'stop'):
                    self.engine.stop()
                
                # Vider la queue
                while not self.voice_queue.empty():
                    try:
                        self.voice_queue.get_nowait()
                        self.voice_queue.task_done()
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
        if not self.available or not self.engine:
            return
        
        try:
            if rate is not None:
                self.voice_config['rate'] = max(50, min(300, rate))  # Limiter la plage
                self.engine.setProperty('rate', self.voice_config['rate'])
                print(f"[VOICE] Vitesse: {self.voice_config['rate']} mots/min")
            
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
        if not self.available or not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            if not voices:
                return []
            
            voice_list = []
            for voice in voices:
                voice_info = {
                    'id': getattr(voice, 'id', ''),
                    'name': getattr(voice, 'name', 'Voix inconnue'),
                    'languages': getattr(voice, 'languages', [])
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            print(f"[ERROR VOICE] Erreur récupération voix: {e}")
            return []
    
    def test_voice(self, text: str = "Bonjour, je suis votre assistant IA !"):
        """Teste la synthèse vocale"""
        if self.available:
            self.speak(text, priority=True)
        else:
            print("[VOICE] Test impossible - moteur non disponible")
    
    def get_voice_info(self) -> dict:
        """Retourne les informations sur la configuration vocale"""
        return {
            'available': self.available,
            'speaking': self.speaking,
            'rate': self.voice_config['rate'],
            'volume': self.voice_config['volume'],
            'voice_id': self.voice_config['voice_id'],
            'queue_size': self.voice_queue.qsize(),
            'pyttsx3_available': PYTTSX3_AVAILABLE
        }
    
    def shutdown(self):
        """Arrête proprement le moteur vocal"""
        if not self.available:
            return
        
        print("[VOICE] Arrêt du moteur vocal...")
        self._shutdown_requested = True
        
        # Arrêter la synthèse en cours
        self.stop()
        
        # Signaler l'arrêt au worker
        try:
            self.voice_queue.put("STOP", timeout=1)
        except queue.Full:
            pass
        
        # Attendre l'arrêt du worker thread
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=3)
        
        # Nettoyer l'engine
        if self.engine:
            try:
                if hasattr(self.engine, 'stop'):
                    self.engine.stop()
            except:
                pass
            self.engine = None
        
        self.available = False
        print("[VOICE] Moteur vocal arrêté")


# Instance globale
voice_engine = VoiceEngine()