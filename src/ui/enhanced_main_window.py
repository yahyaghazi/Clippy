"""
Fenêtre principale améliorée avec toutes les fonctionnalités Clippy
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import time
import os
from typing import Optional

from ..config.settings import settings
from ..core.ollama_client import OllamaClient
from ..core.system_monitor import SystemMonitor
from .character import CharacterWidget
from .speech_bubble import SpeechBubble
from .chat_widget import ChatWidget
from ..utils.voice_engine import voice_engine
from ..core.enhanced_file_manager import enhanced_file_manager
from ..utils.speech_recognition_engine import SpeechRecognitionEngine


class EnhancedMainWindow:
    """Fenêtre principale avec toutes les fonctionnalités avancées"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.ollama_client: Optional[OllamaClient] = None
        self.system_monitor: Optional[SystemMonitor] = None
        self.speech_recognition_engine: Optional[SpeechRecognitionEngine] = None
        
        # États de l'interface
        self.voice_enabled = True
        self.speech_listening = False
        self.chat_mode = False
        self.advanced_mode = False  # Mode avancé avec fenêtre étendue
        
        # Variables pour le déplacement
        self.start_x = 0
        self.start_y = 0
        
        # Widgets
        self.character_widget: Optional[CharacterWidget] = None
        self.speech_bubble: Optional[SpeechBubble] = None
        self.chat_widget: Optional[ChatWidget] = None
        self.advanced_panel: Optional[tk.Frame] = None
        
        # Animation Clippy
        self.animation_frames = []
        self.animation_index = 0
        
        self._setup_window()
        self._load_clippy_images()
        self._create_widgets()
        self._initialize_components()
    
    def _setup_window(self):
        """Configuration de la fenêtre"""
        self.root.title("Assistant IA - Clippy Moderne")
        
        # Taille adaptative
        base_width = settings.ui.window_width
        base_height = settings.ui.window_height + 100  # Plus grand pour les nouvelles fonctionnalités
        
        self.root.geometry(f"{base_width}x{base_height}")
        
        # Fenêtre flottante
        if settings.ui.always_on_top:
            self.root.wm_attributes("-topmost", True)
        
        self.root.overrideredirect(True)  # Sans bordure système
        
        # Position initiale
        self._position_window()
        
        # Style moderne
        self.root.configure(bg="#f8f9fa")
        
        # Gestion fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
    
    def _position_window(self):
        """Positionne la fenêtre intelligemment"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Coin bas-droit mais pas collé au bord
        x = screen_width - settings.ui.initial_x_offset - 50
        y = screen_height - settings.ui.initial_y_offset - 100
        
        self.root.geometry(f"+{x}+{y}")
    
    def _load_clippy_images(self):
        """Charge les images d'animation de Clippy"""
        try:
            # Chercher les images dans le dossier de base
            base_dir = enhanced_file_manager.base_directory
            
            # Images d'animation
            frame_files = ["frame1.png", "frame2.png", "frame3.png"]
            for frame_file in frame_files:
                frame_path = os.path.join(base_dir, frame_file)
                if os.path.exists(frame_path):
                    img = Image.open(frame_path).resize((80, 80), Image.Resampling.LANCZOS)
                    self.animation_frames.append(ImageTk.PhotoImage(img))
            
            # Image Clippy principale
            clippy_path = os.path.join(base_dir, "clippy.jpg")
            if os.path.exists(clippy_path):
                img = Image.open(clippy_path).resize((80, 80), Image.Resampling.LANCZOS)
                self.clippy_image = ImageTk.PhotoImage(img)
            else:
                self.clippy_image = None
            
            print(f"[CLIPPY] {len(self.animation_frames)} frames d'animation chargées")
            
        except Exception as e:
            print(f"[CLIPPY] Erreur chargement images : {e}")
            self.animation_frames = []
            self.clippy_image = None
    
    def _create_widgets(self):
        """Création de l'interface moderne"""
        # Frame principal avec gradient simulé
        main_frame = tk.Frame(self.root, bg="#f8f9fa", relief=tk.RAISED, bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Barre de titre moderne
        self._create_modern_title_bar(main_frame)
        
        # Zone personnage avec animation Clippy
        self._create_character_area(main_frame)
        
        # Bulle de dialogue améliorée
        self.speech_bubble = SpeechBubble(main_frame)
        self.speech_bubble.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Widget de chat intégré
        self.chat_widget = ChatWidget(main_frame, self._on_chat_message)
        self.chat_widget.pack(fill=tk.X, pady=2)
        
        # Panel avancé (caché par défaut)
        self._create_advanced_panel(main_frame)
        
        # Lien pour communications
        self.root.main_window_instance = self
        
        # Message de bienvenue avec style Clippy
        self._show_clippy_welcome()
    
    def _create_modern_title_bar(self, parent):
        """Barre de titre moderne avec gradient"""
        title_frame = tk.Frame(parent, bg="#343a40", height=30)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        title_frame.pack_propagate(False)
        
        # Titre avec icône
        title_label = tk.Label(
            title_frame,
            text="📎 Assistant Clippy IA",
            bg="#343a40",
            fg="white",
            font=("Segoe UI", 10, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=8, pady=5)
        
        # Boutons de contrôle modernes
        self._create_modern_control_buttons(title_frame)
        
        # Bind pour déplacement
        title_frame.bind("<Button-1>", self._start_drag)
        title_frame.bind("<B1-Motion>", self._on_drag)
        title_label.bind("<Button-1>", self._start_drag)
        title_label.bind("<B1-Motion>", self._on_drag)
    
    def _create_modern_control_buttons(self, parent):
        """Boutons de contrôle avec style moderne"""
        button_style = {
            "font": ("Segoe UI", 8),
            "width": 3,
            "height": 1,
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2"
        }
        
        # Bouton mode avancé
        self.advanced_btn = tk.Button(
            parent,
            text="🔧",
            command=self._toggle_advanced_mode,
            bg="#17a2b8",
            fg="white",
            **button_style
        )
        self.advanced_btn.pack(side=tk.RIGHT, padx=1, pady=3)
        
        # Bouton fermer
        close_btn = tk.Button(
            parent,
            text="✕",
            command=self.close_app,
            bg="#dc3545",
            fg="white",
            **button_style
        )
        close_btn.pack(side=tk.RIGHT, padx=1, pady=3)
        
        # Bouton minimiser
        minimize_btn = tk.Button(
            parent,
            text="_",
            command=self._minimize_window,
            bg="#ffc107",
            fg="black",
            **button_style
        )
        minimize_btn.pack(side=tk.RIGHT, padx=1, pady=3)
        
        # Bouton microphone
        self.mic_btn = tk.Button(
            parent,
            text="🎤",
            command=self._toggle_speech_recognition,
            bg="#e83e8c",
            fg="white",
            **button_style
        )
        self.mic_btn.pack(side=tk.RIGHT, padx=1, pady=3)
        
        # Bouton actualiser
        refresh_btn = tk.Button(
            parent,
            text="🔄",
            command=self._request_new_advice,
            bg="#007bff",
            fg="white",
            **button_style
        )
        refresh_btn.pack(side=tk.RIGHT, padx=1, pady=3)
        
        # Bouton voice
        self.voice_btn = tk.Button(
            parent,
            text="🔊" if self.voice_enabled else "🔇",
            command=self._toggle_voice,
            bg="#6f42c1" if self.voice_enabled else "#6c757d",
            fg="white",
            **button_style
        )
        self.voice_btn.pack(side=tk.RIGHT, padx=1, pady=3)
        
        # Bouton paramètres
        settings_btn = tk.Button(
            parent,
            text="⚙️",
            command=self._show_enhanced_settings,
            bg="#28a745",
            fg="white",
            **button_style
        )
        settings_btn.pack(side=tk.RIGHT, padx=1, pady=3)
    
    def _create_character_area(self, parent):
        """Zone personnage avec Clippy animé"""
        char_frame = tk.Frame(parent, bg="#f8f9fa")
        char_frame.pack(pady=5)
        
        # Label pour Clippy avec animation
        self.clippy_label = tk.Label(
            char_frame,
            bg="#f8f9fa",
            cursor="hand2"
        )
        self.clippy_label.pack()
        
        # Bind clic sur Clippy
        self.clippy_label.bind("<Button-1>", self._on_clippy_click)
        
        # Démarrer animation
        self._start_clippy_animation()
    
    def _create_advanced_panel(self, parent):
        """Panel avancé avec fonctionnalités étendues"""
        self.advanced_panel = tk.Frame(parent, bg="#e9ecef", relief=tk.SUNKEN, bd=1)
        
        # Titre du panel
        title_label = tk.Label(
            self.advanced_panel,
            text="🔧 Fonctionnalités Avancées",
            bg="#e9ecef",
            font=("Segoe UI", 9, "bold"),
            fg="#495057"
        )
        title_label.pack(pady=5)
        
        # Boutons fonctionnalités avancées
        self._create_advanced_buttons()
        
        # Zone d'informations système
        self._create_system_info_area()
        
        # Historique des commandes
        self._create_history_area()
    
    def _create_advanced_buttons(self):
        """Boutons pour fonctionnalités avancées"""
        btn_frame = tk.Frame(self.advanced_panel, bg="#e9ecef")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        button_style = {
            "font": ("Segoe UI", 8),
            "relief": tk.RAISED,
            "bd": 1,
            "cursor": "hand2",
            "width": 12
        }
        
        # Ligne 1
        row1 = tk.Frame(btn_frame, bg="#e9ecef")
        row1.pack(fill=tk.X, pady=2)
        
        tk.Button(
            row1,
            text="📄 Résumer PDF",
            command=lambda: self._quick_action("resumer"),
            bg="#17a2b8",
            fg="white",
            **button_style
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            row1,
            text="🌐 Web → PDF",
            command=lambda: self._quick_action("webscraping"),
            bg="#28a745",
            fg="white",
            **button_style
        ).pack(side=tk.LEFT, padx=2)
        
        # Ligne 2
        row2 = tk.Frame(btn_frame, bg="#e9ecef")
        row2.pack(fill=tk.X, pady=2)
        
        tk.Button(
            row2,
            text="📝 Générer Doc",
            command=lambda: self._quick_action("generer"),
            bg="#fd7e14",
            fg="white",
            **button_style
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            row2,
            text="🗂️ Lister Fichiers",
            command=lambda: self._quick_action("lister"),
            bg="#6f42c1",
            fg="white",
            **button_style
        ).pack(side=tk.LEFT, padx=2)
        
        # Ligne 3
        row3 = tk.Frame(btn_frame, bg="#e9ecef")
        row3.pack(fill=tk.X, pady=2)
        
        tk.Button(
            row3,
            text="🔤 Traduire",
            command=lambda: self._quick_action("traduire"),
            bg="#dc3545",
            fg="white",
            **button_style
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            row3,
            text="📋 Historique",
            command=lambda: self._quick_action("historique"),
            bg="#6c757d",
            fg="white",
            **button_style
        ).pack(side=tk.LEFT, padx=2)
    
    def _create_system_info_area(self):
        """Zone d'informations système"""
        info_frame = tk.LabelFrame(
            self.advanced_panel,
            text="💻 Informations Système",
            bg="#e9ecef",
            font=("Segoe UI", 8),
            fg="#495057"
        )
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.system_info_text = tk.Text(
            info_frame,
            height=4,
            font=("Consolas", 8),
            bg="#ffffff",
            fg="#212529",
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.system_info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Mettre à jour les infos
        self._update_system_info()
    
    def _create_history_area(self):
        """Zone historique des commandes"""
        history_frame = tk.LabelFrame(
            self.advanced_panel,
            text="📝 Dernières Commandes",
            bg="#e9ecef",
            font=("Segoe UI", 8),
            fg="#495057"
        )
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            height=6,
            font=("Consolas", 8),
            bg="#ffffff",
            fg="#212529",
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _start_clippy_animation(self):
        """Démarre l'animation de Clippy"""
        if self.animation_frames:
            self._animate_clippy()
        elif self.clippy_image:
            self.clippy_label.config(image=self.clippy_image)
    
    def _animate_clippy(self):
        """Animation continue de Clippy"""
        if self.animation_frames and hasattr(self, 'clippy_label'):
            frame = self.animation_frames[self.animation_index]
            self.clippy_label.config(image=frame)
            self.animation_index = (self.animation_index + 1) % len(self.animation_frames)
            
            # Programmer la prochaine frame
            self.root.after(500, self._animate_clippy)  # Animation plus lente
    
    def _show_clippy_welcome(self):
        """Message de bienvenue style Clippy"""
        welcome_msg = (
            "👋 Salut ! Je suis Clippy, votre assistant IA moderne !\n\n"
            "🎯 Je peux :\n"
            "• 💬 Discuter avec vous\n"
            "• 📁 Gérer vos fichiers\n"
            "• 🌐 Rechercher sur le web\n"
            "• 📄 Créer des documents\n"
            "• 🎤 Vous écouter\n\n"
            "Cliquez sur 💬 pour me parler ou sur 🔧 pour plus d'options !"
        )
        
        if self.speech_bubble:
            self.speech_bubble.update_text(welcome_msg)
    
    def _initialize_components(self):
        """Initialise tous les composants"""
        # Client Ollama
        self.ollama_client = OllamaClient()
        
        # Monitoring système
        self.system_monitor = SystemMonitor(self._on_app_changed)
        
        # Reconnaissance vocale
        try:
            self.speech_engine = SpeechRecognitionEngine(self._on_speech_recognized)
            if self.speech_engine.available:
                print("🎤 Reconnaissance vocale disponible")
            else:
                print("❌ Reconnaissance vocale non disponible")
        except Exception as e:
            print(f"❌ Erreur reconnaissance vocale: {e}")
            self.speech_engine = None
        
        # Mettre à jour les infos système
        self._update_system_status()
    
    def _update_system_status(self):
        """Met à jour le statut système"""
        if not self.speech_bubble:
            return
        
        status_lines = ["📎 Clippy IA Moderne - Prêt !"]
        
        # Statut IA
        if self.ollama_client and self.ollama_client.available:
            status_lines.append("🧠 IA connectée et opérationnelle")
        else:
            status_lines.append("⚠️ IA déconnectée - Démarrez Ollama")
        
        # Statut surveillance
        status_lines.append("🔍 Surveillance des applications active")
        
        # Statut micro
        if self.speech_engine and self.speech_engine.available:
            status_lines.append("🎤 Microphone prêt")
        else:
            status_lines.append("❌ Microphone non disponible")
        
        # Fonctionnalités avancées
        status_lines.append("🔧 Fonctionnalités avancées disponibles")
        
        self.speech_bubble.update_text("\n".join(status_lines))
    
    def _toggle_advanced_mode(self):
        """Bascule le mode avancé"""
        self.advanced_mode = not self.advanced_mode
        
        if self.advanced_mode:
            # Afficher le panel avancé
            self.advanced_panel.pack(fill=tk.BOTH, expand=True, pady=5)
            self.advanced_btn.config(bg="#fd7e14", text="🔧")
            
            # Agrandir la fenêtre
            current_geom = self.root.geometry()
            width, height_pos = current_geom.split('x')
            height, pos = height_pos.split('+', 1)
            new_height = int(height) + 300
            self.root.geometry(f"{width}x{new_height}+{'+'.join(pos)}")
            
            # Mettre à jour les infos
            self._update_system_info()
            self._update_history_display()
            
        else:
            # Cacher le panel avancé
            self.advanced_panel.pack_forget()
            self.advanced_btn.config(bg="#17a2b8", text="🔧")
            
            # Réduire la fenêtre
            current_geom = self.root.geometry()
            width, height_pos = current_geom.split('x')
            height, pos = height_pos.split('+', 1)
            new_height = int(height) - 300
            self.root.geometry(f"{width}x{new_height}+{'+'.join(pos)}")
    
    def _update_system_info(self):
        """Met à jour les informations système"""
        if not hasattr(self, 'system_info_text'):
            return
        
        try:
            import psutil
            
            info_text = (
                f"CPU: {psutil.cpu_percent()}% | "
                f"RAM: {psutil.virtual_memory().percent}%\n"
                f"Disque: {psutil.disk_usage('/').percent}%\n"
                f"IA: {'✅ Connectée' if self.ollama_client.available else '❌ Déconnectée'}\n"
                f"Fichiers: {len(os.listdir(enhanced_file_manager.base_directory))} dans le dossier"
            )
            
            self.system_info_text.config(state=tk.NORMAL)
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(1.0, info_text)
            self.system_info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Erreur mise à jour système : {e}")
    
    def _update_history_display(self):
        """Met à jour l'affichage de l'historique"""
        if not hasattr(self, 'history_text'):
            return
        
        try:
            history = enhanced_file_manager.get_history(5)
            
            self.history_text.config(state=tk.NORMAL)
            self.history_text.delete(1.0, tk.END)
            self.history_text.insert(1.0, history)
            self.history_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Erreur mise à jour historique : {e}")
    
    def _quick_action(self, action_type: str):
        """Actions rapides depuis les boutons avancés"""
        if action_type == "resumer":
            filename = tk.simpledialog.askstring("Résumer", "Nom du fichier à résumer :")
            if filename:
                self._process_file_command(f"résume le document {filename}")
        
        elif action_type == "webscraping":
            topic = tk.simpledialog.askstring("Web Research", "Sujet à rechercher :")
            if topic:
                self._process_file_command(f"cherche des infos sur {topic} et crée un PDF")
        
        elif action_type == "generer":
            instruction = tk.simpledialog.askstring("Générer", "Type de document à générer :")
            if instruction:
                self._process_file_command(f"génère un document {instruction}")
        
        elif action_type == "lister":
            dossier = tk.simpledialog.askstring("Lister", "Dossier à lister (vide = racine) :")
            self._process_file_command(f"liste les fichiers {dossier or ''}")
        
        elif action_type == "traduire":
            texte = tk.simpledialog.askstring("Traduire", "Texte à traduire :")
            if texte:
                self._process_file_command(f"traduis : {texte}")
        
        elif action_type == "historique":
            self._process_file_command("affiche l'historique")
    
    def _process_file_command(self, command: str):
        """Traite une commande via le gestionnaire de fichiers"""
        def process():
            try:
                result = enhanced_file_manager.process_command(command)
                self.root.after(0, lambda: self._show_file_result(result))
            except Exception as e:
                self.root.after(0, lambda: self._show_file_result(f"❌ Erreur : {e}"))
        
        threading.Thread(target=process, daemon=True).start()
        
        # Afficher un message de traitement
        self.speech_bubble.update_text("🔄 Traitement en cours...")
    
    def _show_file_result(self, result: str):
        """Affiche le résultat d'une opération fichier"""
        self.speech_bubble.update_text(result)
        
        # Mettre à jour l'historique si en mode avancé
        if self.advanced_mode:
            self._update_history_display()
        
        # Synthèse vocale si activée
        if self.voice_enabled and voice_engine.available:
            # Nettoyer le résultat pour la voix
            clean_result = result.replace("📄", "").replace("❌", "Erreur").replace("✅", "Succès")
            voice_engine.speak(clean_result[:100])  # Limiter la longueur
    
    def _on_clippy_click(self, event):
        """Clic sur Clippy pour nouveau conseil"""
        print("[CLIPPY] Clic sur Clippy - nouveau conseil")
        self._request_new_advice()
    
    def _on_app_changed(self, app_name: str, context: str):
        """Callback changement d'application (surveillance)"""
        if self.chat_mode:
            return
        
        if settings.debug_mode:
            print(f"[APP CHANGE] {app_name} - {context}")
        
        # Afficher info immédiate
        basic_message = f"📱 {app_name}\n🕒 {context}\n\n🤔 Clippy analyse..."
        self.speech_bubble.update_text(basic_message)
        
        # Générer suggestion IA
        def generate_ai_response():
            if self.ollama_client:
                suggestion = self.ollama_client.generate_suggestion(app_name, context)
                final_message = f"📱 {app_name}\n🕒 {context}\n\n💡 {suggestion}"
                self.root.after(0, lambda: self._update_ai_response(final_message))
            else:
                fallback = f"📱 {app_name}\n🕒 {context}\n\n🔌 IA non disponible"
                self.root.after(0, lambda: self.speech_bubble.update_text(fallback))
        
        threading.Thread(target=generate_ai_response, daemon=True).start()
    
    def _on_chat_message(self, message: str):
        """Traitement des messages de chat avec gestion des commandes fichiers"""
        print(f"[CHAT] Message reçu: {message}")
        
        self.chat_mode = True
        
        # Afficher traitement
        thinking_msg = f"💬 Vous: {message}\n\n🤔 Clippy réfléchit..."
        self.speech_bubble.update_text(thinking_msg)
        
        def generate_response():
            # Détecter les commandes de fichiers
            file_keywords = [
                "crée", "créer", "génère", "générer", "fichier", "script", "code",
                "lance", "lancer", "ouvre", "ouvrir", "exécute", "exécuter",
                "déplace", "déplacer", "supprime", "supprimer", "modifie", "modifier",
                "liste", "lister", "affiche", "afficher", "résume", "résumer",
                "cherche", "recherche", "web", "pdf", "traduis", "traduire",
                "corrige", "corriger", "rappel", "historique"
            ]
            
            is_file_command = any(keyword in message.lower() for keyword in file_keywords)
            
            if is_file_command:
                print("[CHAT] Commande fichier détectée")
                try:
                    result = enhanced_file_manager.process_command(message)
                    final_message = f"💬 Vous: {message}\n\n📁 Clippy: {result}"
                except Exception as e:
                    print(f"[CHAT ERROR] Erreur gestionnaire: {e}")
                    final_message = f"💬 Vous: {message}\n\n❌ Erreur: {str(e)}"
            else:
                # Conversation normale
                if self.ollama_client and self.ollama_client.available:
                    try:
                        chat_prompt = f"Tu es Clippy, l'assistant de Microsoft devenu moderne. L'utilisateur te dit: '{message}'. Réponds avec personnalité et humour, en 1-2 phrases maximum."
                        
                        import requests
                        response = requests.post(
                            f"{self.ollama_client.base_url}/api/generate",
                            json={
                                "model": self.ollama_client.model,
                                "prompt": chat_prompt,
                                "stream": False,
                                "options": {"temperature": 0.8, "num_predict": 150}
                            },
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            ai_response = response.json().get("response", "").strip()
                            final_message = f"💬 Vous: {message}\n\n📎 Clippy: {ai_response or 'Je n\'ai pas de réponse...'}"
                        else:
                            final_message = f"💬 Vous: {message}\n\n❌ Erreur de communication avec l'IA"
                    
                    except Exception as e:
                        print(f"[CHAT ERROR] Erreur IA: {e}")
                        final_message = f"💬 Vous: {message}\n\n❌ Erreur: {str(e)}"
                else:
                    final_message = f"💬 Vous: {message}\n\n🔌 IA non disponible - Démarrez Ollama"
            
            # Mettre à jour l'interface
            self.root.after(0, lambda: self._update_chat_response(final_message))
        
        threading.Thread(target=generate_response, daemon=True).start()
    
    def _update_chat_response(self, message: str):
        """Met à jour l'interface avec la réponse"""
        if self.speech_bubble:
            self.speech_bubble.update_text(message)
        
        # Synthèse vocale si activée
        if self.voice_enabled and voice_engine.available:
            lines = message.split('\n')
            for line in lines:
                if line.startswith('📎 Clippy:') or line.startswith('📁 Clippy:'):
                    ai_text = line.split(':', 1)[1].strip()
                    voice_engine.speak(ai_text)
                    break
        
        # Réactiver les contrôles du chat
        if self.chat_widget:
            self.chat_widget.on_response_received()
        
        # Mettre à jour l'historique en mode avancé
        if self.advanced_mode:
            self._update_history_display()
        
        # Retour surveillance après 30s
        def return_to_monitoring():
            self.chat_mode = False
            print("[CHAT] Retour surveillance auto")
        
        self.root.after(30000, return_to_monitoring)
    
    def _update_ai_response(self, message: str):
        """Met à jour avec réponse IA (surveillance)"""
        if self.speech_bubble:
            self.speech_bubble.update_text(message)
        
        # Synthèse vocale de la suggestion
        if self.voice_enabled and voice_engine.available:
            suggestion_text = self._extract_suggestion_from_message(message)
            if suggestion_text:
                voice_engine.speak(suggestion_text)
    
    def _extract_suggestion_from_message(self, message: str) -> str:
        """Extrait la suggestion du message"""
        lines = message.split('\n')
        for line in lines:
            if line.startswith('💡'):
                return line.replace('💡', '').strip()
        return ""
    
    def _start_drag(self, event):
        """Début déplacement fenêtre"""
        self.start_x = event.x_root
        self.start_y = event.y_root
    
    def _on_drag(self, event):
        """Déplacement fenêtre"""
        x = self.root.winfo_x() + (event.x_root - self.start_x)
        y = self.root.winfo_y() + (event.y_root - self.start_y)
        self.root.geometry(f"+{x}+{y}")
        self.start_x = event.x_root
        self.start_y = event.y_root
    
    def _toggle_voice(self):
        """Bascule synthèse vocale"""
        self.voice_enabled = not self.voice_enabled
        
        if self.voice_enabled:
            self.voice_btn.config(text="🔊", bg="#6f42c1")
            if voice_engine.available:
                voice_engine.speak("Voix activée !", priority=True)
        else:
            self.voice_btn.config(text="🔇", bg="#6c757d")
            voice_engine.stop()
    
    def _toggle_speech_recognition(self):
        """Bascule reconnaissance vocale"""
        if not self.speech_engine or not self.speech_engine.available:
            self.speech_bubble.update_text("❌ Microphone non disponible\nVérifiez vos périphériques audio")
            return
        
        if self.speech_listening:
            self.speech_engine.stop_continuous_listening()
            self.speech_listening = False
            self.mic_btn.config(text="🎤", bg="#e83e8c")
            
            if self.speech_bubble:
                self.speech_bubble.update_text("🔇 Écoute arrêtée\nCliquez sur 🎤 pour réactiver")
        else:
            if self.speech_engine.start_continuous_listening():
                self.speech_listening = True
                self.mic_btn.config(text="🔇", bg="#28a745")
                
                if self.speech_bubble:
                    self.speech_bubble.update_text("🎤 Clippy vous écoute !\nParlez maintenant...\n\nDites 'stop' pour arrêter")
                
                if self.voice_enabled and voice_engine.available:
                    voice_engine.speak("Clippy vous écoute !")
    
    def _on_speech_recognized(self, text: str):
        """Traitement parole reconnue"""
        print(f"[SPEECH] Reconnu: {text}")
        self.root.after(0, lambda: self._process_speech_input(text))
    
    def _process_speech_input(self, text: str):
        """Traite l'entrée vocale"""
        text_lower = text.lower()
        
        # Commandes vocales spéciales
        if any(word in text_lower for word in ["stop", "arrête", "silence"]):
            self._toggle_speech_recognition()
            return
        
        if "nouveau conseil" in text_lower or "actualise" in text_lower:
            self._request_new_advice()
            return
        
        if "ferme" in text_lower and ("assistant" in text_lower or "clippy" in text_lower):
            self.close_app()
            return
        
        if "mode avancé" in text_lower:
            self._toggle_advanced_mode()
            return
        
        # Traiter comme message de chat
        if self.chat_widget:
            self.chat_widget.message_entry.delete(0, tk.END)
            self.chat_widget.message_entry.insert(0, text)
            self.chat_widget.send_message()
        else:
            self._on_chat_message(text)
    
    def _request_new_advice(self):
        """Demande nouveau conseil"""
        print("[MANUAL] Nouveau conseil demandé")
        
        self.chat_mode = False
        
        if self.system_monitor and self.system_monitor.current_app:
            app_name = self.system_monitor.current_app
            context = f"Nouveau conseil demandé ({time.strftime('%H:%M')})"
            self._on_app_changed(app_name, context)
        else:
            self._on_app_changed("Système", "Conseil général Clippy")
    
    def _minimize_window(self):
        """Minimise temporairement"""
        self.root.withdraw()
        self.root.after(3000, lambda: self.root.deiconify())
    
    def _show_enhanced_settings(self):
        """Paramètres améliorés"""
        stats = ""
        if self.system_monitor:
            usage_stats = self.system_monitor.get_usage_stats()
            if usage_stats:
                stats = "\n\nApps les plus utilisées :\n"
                sorted_apps = sorted(usage_stats.items(), key=lambda x: x[1], reverse=True)
                for app, time_used in sorted_apps[:3]:
                    stats += f"• {app}: {int(time_used//60)}min\n"
        
        chat_status = "ouvert" if (self.chat_widget and self.chat_widget.is_visible()) else "fermé"
        advanced_status = "activé" if self.advanced_mode else "désactivé"
        
        messagebox.showinfo(
            "📎 Paramètres Clippy",
            f"Assistant Clippy IA v2.0\n\n"
            f"🧠 Modèle: {settings.ollama.model}\n"
            f"🔗 IA: {'✅ Connectée' if self.ollama_client.available else '❌ Déconnectée'}\n"
            f"⏱️ Surveillance: {settings.monitoring.check_interval}s\n"
            f"💬 Chat: {chat_status}\n"
            f"🔧 Mode avancé: {advanced_status}\n"
            f"🎤 Micro: {'✅' if (self.speech_engine and self.speech_engine.available) else '❌'}\n"
            f"🔊 Voix: {'✅' if self.voice_enabled else '❌'}\n"
            f"📁 Dossier: {enhanced_file_manager.base_directory}"
            f"{stats}"
        )
    
    def start_monitoring(self):
        """Démarre la surveillance"""
        if self.system_monitor:
            self.system_monitor.start()
            self.root.after(2000, self._force_initial_detection)
    
    def _force_initial_detection(self):
        """Force détection initiale"""
        if self.system_monitor:
            print("[INIT] Déclenchement initial Clippy...")
            self._on_app_changed("Clippy", "Assistant démarré et prêt !")
    
    def stop_monitoring(self):
        """Arrête la surveillance"""
        if self.system_monitor:
            self.system_monitor.stop()
    
    def run(self):
        """Lance l'application"""
        print("📎 Clippy IA Moderne démarré !")
        print(f"- Fenêtre: {self.root.geometry()}")
        print(f"- IA: {'✅' if self.ollama_client.available else '❌'}")
        print(f"- Fonctionnalités avancées: {'✅' if enhanced_file_manager else '❌'}")
        print("- Cliquez sur Clippy ou utilisez 💬 pour interagir")
        print("- 🔧 pour activer le mode avancé")
        
        # Démarrer surveillance
        self.start_monitoring()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.close_app()
    
    def close_app(self):
        """Fermeture propre"""
        print("🔄 Fermeture de Clippy...")
        
        # Arrêter reconnaissance vocale
        if self.speech_engine:
            self.speech_engine.stop_continuous_listening()
        
        # Arrêter synthèse vocale
        voice_engine.shutdown()
        
        # Arrêter surveillance
        self.stop_monitoring()
        
        # Message de fermeture Clippy
        if self.voice_enabled and voice_engine.available:
            voice_engine.speak("Au revoir ! Clippy s'arrête.")
        
        # Fermer fenêtre
        self.root.quit()
        self.root.destroy()
        
        print("📎 Clippy fermé - À bientôt !")


# Pour utilisation avec tkinter uniquement
try:
    import tkinter.simpledialog
    tk.simpledialog = tkinter.simpledialog
except ImportError:
    pass