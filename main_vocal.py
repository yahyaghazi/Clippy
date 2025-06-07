#!/usr/bin/env python3
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
        
        print("\n📋 COMMANDES DISPONIBLES:")
        print("  'Assistant, prends une capture'")
        print("  'Assistant, clique à 500, 300'")
        print("  'Assistant, écris bonjour'")
        print("  'Assistant, scroll vers le bas'")
        print("\nAppuyez sur Ctrl+C pour quitter")
        
        try:
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n[ASSISTANT] Arrêt demandé")
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
