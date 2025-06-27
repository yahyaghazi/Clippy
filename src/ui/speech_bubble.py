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
        print(f"[DEBUG BUBBLE] Mise à jour avec: {text[:50]}...")  # Debug
        
        if animated and not self.is_typing:
            self._animate_text(text)
        else:
            self._set_text_immediate(text)
        
        print(f"[DEBUG BUBBLE] Texte mis à jour, longueur: {len(text)}")
    
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
            
            # Détecter et styler différents types de contenu
            if line.startswith('📱'):
                # Nom d'application
                self.text_widget.insert(tk.END, line, "app_name")
            elif line.startswith('💡'):
                # Suggestion IA
                self.text_widget.insert(tk.END, line, "ai_suggestion")
            elif line.startswith('🕒') or line.startswith('🔍') or line.startswith('⚠️'):
                # Information système
                self.text_widget.insert(tk.END, line, "system_info")
            elif any(emoji in line for emoji in ['👋', '🤖', '🧠', '🔌', '⏱️', '🔄']):
                # Ligne avec emojis
                self.text_widget.insert(tk.END, line, "emoji")
            else:
                # Texte normal
                self.text_widget.insert(tk.END, line)
    
    def _animate_text(self, text: str):
        """Anime l'apparition du texte (effet machine à écrire)"""
        if self.is_typing:
            return
        
        self.is_typing = True
        self.current_text = text
        
        # Effacer le contenu actuel
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)
        
        # Démarrer l'animation
        self._type_character(0, text)
    
    def _type_character(self, index: int, full_text: str):
        """Type un caractère à la fois"""
        if index < len(full_text) and self.is_typing:
            char = full_text[index]
            
            # Activer l'édition temporairement
            self.text_widget.config(state=tk.NORMAL)
            
            # Insérer le caractère
            self.text_widget.insert(tk.END, char)
            
            # Désactiver l'édition
            self.text_widget.config(state=tk.DISABLED)
            
            # Scroller vers le bas
            self.text_widget.see(tk.END)
            
            # Programmer le prochain caractère
            self.after(self.typing_speed, lambda: self._type_character(index + 1, full_text))
        else:
            # Animation terminée
            self.is_typing = False
            
            # Appliquer les styles finaux
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete(1.0, tk.END)
            self._insert_styled_text(full_text)
            self.text_widget.config(state=tk.DISABLED)
    
    def append_text(self, text: str):
        """Ajoute du texte à la fin du contenu actuel"""
        new_content = self.current_text + "\n" + text if self.current_text else text
        self.update_text(new_content)
    
    def clear(self):
        """Efface le contenu de la bulle"""
        self.update_text("")
    
    def set_typing_speed(self, speed_ms: int):
        """Change la vitesse de l'animation de frappe"""
        self.typing_speed = max(10, min(200, speed_ms))  # Entre 10ms et 200ms
    
    def stop_typing_animation(self):
        """Arrête l'animation de frappe en cours"""
        if self.is_typing:
            self.is_typing = False
            # Afficher le texte complet immédiatement
            self._set_text_immediate(self.current_text)
    
    def get_text(self) -> str:
        """Retourne le texte actuel"""
        return self.current_text
    
    def is_empty(self) -> bool:
        """Vérifie si la bulle est vide"""
        return not bool(self.current_text.strip())
    
    def show_loading(self, message: str = "🔄 Chargement..."):
        """Affiche un message de chargement animé"""
        loading_frames = ["🔄", "⏳", "⌛", "🔄"]
        self._animate_loading(message, loading_frames, 0)
    
    def _animate_loading(self, base_message: str, frames: list, frame_index: int):
        """Anime l'indicateur de chargement"""
        if self.is_typing:  # Arrêter si une autre animation commence
            return
        
        current_frame = frames[frame_index % len(frames)]
        loading_message = f"{current_frame} {base_message[2:]}"  # Remplacer le premier emoji
        
        self._set_text_immediate(loading_message)
        
        # Continuer l'animation
        self.after(500, lambda: self._animate_loading(
            base_message, frames, frame_index + 1
        ))
    
    def highlight_keywords(self, keywords: list):
        """Met en surbrillance certains mots-clés"""
        content = self.text_widget.get(1.0, tk.END)
        
        self.text_widget.config(state=tk.NORMAL)
        
        # Créer un tag pour la surbrillance
        self.text_widget.tag_configure(
            "highlight",
            background='yellow',
            foreground='black'
        )
        
        for keyword in keywords:
            start = content.lower().find(keyword.lower())
            if start != -1:
                start_idx = f"1.{start}"
                end_idx = f"1.{start + len(keyword)}"
                self.text_widget.tag_add("highlight", start_idx, end_idx)
        
        self.text_widget.config(state=tk.DISABLED)