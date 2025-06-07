"""
Contrôleur de souris pour automation système
"""

import pyautogui
import time
from typing import Tuple, Optional, List
import random


class MouseController:
    """Contrôleur intelligent de la souris"""
    
    def __init__(self):
        # Configuration sécurité
        pyautogui.FAILSAFE = True  # Coin écran = arrêt d'urgence
        pyautogui.PAUSE = 0.1      # Pause entre actions
        
        # Paramètres de mouvement
        self.move_duration = 0.5   # Durée mouvement naturel
        self.human_like = True     # Mouvements plus naturels
        
        print("[MOUSE] Contrôleur souris initialisé")
    
    def get_position(self) -> Tuple[int, int]:
        """Position actuelle de la souris"""
        return pyautogui.position()
    
    def move_to(self, x: int, y: int, duration: float = None, human_like: bool = None) -> bool:
        """Déplace la souris vers une position"""
        try:
            duration = duration or self.move_duration
            human_like = human_like if human_like is not None else self.human_like
            
            if human_like:
                # Ajouter une petite variation aléatoire pour plus de naturel
                x += random.randint(-2, 2)
                y += random.randint(-2, 2)
                duration += random.uniform(-0.1, 0.1)
            
            pyautogui.moveTo(x, y, duration=max(0.1, duration))
            print(f"[MOUSE] Déplacé vers ({x}, {y})")
            return True
            
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur déplacement: {e}")
            return False
    
    def move_relative(self, dx: int, dy: int, duration: float = None) -> bool:
        """Déplace la souris relativement à sa position actuelle"""
        try:
            duration = duration or self.move_duration
            pyautogui.move(dx, dy, duration=duration)
            print(f"[MOUSE] Déplacé de ({dx}, {dy})")
            return True
            
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur déplacement relatif: {e}")
            return False
    
    def click(self, x: int = None, y: int = None, button: str = 'left', clicks: int = 1, interval: float = 0.1) -> bool:
        """Clique à une position donnée ou position actuelle"""
        try:
            if x is not None and y is not None:
                # Déplacer puis cliquer
                if not self.move_to(x, y):
                    return False
                time.sleep(0.1)  # Petite pause après déplacement
            
            pyautogui.click(button=button, clicks=clicks, interval=interval)
            
            position = self.get_position()
            print(f"[MOUSE] Clic {button} à {position} ({clicks}x)")
            return True
            
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur clic: {e}")
            return False
    
    def double_click(self, x: int = None, y: int = None) -> bool:
        """Double-clic"""
        return self.click(x, y, clicks=2, interval=0.1)
    
    def right_click(self, x: int = None, y: int = None) -> bool:
        """Clic droit"""
        return self.click(x, y, button='right')
    
    def middle_click(self, x: int = None, y: int = None) -> bool:
        """Clic molette"""
        return self.click(x, y, button='middle')
    
    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """Glisser-déposer entre deux points"""
        try:
            # Aller au point de départ
            if not self.move_to(start_x, start_y):
                return False
            
            time.sleep(0.1)
            
            # Maintenir le bouton et glisser
            pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
            
            print(f"[MOUSE] Glisser-déposer de ({start_x}, {start_y}) vers ({end_x}, {end_y})")
            return True
            
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur glisser-déposer: {e}")
            return False
    
    def scroll(self, clicks: int, x: int = None, y: int = None) -> bool:
        """Défilement (positif = haut, négatif = bas)"""
        try:
            if x is not None and y is not None:
                if not self.move_to(x, y):
                    return False
                time.sleep(0.1)
            
            pyautogui.scroll(clicks)
            direction = "haut" if clicks > 0 else "bas"
            print(f"[MOUSE] Défilement {direction} ({abs(clicks)} clics)")
            return True
            
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur défilement: {e}")
            return False
    
    def scroll_horizontal(self, clicks: int, x: int = None, y: int = None) -> bool:
        """Défilement horizontal (si supporté)"""
        try:
            if x is not None and y is not None:
                if not self.move_to(x, y):
                    return False
                time.sleep(0.1)
            
            pyautogui.hscroll(clicks)
            direction = "droite" if clicks > 0 else "gauche"
            print(f"[MOUSE] Défilement horizontal {direction} ({abs(clicks)} clics)")
            return True
            
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur défilement horizontal: {e}")
            return False
    
    def click_and_hold(self, x: int = None, y: int = None, duration: float = 1.0) -> bool:
        """Maintenir le clic pendant une durée"""
        try:
            if x is not None and y is not None:
                if not self.move_to(x, y):
                    return False
                time.sleep(0.1)
            
            pyautogui.mouseDown()
            time.sleep(duration)
            pyautogui.mouseUp()
            
            print(f"[MOUSE] Clic maintenu {duration}s")
            return True
            
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur clic maintenu: {e}")
            return False
    
    def trace_pattern(self, points: List[Tuple[int, int]], duration_per_segment: float = 0.5) -> bool:
        """Trace un motif en suivant une série de points"""
        try:
            if not points:
                return False
            
            # Aller au premier point
            start_x, start_y = points[0]
            if not self.move_to(start_x, start_y):
                return False
            
            # Tracer les segments
            for i in range(1, len(points)):
                x, y = points[i]
                pyautogui.dragTo(x, y, duration=duration_per_segment, button='left')
                time.sleep(0.05)  # Petite pause entre segments
            
            print(f"[MOUSE] Motif tracé avec {len(points)} points")
            return True
            
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur tracé motif: {e}")
            return False
    
    def click_if_color_matches(self, x: int, y: int, expected_color: Tuple[int, int, int], tolerance: int = 10) -> bool:
        """Clique seulement si la couleur du pixel correspond"""
        try:
            actual_color = pyautogui.pixel(x, y)
            
            # Vérifier si les couleurs correspondent (avec tolérance)
            color_match = all(
                abs(actual_color[i] - expected_color[i]) <= tolerance 
                for i in range(3)
            )
            
            if color_match:
                self.click(x, y)
                print(f"[MOUSE] Clic conditionnel réussi à ({x}, {y})")
                return True
            else:
                print(f"[MOUSE] Couleur ne correspond pas: attendu {expected_color}, trouvé {actual_color}")
                return False
                
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur clic conditionnel: {e}")
            return False
    
    def find_and_click_color(self, color: Tuple[int, int, int], region: Tuple[int, int, int, int] = None) -> bool:
        """Trouve et clique sur la première occurrence d'une couleur"""
        try:
            # Capturer la région ou tout l'écran
            if region:
                x, y, width, height = region
                screenshot = pyautogui.screenshot(region=region)
                offset_x, offset_y = x, y
            else:
                screenshot = pyautogui.screenshot()
                offset_x, offset_y = 0, 0
            
            # Convertir en numpy pour recherche plus efficace
            import numpy as np
            img_array = np.array(screenshot)
            
            # Chercher la couleur
            matches = np.where(np.all(img_array == color, axis=2))
            
            if len(matches[0]) > 0:
                # Prendre le premier match
                pixel_y, pixel_x = matches[0][0], matches[1][0]
                click_x = pixel_x + offset_x
                click_y = pixel_y + offset_y
                
                self.click(click_x, click_y)
                print(f"[MOUSE] Couleur {color} trouvée et cliquée à ({click_x}, {click_y})")
                return True
            else:
                print(f"[MOUSE] Couleur {color} non trouvée")
                return False
                
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur recherche couleur: {e}")
            return False
    
    def safe_click_with_retry(self, x: int, y: int, max_retries: int = 3, retry_delay: float = 0.5) -> bool:
        """Clic avec retry en cas d'échec"""
        for attempt in range(max_retries):
            try:
                if self.click(x, y):
                    return True
                    
                if attempt < max_retries - 1:
                    print(f"[MOUSE] Tentative {attempt + 1} échouée, retry dans {retry_delay}s")
                    time.sleep(retry_delay)
                    
            except Exception as e:
                print(f"[MOUSE ERROR] Tentative {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        print(f"[MOUSE] Échec après {max_retries} tentatives")
        return False
    
    def get_screen_bounds(self) -> Tuple[int, int]:
        """Retourne les dimensions de l'écran"""
        return pyautogui.size()
    
    def is_position_valid(self, x: int, y: int) -> bool:
        """Vérifie si une position est dans les limites de l'écran"""
        screen_width, screen_height = self.get_screen_bounds()
        return 0 <= x < screen_width and 0 <= y < screen_height
    
    def move_in_circle(self, center_x: int, center_y: int, radius: int, steps: int = 20) -> bool:
        """Déplace la souris en cercle (pour démonstration/test)"""
        try:
            import math
            
            for i in range(steps + 1):
                angle = 2 * math.pi * i / steps
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                
                if self.is_position_valid(x, y):
                    pyautogui.moveTo(x, y, duration=0.1)
                else:
                    print(f"[MOUSE] Position ({x}, {y}) hors limites")
                    break
            
            print(f"[MOUSE] Cercle tracé autour de ({center_x}, {center_y})")
            return True
            
        except Exception as e:
            print(f"[MOUSE ERROR] Erreur mouvement circulaire: {e}")
            return False
    
    def set_speed(self, duration: float):
        """Configure la vitesse de déplacement"""
        self.move_duration = max(0.1, duration)
        print(f"[MOUSE] Vitesse configurée: {self.move_duration}s")
    
    def enable_human_like_movement(self, enabled: bool = True):
        """Active/désactive les mouvements naturels"""
        self.human_like = enabled
        mode = "activés" if enabled else "désactivés"
        print(f"[MOUSE] Mouvements naturels {mode}")
    
    def emergency_stop(self):
        """Arrêt d'urgence (déplace souris au coin)"""
        try:
            pyautogui.moveTo(0, 0, duration=0.1)
            print("[MOUSE] Arrêt d'urgence activé")
        except:
            pass


# Instance globale
mouse_controller = MouseController()