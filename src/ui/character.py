"""
Widget du personnage animé
"""

import tkinter as tk
from typing import Dict, Tuple
import math
import time


class CharacterWidget(tk.Frame):
    """Widget personnage avec animations"""
    
    def __init__(self, parent, size: int = 80):
        # Fix: Obtenir la couleur de fond du parent correctement
        parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else '#f0f0f0'
        super().__init__(parent, bg=parent_bg)
        
        self.size = size
        self.current_mood = "neutral"
        self.animation_frame = 0
        self.animation_running = False
        
        # Canvas pour dessiner le personnage
        self.canvas = tk.Canvas(
            self, 
            width=size, 
            height=size,
            bg='white', 
            highlightthickness=1,
            highlightbackground='#ccc'
        )
        self.canvas.pack()
        
        # Définition des humeurs et animations
        self._define_moods()
        
        # Dessiner le personnage initial
        self.draw_character()
        
        # Démarrer l'animation
        self._start_animation_loop()
    
    def _define_moods(self):
        """Définit les différentes humeurs du personnage"""
        self.moods: Dict[str, Dict] = {
            "neutral": {
                "eye_shape": "normal",
                "mouth_shape": "slight_smile",
                "body_color": "#6496ff",
                "blink_rate": 3000,  # ms
                "animation": None
            },
            "happy": {
                "eye_shape": "normal", 
                "mouth_shape": "big_smile",
                "body_color": "#4CAF50",
                "blink_rate": 2000,
                "animation": "bounce"
            },
            "thinking": {
                "eye_shape": "squint",
                "mouth_shape": "thinking",
                "body_color": "#FF9800",
                "blink_rate": 1500,
                "animation": "sway"
            },
            "confused": {
                "eye_shape": "confused",
                "mouth_shape": "confused",
                "body_color": "#9C27B0",
                "blink_rate": 4000,
                "animation": "shake"
            },
            "working": {
                "eye_shape": "focused",
                "mouth_shape": "straight",
                "body_color": "#2196F3",
                "blink_rate": 1000,
                "animation": "pulse"
            }
        }
    
    def set_mood(self, mood: str):
        """Change l'humeur du personnage"""
        if mood in self.moods:
            self.current_mood = mood
            self.draw_character()
            print(f"[CHARACTER] Humeur: {mood}")
    
    def draw_character(self):
        """Dessine le personnage selon son humeur actuelle"""
        self.canvas.delete("all")
        
        mood_config = self.moods[self.current_mood]
        center_x, center_y = self.size // 2, self.size // 2
        radius = self.size // 3
        
        # Animation offset
        offset_x, offset_y = self._get_animation_offset()
        
        # Corps (cercle principal)
        body_x1 = center_x - radius + offset_x
        body_y1 = center_y - radius + offset_y
        body_x2 = center_x + radius + offset_x
        body_y2 = center_y + radius + offset_y
        
        self.canvas.create_oval(
            body_x1, body_y1, body_x2, body_y2,
            fill=mood_config["body_color"],
            outline=self._darken_color(mood_config["body_color"]),
            width=2
        )
        
        # Yeux
        self._draw_eyes(center_x + offset_x, center_y + offset_y, mood_config["eye_shape"])
        
        # Bouche
        self._draw_mouth(center_x + offset_x, center_y + offset_y, mood_config["mouth_shape"])
        
        # Effet spéciaux selon l'humeur
        if self.current_mood == "thinking":
            self._draw_thought_bubble(center_x + offset_x, center_y + offset_y)
    
    def _draw_eyes(self, center_x: int, center_y: int, eye_shape: str):
        """Dessine les yeux selon la forme demandée"""
        eye_y = center_y - 8
        left_eye_x = center_x - 12
        right_eye_x = center_x + 8
        
        if eye_shape == "normal":
            # Yeux normaux
            self.canvas.create_oval(left_eye_x, eye_y, left_eye_x + 8, eye_y + 8, 
                                  fill='white', outline='black')
            self.canvas.create_oval(right_eye_x, eye_y, right_eye_x + 8, eye_y + 8, 
                                  fill='white', outline='black')
            
            # Pupilles
            self.canvas.create_oval(left_eye_x + 2, eye_y + 2, left_eye_x + 6, eye_y + 6, 
                                  fill='black')
            self.canvas.create_oval(right_eye_x + 2, eye_y + 2, right_eye_x + 6, eye_y + 6, 
                                  fill='black')
        
        elif eye_shape == "squint":
            # Yeux plissés (réflexion)
            self.canvas.create_line(left_eye_x, eye_y + 4, left_eye_x + 8, eye_y + 4, 
                                  fill='black', width=2)
            self.canvas.create_line(right_eye_x, eye_y + 4, right_eye_x + 8, eye_y + 4, 
                                  fill='black', width=2)
        
        elif eye_shape == "confused":
            # Yeux interrogateurs
            self.canvas.create_oval(left_eye_x, eye_y, left_eye_x + 8, eye_y + 8, 
                                  fill='white', outline='black')
            self.canvas.create_oval(right_eye_x, eye_y, right_eye_x + 8, eye_y + 8, 
                                  fill='white', outline='black')
            
            # Pupilles décalées
            self.canvas.create_oval(left_eye_x + 1, eye_y + 3, left_eye_x + 5, eye_y + 7, 
                                  fill='black')
            self.canvas.create_oval(right_eye_x + 3, eye_y + 1, right_eye_x + 7, eye_y + 5, 
                                  fill='black')
        
        elif eye_shape == "focused":
            # Yeux concentrés
            self.canvas.create_oval(left_eye_x, eye_y + 2, left_eye_x + 8, eye_y + 6, 
                                  fill='white', outline='black')
            self.canvas.create_oval(right_eye_x, eye_y + 2, right_eye_x + 8, eye_y + 6, 
                                  fill='white', outline='black')
            
            self.canvas.create_oval(left_eye_x + 2, eye_y + 3, left_eye_x + 6, eye_y + 5, 
                                  fill='black')
            self.canvas.create_oval(right_eye_x + 2, eye_y + 3, right_eye_x + 6, eye_y + 5, 
                                  fill='black')
    
    def _draw_mouth(self, center_x: int, center_y: int, mouth_shape: str):
        """Dessine la bouche selon la forme demandée"""
        mouth_y = center_y + 8
        
        if mouth_shape == "slight_smile":
            # Sourire léger
            self.canvas.create_arc(center_x - 10, mouth_y, center_x + 10, mouth_y + 10,
                                 start=0, extent=-180, outline='black', width=2)
        
        elif mouth_shape == "big_smile":
            # Grand sourire
            self.canvas.create_arc(center_x - 15, mouth_y - 5, center_x + 15, mouth_y + 15,
                                 start=0, extent=-180, outline='black', width=3)
        
        elif mouth_shape == "thinking":
            # Bouche de réflexion (petit 'o')
            self.canvas.create_oval(center_x - 3, mouth_y + 2, center_x + 3, mouth_y + 8,
                                  fill='white', outline='black', width=2)
        
        elif mouth_shape == "confused":
            # Bouche confuse (ligne ondulée)
            points = []
            for i in range(0, 21, 2):
                x = center_x - 10 + i
                y = mouth_y + 5 + math.sin(i * 0.5) * 2
                points.extend([x, y])
            
            if len(points) >= 4:
                self.canvas.create_line(points, fill='black', width=2, smooth=True)
        
        elif mouth_shape == "straight":
            # Bouche droite (concentration)
            self.canvas.create_line(center_x - 8, mouth_y + 5, center_x + 8, mouth_y + 5,
                                  fill='black', width=2)
    
    def _draw_thought_bubble(self, center_x: int, center_y: int):
        """Dessine une bulle de pensée"""
        # Petites bulles
        bubble_x = center_x + 25
        bubble_y = center_y - 20
        
        self.canvas.create_oval(bubble_x, bubble_y, bubble_x + 4, bubble_y + 4,
                              fill='white', outline='gray')
        self.canvas.create_oval(bubble_x + 6, bubble_y - 8, bubble_x + 8, bubble_y - 6,
                              fill='white', outline='gray')
        self.canvas.create_oval(bubble_x + 10, bubble_y - 15, bubble_x + 12, bubble_y - 13,
                              fill='white', outline='gray')
    
    def _get_animation_offset(self) -> Tuple[int, int]:
        """Calcule l'offset d'animation selon l'humeur"""
        if not self.animation_running:
            return 0, 0
        
        mood_config = self.moods[self.current_mood]
        animation = mood_config.get("animation")
        
        if animation == "bounce":
            # Animation de rebond
            offset_y = int(math.sin(self.animation_frame * 0.3) * 3)
            return 0, offset_y
        
        elif animation == "sway":
            # Animation de balancement
            offset_x = int(math.sin(self.animation_frame * 0.2) * 2)
            return offset_x, 0
        
        elif animation == "shake":
            # Animation de tremblement
            offset_x = int(math.sin(self.animation_frame * 0.8) * 1)
            offset_y = int(math.cos(self.animation_frame * 0.9) * 1)
            return offset_x, offset_y
        
        elif animation == "pulse":
            # Animation de pulsation (changement de taille)
            # Pour simplifier, on retourne juste un léger mouvement
            offset = int(math.sin(self.animation_frame * 0.4) * 1)
            return offset, offset
        
        return 0, 0
    
    def _darken_color(self, color: str) -> str:
        """Assombrit une couleur hexadécimale"""
        if color.startswith('#'):
            try:
                # Convertir hex en RGB
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                # Assombrir de 20%
                r = max(0, int(r * 0.8))
                g = max(0, int(g * 0.8))
                b = max(0, int(b * 0.8))
                
                # Reconvertir en hex
                return f"#{r:02x}{g:02x}{b:02x}"
            except:
                return "#333333"
        
        return color
    
    def _start_animation_loop(self):
        """Démarre la boucle d'animation"""
        self.animation_running = True
        self._animate()
    
    def _animate(self):
        """Boucle d'animation principale"""
        if self.animation_running:
            self.animation_frame += 1
            
            # Redessiner seulement si il y a une animation
            mood_config = self.moods[self.current_mood]
            if mood_config.get("animation"):
                self.draw_character()
            
            # Programmer la prochaine frame
            self.after(50, self._animate)  # 20 FPS
    
    def stop_animation(self):
        """Arrête l'animation"""
        self.animation_running = False
    
    def start_animation(self):
        """Redémarre l'animation"""
        if not self.animation_running:
            self._start_animation_loop()