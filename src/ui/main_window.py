"""
Fenêtre principale de l'assistant IA
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
from ..utils.voice_engine import voice_engine


class MainWindow:
    """Fenêtre principale de l'assistant"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.ollama_client: Optional[OllamaClient] = None
        self.system_monitor: Optional[SystemMonitor] = None
        
        self.voice_enabled = True  # État du mode vocal
        
        # Variables pour le déplacement
        self.start_x = 0
        self.start_y = 0
        
        # Widgets
        self.character_widget: Optional[CharacterWidget] = None
        self.speech_bubble: Optional[SpeechBubble] = None
        
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
        
        # Position initiale (coin bas-droit)
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
        """Crée les boutons de contrôle (minimiser, fermer)"""
        # Bouton paramètres
        settings_btn = tk.Button(
            parent, 
            text="⚙️", 
            command=self._show_settings,
            bg='#4CAF50', 
            fg='white', 
            font=('Arial', 8),
            width=3, 
            height=1
        )
        settings_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Bouton fermer
        close_btn = tk.Button(
            parent, 
            text="✕", 
            command=self.close_app,
            bg='#ff6b6b', 
            fg='white', 
            font=('Arial', 8),
            width=3, 
            height=1
        )
        close_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Bouton minimiser (désactivé pour fenêtre sans bordure)
        minimize_btn = tk.Button(
            parent, 
            text="_", 
            command=self._minimize_window,  # Fonction personnalisée
            bg='#ffa726', 
            fg='white', 
            font=('Arial', 8),
            width=3, 
            height=1
        )
        minimize_btn.pack(side=tk.RIGHT, padx=2, pady=2)
    
    def _initialize_components(self):
        """Initialise les composants (Ollama, monitoring)"""
        # Client Ollama
        self.ollama_client = OllamaClient()
        
        # Monitoring système
        self.system_monitor = SystemMonitor(self._on_app_changed)
        
        # Mettre à jour le message initial avec le statut
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
        
        self.speech_bubble.update_text("\n".join(status_lines))
    
    def _on_app_changed(self, app_name: str, context: str):
        """Callback appelé quand l'application active change"""
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
            if self.ollama_client:
                suggestion = self.ollama_client.generate_suggestion(app_name, context)
                final_message = f"📱 {app_name}\n🕒 {context}\n\n💡 {suggestion}"
                
                # Mettre à jour l'UI dans le thread principal
                self.root.after(0, lambda: self._update_ai_response(final_message))
            else:
                fallback_msg = f"📱 {app_name}\n🕒 {context}\n\n🔌 IA non disponible"
                self.root.after(0, lambda: self.speech_bubble.update_text(fallback_msg))
        
        # Lancer l'IA dans un thread séparé
        threading.Thread(target=generate_ai_response, daemon=True).start()
    
    def _update_ai_response(self, message: str):
        """Met à jour l'interface avec la réponse de l'IA"""
        print(f"[DEBUG UI] Mise à jour bulle avec: {message[:100]}...")  # Debug
        
        if self.speech_bubble:
            self.speech_bubble.update_text(message)
            print("[DEBUG UI] Bulle mise à jour")
        else:
            print("[ERROR UI] speech_bubble est None !")
        
        # Animer le personnage
        if self.character_widget:
            self.character_widget.set_mood("happy")
            print("[DEBUG UI] Personnage mis en mode happy")
        
        # Synthèse vocale si activée
        if self.voice_enabled and voice_engine.available:
            # Extraire seulement la suggestion (partie après 💡)
            suggestion_text = self._extract_suggestion_from_message(message)
            if suggestion_text:
                voice_engine.speak(suggestion_text)
                print(f"[VOICE UI] Synthèse: {suggestion_text[:50]}...")
    
    def _extract_suggestion_from_message(self, message: str) -> str:
        """Extrait la suggestion IA du message complet"""
        lines = message.split('\n')
        for line in lines:
            if line.startswith('💡'):
                return line.replace('💡', '').strip()
        return ""
    
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
    
    def _request_new_advice(self):
        """Demande un nouveau conseil pour l'application actuelle"""
        print("[MANUAL] Demande manuelle d'un nouveau conseil")
        
        if self.system_monitor and self.system_monitor.current_app:
            app_name = self.system_monitor.current_app
            context = f"Nouveau conseil demandé ({time.strftime('%H:%M')})"
            
            # Déclencher l'IA manuellement
            self._on_app_changed(app_name, context)
        else:
            # Fallback si pas d'app détectée
            self._on_app_changed("Système", "Conseil général demandé")
    
    def _minimize_window(self):
        """Cache temporairement la fenêtre"""
        self.root.withdraw()
        # Réapparaître après 3 secondes (ou ajouter un raccourci clavier)
        self.root.after(3000, lambda: self.root.deiconify())
    
    def _show_settings(self):
        """Affiche la fenêtre de paramètres"""
        # TODO: Implémenter une fenêtre de paramètres
        messagebox.showinfo(
            "Paramètres", 
            f"Assistant IA v0.1\n\n"
            f"Modèle: {settings.ollama.model}\n"
            f"Statut IA: {'✅ Connecté' if self.ollama_client.available else '❌ Déconnecté'}\n"
            f"Intervalle: {settings.monitoring.check_interval}s"
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
            # Simuler un changement d'app pour déclencher l'IA
            print("[FORCE] Déclenchement initial de l'IA...")
            self._on_app_changed("Opera", "Navigation web (test initial)")
    
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
        
        # Démarrer la surveillance
        self.start_monitoring()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.close_app()
    
    def close_app(self):
        """Fermeture propre de l'application"""
        print("🔄 Fermeture de l'assistant...")
        
        # Arrêter la synthèse vocale
        voice_engine.shutdown()
        
        # Arrêter la surveillance
        self.stop_monitoring()
        
        # Fermer la fenêtre
        self.root.quit()
        self.root.destroy()
        
        print("👋 Assistant fermé !")