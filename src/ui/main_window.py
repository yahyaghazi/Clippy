"""
Fenêtre principale de l'assistant IA
Version stable et corrigée
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
from typing import Optional

from ..config.settings import settings
from ..core.ollama_client import OllamaClient
from ..core.system_monitor import SystemMonitor
from .character import CharacterWidget
from .speech_bubble import SpeechBubble
from .chat_widget import ChatWidget
from ..utils.voice_engine import voice_engine
from ..core.file_manager import file_manager

# Import optionnel de la reconnaissance vocale
try:
    from ..utils.speech_recognition_engine import SpeechRecognitionEngine
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️ Reconnaissance vocale non disponible")


class MainWindow:
    """Fenêtre principale de l'assistant"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.ollama_client: Optional[OllamaClient] = None
        self.system_monitor: Optional[SystemMonitor] = None
        self.speech_recognition_engine: Optional[SpeechRecognitionEngine] = None
        
        self.voice_enabled = True
        self.speech_listening = False
        self.chat_mode = False
        
        # Variables pour le déplacement
        self.start_x = 0
        self.start_y = 0
        
        # Widgets
        self.character_widget: Optional[CharacterWidget] = None
        self.speech_bubble: Optional[SpeechBubble] = None
        self.chat_widget: Optional[ChatWidget] = None
        
        self._setup_window()
        self._create_widgets()
        self._initialize_components()
    
    def _setup_window(self):
        """Configuration de la fenêtre"""
        self.root.title("Assistant IA")
        self.root.geometry(f"{settings.ui.window_width}x{settings.ui.window_height}")
        
        # Fenêtre flottante
        if settings.ui.always_on_top:
            self.root.wm_attributes("-topmost", True)
        
        self.root.overrideredirect(True)  # Sans bordure système
        
        # Position initiale
        self._position_window()
        
        # Couleur de fond
        self.root.configure(bg=settings.ui.background_color)
        
        # Gestion de la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
    
    def _position_window(self):
        """Positionne la fenêtre au coin bas-droit"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = screen_width - settings.ui.initial_x_offset
        y = screen_height - settings.ui.initial_y_offset
        
        self.root.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Création des widgets de l'interface"""
        # Frame principale
        main_frame = tk.Frame(
            self.root, 
            bg=settings.ui.background_color
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barre de titre (pour déplacement)
        self._create_title_bar(main_frame)
        
        # Widget personnage
        self.character_widget = CharacterWidget(
            main_frame, 
            size=settings.ui.character_size
        )
        self.character_widget.pack(pady=5)
        
        # Lien pour permettre au personnage de communiquer avec cette fenêtre
        self.root.main_window_instance = self
        
        # Bulle de dialogue
        self.speech_bubble = SpeechBubble(main_frame)
        self.speech_bubble.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Widget de chat
        self.chat_widget = ChatWidget(main_frame, self._on_chat_message)
        self.chat_widget.pack(fill=tk.X, pady=2)
        
        # Initialiser avec un message de bienvenue
        self._show_initial_message()
    
    def _create_title_bar(self, parent):
        """Crée la barre de titre"""
        title_frame = tk.Frame(parent, bg='#ddd', height=25)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        title_frame.pack_propagate(False)
        
        # Titre
        title_label = tk.Label(
            title_frame, 
            text="🤖 Assistant IA", 
            bg='#ddd', 
            font=('Arial', 9)
        )
        title_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Boutons de contrôle
        self._create_control_buttons(title_frame)
        
        # Bind pour déplacement
        title_frame.bind("<Button-1>", self._start_drag)
        title_frame.bind("<B1-Motion>", self._on_drag)
        title_label.bind("<Button-1>", self._start_drag)
        title_label.bind("<B1-Motion>", self._on_drag)
    
    def _create_control_buttons(self, parent):
        """Crée les boutons de contrôle"""
        button_style = {
            "font": ('Arial', 8),
            "width": 3,
            "height": 1,
            "cursor": "hand2"
        }
        
        # Bouton fermer
        close_btn = tk.Button(
            parent, 
            text="✕", 
            command=self.close_app,
            bg='#ff6b6b', 
            fg='white',
            **button_style
        )
        close_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Bouton minimiser
        minimize_btn = tk.Button(
            parent, 
            text="_", 
            command=self._minimize_window,
            bg='#ffa726', 
            fg='white',
            **button_style
        )
        minimize_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Bouton paramètres
        settings_btn = tk.Button(
            parent, 
            text="⚙️", 
            command=self._show_settings,
            bg='#4CAF50', 
            fg='white',
            **button_style
        )
        settings_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Bouton microphone (si disponible)
        if SPEECH_RECOGNITION_AVAILABLE:
            self.mic_btn = tk.Button(
                parent, 
                text="🎤", 
                command=self._toggle_speech_recognition,
                bg='#E91E63', 
                fg='white',
                **button_style
            )
            self.mic_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Bouton actualiser
        refresh_btn = tk.Button(
            parent, 
            text="🔄", 
            command=self._request_new_advice,
            bg='#2196F3', 
            fg='white',
            **button_style
        )
        refresh_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Bouton voice toggle
        self.voice_btn = tk.Button(
            parent, 
            text="🔊" if self.voice_enabled else "🔇", 
            command=self._toggle_voice,
            bg='#9C27B0' if self.voice_enabled else '#757575', 
            fg='white',
            **button_style
        )
        self.voice_btn.pack(side=tk.RIGHT, padx=2, pady=2)
    
    def _initialize_components(self):
        """Initialise les composants"""
        # Client Ollama
        self.ollama_client = OllamaClient()
        
        # Monitoring système
        self.system_monitor = SystemMonitor(self._on_app_changed)
        
        # Reconnaissance vocale (si disponible)
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.speech_engine = SpeechRecognitionEngine(self._on_speech_recognized)
                if self.speech_engine.available:
                    print("🎤 Reconnaissance vocale disponible")
                else:
                    print("❌ Reconnaissance vocale non disponible")
            except Exception as e:
                print(f"❌ Erreur reconnaissance vocale: {e}")
                self.speech_engine = None
        
        # Mettre à jour le message initial
        self._update_initial_message()
    
    def _show_initial_message(self):
        """Affiche le message initial"""
        initial_msg = "👋 Salut ! Je démarre...\n⏳ Initialisation en cours..."
        if self.speech_bubble:
            self.speech_bubble.update_text(initial_msg)
    
    def _update_initial_message(self):
        """Met à jour le message initial avec le statut des composants"""
        if not self.speech_bubble:
            return
        
        status_lines = ["👋 Salut ! Je surveille ton activité..."]
        
        # Statut Ollama
        if self.ollama_client and self.ollama_client.available:
            status_lines.append("🧠 IA connectée !")
        else:
            status_lines.append("⚠️ Démarre Ollama pour l'IA")
        
        # Statut monitoring
        status_lines.append("🔍 Surveillance active")
        status_lines.append("💬 Clique sur 💬 pour me parler !")
        
        # Statut microphone
        if SPEECH_RECOGNITION_AVAILABLE and hasattr(self, 'speech_engine') and self.speech_engine and self.speech_engine.available:
            status_lines.append("🎤 Micro prêt - Clic pour parler !")
        else:
            status_lines.append("❌ Micro non disponible")
        
        self.speech_bubble.update_text("\n".join(status_lines))
    
    def _on_app_changed(self, app_name: str, context: str):
        """Callback appelé quand l'application active change"""
        if self.chat_mode:
            return
        
        if settings.debug_mode:
            print(f"[DÉTECTION UI] {app_name} - {context}")
        
        # Afficher l'info de base immédiatement
        basic_message = f"📱 {app_name}\n🕒 {context}\n\n🤔 Analyse en cours..."
        self.root.after(0, lambda: self.speech_bubble.update_text(basic_message))
        
        # Animer le personnage
        if self.character_widget:
            self.root.after(0, lambda: self.character_widget.set_mood("thinking"))
        
        # Générer suggestion IA en arrière-plan
        def generate_ai_response():
            if self.ollama_client and self.ollama_client.available:
                suggestion = self.ollama_client.generate_suggestion(app_name, context)
                final_message = f"📱 {app_name}\n🕒 {context}\n\n💡 {suggestion}"
            else:
                final_message = f"📱 {app_name}\n🕒 {context}\n\n🔌 IA non disponible"
            
            self.root.after(0, lambda: self._update_ai_response(final_message))
        
        # Lancer l'IA dans un thread séparé
        threading.Thread(target=generate_ai_response, daemon=True).start()
    
    def _update_ai_response(self, message: str):
        """Met à jour l'interface avec la réponse de l'IA (surveillance)"""
        if self.speech_bubble:
            self.speech_bubble.update_text(message)
        
        # Animer le personnage
        if self.character_widget:
            self.character_widget.set_mood("happy")
        
        # Synthèse vocale si activée
        if self.voice_enabled and voice_engine.available:
            suggestion_text = self._extract_suggestion_from_message(message)
            if suggestion_text:
                voice_engine.speak(suggestion_text)
    
    def _extract_suggestion_from_message(self, message: str) -> str:
        """Extrait la suggestion IA du message complet"""
        lines = message.split('\n')
        for line in lines:
            if line.startswith('💡'):
                return line.replace('💡', '').strip()
        return ""
    
    def _on_chat_message(self, message: str):
        """Callback appelé quand l'utilisateur envoie un message dans le chat"""
        print(f"[CHAT UI] Message reçu: {message}")
        
        # Passer en mode chat
        self.chat_mode = True
        
        # Afficher que l'IA réfléchit
        thinking_msg = f"💬 Vous: {message}\n\n🤔 L'IA analyse..."
        self.speech_bubble.update_text(thinking_msg)
        
        # Animer le personnage
        if self.character_widget:
            self.character_widget.set_mood("thinking")
        
        # Générer réponse IA
        def generate_chat_response():
            # Détecter les commandes de fichiers
            file_keywords = [
                "crée", "créer", "génère", "générer", "fichier", "script", "code",
                "lance", "lancer", "ouvre", "ouvrir", "exécute", "exécuter",
                "déplace", "déplacer", "supprime", "supprimer", "modifie", "modifier",
                "liste", "lister", "affiche", "afficher", "pdf", "rapport"
            ]
            
            is_file_command = any(keyword in message.lower() for keyword in file_keywords)
            
            if is_file_command:
                print("[CHAT] Commande de fichier détectée")
                try:
                    result = file_manager.process_command(message)
                    final_message = f"💬 Vous: {message}\n\n📁 Assistant: {result}"
                except Exception as e:
                    print(f"[CHAT ERROR] Erreur gestionnaire: {e}")
                    final_message = f"💬 Vous: {message}\n\n❌ Erreur: {str(e)}"
            
            else:
                # Conversation normale
                if self.ollama_client and self.ollama_client.available:
                    try:
                        chat_prompt = f"L'utilisateur te dit: '{message}'. Réponds de manière naturelle et utile en 1-2 phrases maximum."
                        
                        import requests
                        payload = {
                            "model": self.ollama_client.model,
                            "prompt": chat_prompt,
                            "stream": False,
                            "options": {
                                "temperature": 0.8,
                                "num_predict": 150
                            }
                        }
                        
                        response = requests.post(
                            f"{self.ollama_client.base_url}/api/generate",
                            json=payload,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            ai_response = result.get("response", "").strip()
                            
                            if ai_response:
                                final_message = f"💬 Vous: {message}\n\n🤖 Assistant: {ai_response}"
                            else:
                                final_message = f"💬 Vous: {message}\n\n🤖 Assistant: Je n'ai pas de réponse pour le moment."
                        else:
                            final_message = f"💬 Vous: {message}\n\n❌ Erreur de communication avec l'IA"
                    
                    except Exception as e:
                        print(f"[CHAT ERROR] Erreur génération IA: {e}")
                        final_message = f"💬 Vous: {message}\n\n❌ Erreur: {str(e)}"
                else:
                    final_message = f"💬 Vous: {message}\n\n🔌 IA non disponible - Démarrez Ollama"
            
            # Mettre à jour l'UI dans le thread principal
            self.root.after(0, lambda: self._update_chat_response(final_message))
        
        # Lancer la génération en arrière-plan
        threading.Thread(target=generate_chat_response, daemon=True).start()
    
    def _update_chat_response(self, message: str):
        """Met à jour l'interface avec la réponse du chat"""
        if self.speech_bubble:
            self.speech_bubble.update_text(message)
        
        # Animer le personnage
        if self.character_widget:
            self.character_widget.set_mood("happy")
        
        # Synthèse vocale si activée
        if self.voice_enabled and voice_engine.available:
            lines = message.split('\n')
            for line in lines:
                if line.startswith('🤖 Assistant:') or line.startswith('📁 Assistant:'):
                    ai_text = line.split(':', 1)[1].strip()
                    voice_engine.speak(ai_text)
                    break
        
        # Réactiver les contrôles du chat
        if self.chat_widget:
            self.chat_widget.on_response_received()
        
        # Retour surveillance après 30 secondes
        def return_to_monitoring():
            self.chat_mode = False
            print("[CHAT] Retour au mode surveillance automatique")
        
        self.root.after(30000, return_to_monitoring)
    
    def _start_drag(self, event):
        """Début du déplacement de la fenêtre"""
        self.start_x = event.x_root
        self.start_y = event.y_root
    
    def _on_drag(self, event):
        """Déplacement de la fenêtre"""
        x = self.root.winfo_x() + (event.x_root - self.start_x)
        y = self.root.winfo_y() + (event.y_root - self.start_y)
        self.root.geometry(f"+{x}+{y}")
        self.start_x = event.x_root
        self.start_y = event.y_root
    
    def _toggle_voice(self):
        """Active/désactive la synthèse vocale"""
        self.voice_enabled = not self.voice_enabled
        
        if self.voice_enabled:
            self.voice_btn.config(text="🔊", bg='#9C27B0')
            if voice_engine.available:
                voice_engine.speak("Synthèse vocale activée !", priority=True)
            print("[VOICE UI] Synthèse vocale activée")
        else:
            self.voice_btn.config(text="🔇", bg='#757575')
            voice_engine.stop()
            print("[VOICE UI] Synthèse vocale désactivée")
    
    def _toggle_speech_recognition(self):
        """Active/désactive la reconnaissance vocale"""
        if not hasattr(self, 'speech_engine') or not self.speech_engine or not self.speech_engine.available:
            self.speech_bubble.update_text("❌ Microphone non disponible\nVérifiez vos périphériques audio")
            return
        
        if self.speech_listening:
            # Arrêter l'écoute
            self.speech_engine.stop_continuous_listening()
            self.speech_listening = False
            self.mic_btn.config(text="🎤", bg='#E91E63')
            print("[SPEECH UI] Écoute vocale désactivée")
            
            # Message d'arrêt
            if self.speech_bubble:
                self.speech_bubble.update_text("🔇 Écoute vocale arrêtée\nCliquez sur 🎤 pour réactiver")
        else:
            # Démarrer l'écoute
            if self.speech_engine.start_continuous_listening():
                self.speech_listening = True
                self.mic_btn.config(text="🔇", bg='#4CAF50')  # Vert quand actif
                print("[SPEECH UI] Écoute vocale activée")
                
                # Message de démarrage
                if self.speech_bubble:
                    self.speech_bubble.update_text("🎤 Écoute vocale active\nParlez maintenant !\n\nDites 'stop' pour arrêter")
                
                # Synthèse vocale de confirmation
                if self.voice_enabled and voice_engine.available:
                    voice_engine.speak("Écoute vocale activée, je vous écoute !")
            else:
                print("[SPEECH UI] Impossible de démarrer l'écoute")
    
    def _on_speech_recognized(self, text: str):
        """Callback appelé quand de la parole est reconnue"""
        print(f"[SPEECH UI] Parole reconnue: {text}")
        
        # Mettre à jour l'interface dans le thread principal
        self.root.after(0, lambda: self._process_speech_input(text))
    
    def _process_speech_input(self, text: str):
        """Traite l'entrée vocale reconnue"""
        text_lower = text.lower()
        
        # Commandes de contrôle vocal
        if any(word in text_lower for word in ["stop", "arrête", "silence"]):
            self._toggle_speech_recognition()
            return
        
        if "nouveau conseil" in text_lower or "actualise" in text_lower:
            self._request_new_advice()
            return
        
        if "ferme" in text_lower and "assistant" in text_lower:
            self.close_app()
            return
        
        # Traiter comme un message de chat
        if self.chat_widget:
            self.chat_widget.message_entry.delete(0, tk.END)
            self.chat_widget.message_entry.insert(0, text)
            self.chat_widget.send_message()
        else:
            self._on_chat_message(text)
    
    def _request_new_advice(self):
        """Demande un nouveau conseil pour l'application actuelle"""
        print("[MANUAL] Demande manuelle d'un nouveau conseil")
        
        # Sortir du mode chat
        self.chat_mode = False
        
        if self.system_monitor and self.system_monitor.current_app:
            app_name = self.system_monitor.current_app
            context = f"Nouveau conseil demandé ({time.strftime('%H:%M')})"
            self._on_app_changed(app_name, context)
        else:
            self._on_app_changed("Système", "Conseil général demandé")
    
    def _minimize_window(self):
        """Cache temporairement la fenêtre"""
        self.root.withdraw()
        # Réapparaître après 3 secondes
        self.root.after(3000, lambda: self.root.deiconify())
    
    def _show_settings(self):
        """Affiche la fenêtre de paramètres"""
        chat_status = "ouvert" if (self.chat_widget and self.chat_widget.is_visible()) else "fermé"
        
        messagebox.showinfo(
            "Paramètres", 
            f"Assistant IA v1.0\n\n"
            f"Modèle: {settings.ollama.model}\n"
            f"Statut IA: {'✅ Connecté' if self.ollama_client.available else '❌ Déconnecté'}\n"
            f"Intervalle: {settings.monitoring.check_interval}s\n"
            f"Mode: {'💬 Chat' if self.chat_mode else '🔍 Surveillance'}\n"
            f"Chat: {chat_status}\n"
            f"Voix: {'✅ Activée' if self.voice_enabled else '❌ Désactivée'}"
        )
    
    def start_monitoring(self):
        """Démarre la surveillance système"""
        if self.system_monitor:
            self.system_monitor.start()
            # Forcer une première détection après 2 secondes
            self.root.after(2000, self._force_initial_detection)
    
    def _force_initial_detection(self):
        """Force une première détection pour déclencher l'IA"""
        if self.system_monitor:
            print("[FORCE] Déclenchement initial de l'IA...")
            self._on_app_changed("Système", "Démarrage de l'assistant")
    
    def stop_monitoring(self):
        """Arrête la surveillance système"""
        if self.system_monitor:
            self.system_monitor.stop()
    
    def run(self):
        """Lance l'application"""
        print("🤖 Assistant IA démarré !")
        print(f"- Fenêtre flottante: {settings.ui.window_width}x{settings.ui.window_height}")
        print(f"- IA: {'✅' if self.ollama_client.available else '❌'}")
        print("- Glissez la barre de titre pour déplacer")
        print("- Cliquez sur 💬 pour discuter avec l'IA")
        
        # Démarrer la surveillance
        self.start_monitoring()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.close_app()
    
    def close_app(self):
        """Fermeture propre de l'application"""
        print("🔄 Fermeture de l'assistant...")
        
        # Arrêter la reconnaissance vocale
        if hasattr(self, 'speech_engine') and self.speech_engine:
            self.speech_engine.stop_continuous_listening()
        
        # Arrêter la synthèse vocale
        voice_engine.shutdown()
        
        # Arrêter la surveillance
        self.stop_monitoring()
        
        # Fermer la fenêtre
        self.root.quit()
        self.root.destroy()
        
        print("👋 Assistant fermé !")