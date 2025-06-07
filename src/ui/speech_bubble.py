"""
Widget bulle de dialogue
"""

import tkinter as tk
from tkinter import scrolledtext
from typing import Optional
import time


class SpeechBubble(tk.Frame):
    """Bulle de dialogue pour afficher les messages de l'assistant"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=parent['bg'])
        
        self.current_text = ""
        self.is_typing = False
        self.typing_speed = 30  # ms par caractère
        
        self._create_bubble()
    
    def _create_bubble(self):
        """Crée la bulle de dialogue"""
        # Frame pour la bulle avec style
        bubble_frame = tk.Frame(
            self,
            bg='white',
            relief=tk.RAISED,
            bd=2
        )
        bubble_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Zone de texte avec scrollbar si nécessaire
        self.text_widget = scrolledtext.ScrolledText(
            bubble_frame,
            height=6,
            width=25,
            wrap=tk.WORD,
            font=('Arial', 9),
            bg='white',
            fg='#333',
            relief=tk.FLAT,
            padx=8,
            pady=8,
            state=tk.DISABLED,  # Lecture seule par défaut
            cursor='arrow'
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configurer les tags pour le style
        self._configure_text_styles()
    
    def _configure_text_styles(self):
        """Configure les styles de texte"""
        # Style pour les emojis (plus gros)
        self.text_widget.tag_configure(
            "emoji",
            font=('Arial', 12),
            foreground='#FF6B6B'
        )
        
        # Style pour les titres d'applications
        self.text_widget.tag_configure(
            "app_name",
            font=('Arial', 9, 'bold'),
            foreground='#2196F3'
        )
        
        # Style pour les suggestions IA
        self.text_widget.tag_configure(
            "ai_suggestion",
            font=('Arial', 9),
            foreground='#4CAF50',
            spacing1=3
        )
        
        # Style pour les informations système
        self.text_widget.tag_configure(
            "system_info",
            font=('Arial', 8),
            foreground='#666'
        )
    
    def update_text(self, text: str, animated: bool = False):
        """Met à jour le texte de la bulle"""
        if animated and not self.is_typing:
            self._animate_text(text)
        else:
            self._set_text_immediate(text)
    
    def _set_text_immediate(self, text: str):
        """Met à jour le texte immédiatement"""
        self.current_text = text
        
        # Activer l'édition temporairement
        self.text_widget.config(state=tk.NORMAL)
        
        # Effacer le contenu actuel
        self.text_widget.delete(1.0, tk.END)
        
        # Insérer le nouveau texte avec style
        self._insert_styled_text(text)
        
        # Désactiver l'édition
        self.text_widget.config(state=tk.DISABLED)
        
        # Scroller vers le bas
        self.text_widget.see(tk.END)
    
    def _insert_styled_text(self, text: str):
        """Insère le texte avec des styles"""
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if i > 0:
                self.text_widget.insert(tk.END, '\n')
            
            # Détecter les émojis
            if line.startswith('📱'):
                self.text_widget.insert(tk.END, line, "app_name")
            elif line.startswith('💡'):
                self.text_widget.insert(tk.END, line, "ai_suggestion")
            elif line.startswith('🕒'):
                self.text_widget.insert(tk.END, line, "system_info")
            else:
                self.text_widget.insert(tk.END, line)