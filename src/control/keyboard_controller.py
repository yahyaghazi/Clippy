"""
Contrôleur de clavier pour automation système
"""

import pyautogui
import time
from typing import List, Union, Dict
import random


class KeyboardController:
    """Contrôleur intelligent du clavier"""
    
    def __init__(self):
        # Configuration
        pyautogui.PAUSE = 0.05  # Pause courte entre frappes
        
        # Vitesse de frappe
        self.typing_interval = 0.03  # Délai entre caractères
        self.human_like_typing = True
        
        # Mappings des touches spéciales
        self.special_keys = {
            'enter': 'enter',
            'tab': 'tab',
            'space': 'space',
            'backspace': 'backspace',
            'delete': 'delete',
            'escape': 'esc',
            'shift': 'shift',
            'ctrl': 'ctrl',
            'alt': 'alt',
            'win': 'win',
            'home': 'home',
            'end': 'end',
            'pageup': 'pageup',
            'pagedown': 'pagedown',
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
            'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
            'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12'
        }
        
        print("[KEYBOARD] Contrôleur clavier initialisé")
    
    def type_text(self, text: str, interval: float = None, human_like: bool = None) -> bool:
        """Tape du texte avec simulation naturelle"""
        try:
            interval = interval or self.typing_interval
            human_like = human_like if human_like is not None else self.human_like_typing
            
            if human_like:
                # Simulation de frappe humaine avec variations
                for char in text:
                    pyautogui.write(char)
                    
                    # Variation aléatoire du délai
                    varied_interval = interval + random.uniform(-0.01, 0.02)
                    time.sleep(max(0.001, varied_interval))
                    
                    # Pauses plus longues après ponctuation
                    if char in '.,;:!?':
                        time.sleep(random.uniform(0.1, 0.3))
            else:
                # Frappe rapide et régulière
                pyautogui.write(text, interval=interval)
            
            print(f"[KEYBOARD] Texte tapé: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur frappe: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Appuie sur une touche"""
        try:
            # Convertir en nom pyautogui si nécessaire
            key_name = self.special_keys.get(key.lower(), key)
            pyautogui.press(key_name)
            print(f"[KEYBOARD] Touche pressée: {key}")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur touche {key}: {e}")
            return False
    
    def press_keys(self, keys: List[str]) -> bool:
        """Appuie sur plusieurs touches en séquence"""
        try:
            for key in keys:
                if not self.press_key(key):
                    return False
                time.sleep(0.05)  # Petite pause entre touches
            
            print(f"[KEYBOARD] Séquence de touches: {' -> '.join(keys)}")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur séquence: {e}")
            return False
    
    def hotkey(self, *keys) -> bool:
        """Exécute un raccourci clavier (touches simultanées)"""
        try:
            # Convertir les noms de touches
            converted_keys = [self.special_keys.get(key.lower(), key) for key in keys]
            pyautogui.hotkey(*converted_keys)
            print(f"[KEYBOARD] Raccourci: {'+'.join(keys)}")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur raccourci {'+'.join(keys)}: {e}")
            return False
    
    def key_down(self, key: str) -> bool:
        """Maintient une touche enfoncée"""
        try:
            key_name = self.special_keys.get(key.lower(), key)
            pyautogui.keyDown(key_name)
            print(f"[KEYBOARD] Touche maintenue: {key}")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur key_down {key}: {e}")
            return False
    
    def key_up(self, key: str) -> bool:
        """Relâche une touche"""
        try:
            key_name = self.special_keys.get(key.lower(), key)
            pyautogui.keyUp(key_name)
            print(f"[KEYBOARD] Touche relâchée: {key}")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur key_up {key}: {e}")
            return False
    
    def hold_key_and_press(self, hold_key: str, press_keys: List[str]) -> bool:
        """Maintient une touche et appuie sur d'autres"""
        try:
            # Maintenir la première touche
            if not self.key_down(hold_key):
                return False
            
            time.sleep(0.05)
            
            # Appuyer sur les autres touches
            for key in press_keys:
                if not self.press_key(key):
                    self.key_up(hold_key)  # Relâcher en cas d'erreur
                    return False
                time.sleep(0.05)
            
            # Relâcher la touche maintenue
            time.sleep(0.05)
            self.key_up(hold_key)
            
            print(f"[KEYBOARD] Combinaison: {hold_key} + {'+'.join(press_keys)}")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur combinaison: {e}")
            try:
                self.key_up(hold_key)  # S'assurer de relâcher
            except:
                pass
            return False
    
    def type_with_corrections(self, text: str, error_rate: float = 0.02) -> bool:
        """Tape avec des erreurs et corrections simulées"""
        try:
            if not self.human_like_typing:
                return self.type_text(text)
            
            for i, char in enumerate(text):
                # Simulation d'erreur occasionnelle
                if random.random() < error_rate:
                    # Taper un caractère incorrect
                    wrong_char = random.choice('qwertyuiopasdfghjklzxcvbnm')
                    pyautogui.write(wrong_char)
                    time.sleep(self.typing_interval)
                    
                    # Corriger (backspace puis bon caractère)
                    time.sleep(random.uniform(0.1, 0.5))  # Pause "réalisation erreur"
                    pyautogui.press('backspace')
                    time.sleep(self.typing_interval)
                
                # Taper le bon caractère
                pyautogui.write(char)
                
                # Variation du délai
                varied_interval = self.typing_interval + random.uniform(-0.01, 0.02)
                time.sleep(max(0.001, varied_interval))
            
            print(f"[KEYBOARD] Texte tapé avec corrections: '{text[:30]}...'")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur frappe avec corrections: {e}")
            return False
    
    def clear_field(self, method: str = 'ctrl_a') -> bool:
        """Efface un champ de texte"""
        try:
            if method == 'ctrl_a':
                # Sélectionner tout et supprimer
                self.hotkey('ctrl', 'a')
                time.sleep(0.1)
                self.press_key('delete')
                
            elif method == 'ctrl_backspace':
                # Effacer mot par mot
                for _ in range(10):  # Maximum 10 mots
                    self.hotkey('ctrl', 'backspace')
                    time.sleep(0.05)
                    
            elif method == 'end_backspace':
                # Aller à la fin et effacer caractère par caractère
                self.press_key('end')
                time.sleep(0.05)
                for _ in range(100):  # Maximum 100 caractères
                    self.press_key('backspace')
                    time.sleep(0.01)
            
            print(f"[KEYBOARD] Champ effacé (méthode: {method})")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur effacement: {e}")
            return False
    
    def navigate_text(self, direction: str, units: int = 1, select: bool = False) -> bool:
        """Navigation dans le texte"""
        try:
            key_map = {
                'left': 'left',
                'right': 'right',
                'up': 'up',
                'down': 'down',
                'word_left': ['ctrl', 'left'],
                'word_right': ['ctrl', 'right'],
                'line_start': 'home',
                'line_end': 'end',
                'doc_start': ['ctrl', 'home'],
                'doc_end': ['ctrl', 'end']
            }
            
            if direction not in key_map:
                print(f"[KEYBOARD] Direction inconnue: {direction}")
                return False
            
            keys = key_map[direction]
            
            # Ajouter shift si sélection demandée
            if select:
                if isinstance(keys, list):
                    keys = ['shift'] + keys
                else:
                    keys = ['shift', keys]
            
            # Répéter le mouvement
            for _ in range(units):
                if isinstance(keys, list):
                    self.hotkey(*keys)
                else:
                    self.press_key(keys)
                time.sleep(0.05)
            
            print(f"[KEYBOARD] Navigation: {direction} x{units} {'(sélection)' if select else ''}")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur navigation: {e}")
            return False
    
    def paste_text(self, text: str = None) -> bool:
        """Colle du texte (depuis presse-papiers ou texte donné)"""
        try:
            if text:
                # Mettre le texte dans le presse-papiers puis coller
                import pyperclip
                pyperclip.copy(text)
                time.sleep(0.1)
            
            self.hotkey('ctrl', 'v')
            print(f"[KEYBOARD] Texte collé")
            return True
            
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur collage: {e}")
            return False
    
    def copy_text(self) -> bool:
        """Copie le texte sélectionné"""
        try:
            self.hotkey('ctrl', 'c')
            print("[KEYBOARD] Texte copié")
            return True
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur copie: {e}")
            return False
    
    def cut_text(self) -> bool:
        """Coupe le texte sélectionné"""
        try:
            self.hotkey('ctrl', 'x')
            print("[KEYBOARD] Texte coupé")
            return True
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur coupe: {e}")
            return False
    
    def undo(self, times: int = 1) -> bool:
        """Annule les dernières actions"""
        try:
            for _ in range(times):
                self.hotkey('ctrl', 'z')
                time.sleep(0.1)
            print(f"[KEYBOARD] Annulation x{times}")
            return True
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur annulation: {e}")
            return False
    
    def redo(self, times: int = 1) -> bool:
        """Refait les dernières actions annulées"""
        try:
            for _ in range(times):
                self.hotkey('ctrl', 'y')
                time.sleep(0.1)
            print(f"[KEYBOARD] Refaire x{times}")
            return True
        except Exception as e:
            print(f"[KEYBOARD ERROR] Erreur refaire: {e}")
            return False
    
    def set_typing_speed(self, speed: str):
        """Configure la vitesse de frappe"""
        speeds = {
            'very_slow': 0.15,
            'slow': 0.08,
            'normal': 0.03,
            'fast': 0.01,
            'very_fast': 0.005
        }
        
        if speed in speeds:
            self.typing_interval = speeds[speed]
            print(f"[KEYBOARD] Vitesse configurée: {speed}")
        else:
            print(f"[KEYBOARD] Vitesse inconnue: {speed}")
    
    def enable_human_typing(self, enabled: bool = True):
        """Active/désactive la simulation de frappe humaine"""
        self.human_like_typing = enabled
        mode = "activée" if enabled else "désactivée"
        print(f"[KEYBOARD] Frappe humaine {mode}")


# Instance globale
keyboard_controller = KeyboardController()