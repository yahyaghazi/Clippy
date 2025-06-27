"""
Widget de chat pour interaction directe avec l'IA - Version debug
"""

import tkinter as tk
from typing import Callable


class ChatWidget(tk.Frame):
    """Widget de chat pour parler directement avec l'IA"""
    
    def __init__(self, parent, on_message_callback: Callable[[str], None]):
        super().__init__(parent, bg=parent['bg'])
        
        self.on_message_callback = on_message_callback
        self.chat_visible = False
        self.message_history = []
        self.history_index = -1
        
        print("[CHAT WIDGET] Initialisation du widget de chat...")
        self._create_widgets()
        print("[CHAT WIDGET] Widget de chat créé avec succès")
    
    def _create_widgets(self):
        """Crée les widgets du chat"""
        print("[CHAT WIDGET] Création des widgets...")
        
        # Bouton pour basculer l'affichage du chat
        self.toggle_btn = tk.Button(
            self,
            text="💬 Chat",
            command=self.toggle_chat,
            bg='#2196F3',
            fg='white',
            font=('Arial', 9),
            width=10,
            height=1,
            relief=tk.RAISED,
            cursor='hand2'
        )
        self.toggle_btn.pack(pady=3)
        print("[CHAT WIDGET] Bouton toggle créé")
        
        # Frame principal du chat (initialement caché)
        self.chat_frame = tk.Frame(
            self, 
            bg='#e3f2fd',  # Bleu clair pour le debug
            relief=tk.RAISED, 
            bd=2
        )
        print("[CHAT WIDGET] Frame principal créé")
        
        # Zone de saisie du chat
        self._create_chat_area()
        print("[CHAT WIDGET] Zone de saisie créée")
    
    def _create_chat_area(self):
        """Crée la zone de saisie du chat"""
        print("[CHAT WIDGET] Création de la zone de saisie...")
        
        # Titre du chat
        title_label = tk.Label(
            self.chat_frame,
            text="💭 Discussion avec l'IA",
            bg='#e3f2fd',
            font=('Arial', 9, 'bold'),
            fg='#1976d2'
        )
        title_label.pack(pady=5)
        print("[CHAT WIDGET] Titre créé")
        
        # Frame pour l'entrée de texte
        entry_frame = tk.Frame(self.chat_frame, bg='#e3f2fd')
        entry_frame.pack(fill=tk.X, padx=10, pady=5)
        print("[CHAT WIDGET] Frame d'entrée créé")
        
        # Label d'instruction
        instruction_label = tk.Label(
            entry_frame,
            text="Tapez votre message :",
            bg='#e3f2fd',
            font=('Arial', 8),
            fg='#424242'
        )
        instruction_label.pack(anchor=tk.W, pady=(0, 2))
        print("[CHAT WIDGET] Label d'instruction créé")
        
        # Frame pour entry + bouton sur la même ligne
        input_frame = tk.Frame(entry_frame, bg='#e3f2fd')
        input_frame.pack(fill=tk.X, pady=2)
        print("[CHAT WIDGET] Frame d'input créé")
        
        # Entry pour taper le message
        self.message_entry = tk.Entry(
            input_frame,
            font=('Arial', 9),
            relief=tk.SUNKEN,
            bd=1,
            bg='white',
            fg='#333333',
            width=20
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        print("[CHAT WIDGET] Entry créé")
        
        # Bouton envoyer
        self.send_btn = tk.Button(
            input_frame,
            text="Envoyer",
            command=self.send_message,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 8),
            relief=tk.RAISED,
            cursor='hand2'
        )
        self.send_btn.pack(side=tk.RIGHT)
        print("[CHAT WIDGET] Bouton d'envoi créé")
        
        # Aide
        help_label = tk.Label(
            self.chat_frame,
            text="💡 Astuce : Entrée=Envoyer, Échap=Fermer",
            bg='#e3f2fd',
            font=('Arial', 7),
            fg='#666666'
        )
        help_label.pack(pady=2)
        print("[CHAT WIDGET] Label d'aide créé")
        
        # Bindings pour l'entry
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        self.message_entry.bind('<Escape>', lambda e: self.toggle_chat())
        print("[CHAT WIDGET] Bindings configurés")
        
        # Test pour vérifier que le frame existe
        test_label = tk.Label(
            self.chat_frame,
            text="🧪 ZONE DE TEST - SI VOUS VOYEZ CECI, LE CHAT FONCTIONNE",
            bg='yellow',
            fg='red',
            font=('Arial', 8, 'bold')
        )
        test_label.pack(pady=2)
        print("[CHAT WIDGET] Label de test ajouté")
    
    def toggle_chat(self):
        """Affiche/cache la zone de chat"""
        print(f"[CHAT WIDGET] Toggle chat appelé - État actuel: {self.chat_visible}")
        
        if self.chat_visible:
            self._hide_chat()
        else:
            self._show_chat()
        
        print(f"[CHAT WIDGET] Nouvel état: {self.chat_visible}")
    
    def _show_chat(self):
        """Affiche la zone de chat"""
        print("[CHAT WIDGET] === AFFICHAGE DU CHAT ===")
        
        # Vérifier que le frame existe
        if not hasattr(self, 'chat_frame'):
            print("[CHAT WIDGET ERROR] chat_frame n'existe pas !")
            return
        
        # Afficher le frame
        self.chat_frame.pack(fill=tk.X, padx=5, pady=5)
        print("[CHAT WIDGET] Frame chat_frame packé")
        
        # Mettre à jour l'état
        self.chat_visible = True
        self.toggle_btn.config(text="💬 Fermer", bg='#FF9800')
        print("[CHAT WIDGET] Bouton mis à jour")
        
        # Forcer la mise à jour de l'affichage
        self.update_idletasks()
        print("[CHAT WIDGET] update_idletasks() appelé")
        
        # Focus sur l'entry
        try:
            self.message_entry.focus_set()
            print("[CHAT WIDGET] Focus mis sur l'entry")
        except Exception as e:
            print(f"[CHAT WIDGET ERROR] Erreur focus: {e}")
        
        print("[CHAT WIDGET] === FIN AFFICHAGE ===")
    
    def _hide_chat(self):
        """Cache la zone de chat"""
        print("[CHAT WIDGET] === MASQUAGE DU CHAT ===")
        
        if hasattr(self, 'chat_frame'):
            self.chat_frame.pack_forget()
            print("[CHAT WIDGET] Frame chat_frame caché")
        
        self.chat_visible = False
        self.toggle_btn.config(text="💬 Chat", bg='#2196F3')
        print("[CHAT WIDGET] Bouton remis en mode fermé")
        
        print("[CHAT WIDGET] === FIN MASQUAGE ===")
    
    def send_message(self):
        """Envoie le message à l'IA"""
        if not hasattr(self, 'message_entry'):
            print("[CHAT WIDGET ERROR] message_entry n'existe pas !")
            return
            
        message = self.message_entry.get().strip()
        print(f"[CHAT WIDGET] Tentative d'envoi: '{message}'")
        
        # Ignorer les messages vides
        if not message:
            print("[CHAT WIDGET] Message vide, ignoré")
            return
        
        # Ajouter à l'historique
        self.message_history.append(message)
        self.history_index = len(self.message_history)
        
        # Limiter l'historique à 20 messages
        if len(self.message_history) > 20:
            self.message_history = self.message_history[-20:]
            self.history_index = len(self.message_history)
        
        # Effacer l'entry
        self.message_entry.delete(0, tk.END)
        
        # Désactiver temporairement les contrôles
        self._set_controls_state(False)
        
        # Callback vers l'IA
        print(f"[CHAT WIDGET] Appel du callback avec: {message}")
        try:
            self.on_message_callback(message)
            print("[CHAT WIDGET] Callback exécuté avec succès")
        except Exception as e:
            print(f"[CHAT WIDGET ERROR] Erreur dans le callback: {e}")
            self._set_controls_state(True)  # Réactiver en cas d'erreur
    
    def _set_controls_state(self, enabled: bool):
        """Active/désactive les contrôles du chat"""
        if not hasattr(self, 'message_entry') or not hasattr(self, 'send_btn'):
            print("[CHAT WIDGET ERROR] Contrôles non initialisés")
            return
            
        state = tk.NORMAL if enabled else tk.DISABLED
        self.message_entry.config(state=state)
        self.send_btn.config(state=state)
        
        if enabled:
            self.send_btn.config(text="Envoyer", bg='#4CAF50')
        else:
            self.send_btn.config(text="⏳", bg='#999999')
        
        print(f"[CHAT WIDGET] Contrôles {'activés' if enabled else 'désactivés'}")
    
    def on_response_received(self):
        """Appelé quand une réponse de l'IA est reçue"""
        print("[CHAT WIDGET] Réponse reçue, réactivation des contrôles")
        self._set_controls_state(True)
        
        # Remettre le focus sur l'entry si le chat est ouvert
        if self.chat_visible and hasattr(self, 'message_entry'):
            self.message_entry.focus_set()
    
    def is_visible(self) -> bool:
        """Retourne True si le chat est visible"""
        return self.chat_visible
    
    def clear_entry(self):
        """Efface l'entry"""
        if hasattr(self, 'message_entry'):
            self.message_entry.delete(0, tk.END)
    
    def get_history(self) -> list:
        """Retourne l'historique des messages"""
        return self.message_history.copy()