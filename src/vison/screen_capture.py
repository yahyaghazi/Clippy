"""
Module de capture d'écran et analyse visuelle
"""

import pyautogui
import time
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from typing import Tuple, Optional, List, Dict
from pathlib import Path
import os


class ScreenCapture:
    """Gestionnaire de capture d'écran et analyse"""
    
    def __init__(self):
        # Configuration pyautogui
        pyautogui.FAILSAFE = True  # Mouvement souris coin = arrêt urgence
        pyautogui.PAUSE = 0.1      # Pause entre actions
        
        # Dossier de sauvegarde
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        
        print("[VISION] Module capture d'écran initialisé")
    
    def capture_full_screen(self, save=True) -> Image.Image:
        """Capture l'écran complet"""
        try:
            screenshot = pyautogui.screenshot()
            
            if save:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = self.screenshot_dir / f"screen_{timestamp}.png"
                screenshot.save(filename)
                print(f"[VISION] Capture sauvée: {filename}")
            
            return screenshot
            
        except Exception as e:
            print(f"[VISION ERROR] Erreur capture: {e}")
            return None
    
    def capture_region(self, x: int, y: int, width: int, height: int, save=True) -> Image.Image:
        """Capture une région spécifique de l'écran"""
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            if save:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = self.screenshot_dir / f"region_{timestamp}.png"
                screenshot.save(filename)
                print(f"[VISION] Région capturée: {filename}")
            
            return screenshot
            
        except Exception as e:
            print(f"[VISION ERROR] Erreur capture région: {e}")
            return None
    
    def capture_active_window(self, save=True) -> Image.Image:
        """Capture la fenêtre active (Windows uniquement)"""
        try:
            # Obtenir les informations de la fenêtre active
            if os.name == 'nt':  # Windows
                import win32gui
                import win32con
                
                hwnd = win32gui.GetForegroundWindow()
                rect = win32gui.GetWindowRect(hwnd)
                x, y, x2, y2 = rect
                width = x2 - x
                height = y2 - y
                
                # Capturer la région de la fenêtre
                screenshot = self.capture_region(x, y, width, height, save=False)
                
                if save and screenshot:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    window_title = win32gui.GetWindowText(hwnd)
                    safe_title = "".join(c for c in window_title if c.isalnum() or c in (' ', '_'))[:50]
                    filename = self.screenshot_dir / f"window_{safe_title}_{timestamp}.png"
                    screenshot.save(filename)
                    print(f"[VISION] Fenêtre '{window_title}' capturée: {filename}")
                
                return screenshot
            else:
                # Fallback : capture complète
                print("[VISION] Capture fenêtre non supportée sur cette plateforme")
                return self.capture_full_screen(save)
                
        except Exception as e:
            print(f"[VISION ERROR] Erreur capture fenêtre: {e}")
            return self.capture_full_screen(save)
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Retourne la taille de l'écran"""
        return pyautogui.size()
    
    def find_image_on_screen(self, template_path: str, confidence=0.8) -> Optional[Tuple[int, int]]:
        """Trouve une image template sur l'écran"""
        try:
            location = pyautogui.locateOnScreen(template_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                print(f"[VISION] Image trouvée à: {center}")
                return center
            else:
                print(f"[VISION] Image non trouvée: {template_path}")
                return None
                
        except Exception as e:
            print(f"[VISION ERROR] Erreur recherche image: {e}")
            return None
    
    def find_all_images_on_screen(self, template_path: str, confidence=0.8) -> List[Tuple[int, int]]:
        """Trouve toutes les occurrences d'une image sur l'écran"""
        try:
            locations = list(pyautogui.locateAllOnScreen(template_path, confidence=confidence))
            centers = [pyautogui.center(loc) for loc in locations]
            print(f"[VISION] {len(centers)} images trouvées")
            return centers
            
        except Exception as e:
            print(f"[VISION ERROR] Erreur recherche multiple: {e}")
            return []
    
    def annotate_screenshot(self, image: Image.Image, annotations: List[Dict]) -> Image.Image:
        """Ajoute des annotations à une capture d'écran"""
        try:
            # Créer une copie pour annotations
            annotated = image.copy()
            draw = ImageDraw.Draw(annotated)
            
            # Police par défaut (si disponible)
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            for annotation in annotations:
                x = annotation.get('x', 0)
                y = annotation.get('y', 0)
                text = annotation.get('text', '')
                color = annotation.get('color', 'red')
                
                # Dessiner un rectangle autour du texte
                text_bbox = draw.textbbox((x, y), text, font=font)
                draw.rectangle(text_bbox, outline=color, width=2)
                
                # Dessiner le texte
                draw.text((x, y), text, fill=color, font=font)
            
            return annotated
            
        except Exception as e:
            print(f"[VISION ERROR] Erreur annotation: {e}")
            return image
    
    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """Obtient la couleur d'un pixel à la position donnée"""
        try:
            return pyautogui.pixel(x, y)
        except Exception as e:
            print(f"[VISION ERROR] Erreur lecture pixel: {e}")
            return (0, 0, 0)
    
    def save_screenshot_with_info(self, image: Image.Image, info: Dict) -> str:
        """Sauvegarde une capture avec des métadonnées"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = self.screenshot_dir / f"annotated_{timestamp}.png"
            
            # Ajouter des informations en bas de l'image
            width, height = image.size
            new_height = height + 100  # Espace pour infos
            
            # Créer nouvelle image avec espace info
            new_image = Image.new('RGB', (width, new_height), 'white')
            new_image.paste(image, (0, 0))
            
            # Ajouter texte d'information
            draw = ImageDraw.Draw(new_image)
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            y_offset = height + 10
            for key, value in info.items():
                text = f"{key}: {value}"
                draw.text((10, y_offset), text, fill='black', font=font)
                y_offset += 20
            
            new_image.save(filename)
            print(f"[VISION] Capture annotée sauvée: {filename}")
            return str(filename)
            
        except Exception as e:
            print(f"[VISION ERROR] Erreur sauvegarde annotée: {e}")
            return ""
    
    def cleanup_old_screenshots(self, keep_days=7):
        """Nettoie les anciennes captures d'écran"""
        try:
            cutoff_time = time.time() - (keep_days * 24 * 3600)
            deleted_count = 0
            
            for file_path in self.screenshot_dir.glob("*.png"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                print(f"[VISION] {deleted_count} anciennes captures supprimées")
                
        except Exception as e:
            print(f"[VISION ERROR] Erreur nettoyage: {e}")


# Instance globale
screen_capture = ScreenCapture()