"""
Parseur de commandes en langage naturel pour le contrôle système
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """Types d'actions système"""
    CLICK = "click"
    TYPE = "type"
    SCREENSHOT = "screenshot"
    FIND_TEXT = "find_text"
    SCROLL = "scroll"
    KEY_PRESS = "key_press"
    WINDOW_CONTROL = "window_control"
    APP_LAUNCH = "app_launch"
    FILE_OPERATION = "file_operation"
    MOUSE_MOVE = "mouse_move"
    WAIT = "wait"
    OCR_READ = "ocr_read"


@dataclass
class ParsedAction:
    """Action parsée depuis une commande"""
    action_type: ActionType
    parameters: Dict[str, Any]
    confidence: float
    original_text: str
    description: str


class CommandParser:
    """Parseur intelligent de commandes naturelles"""
    
    def __init__(self):
        # Patterns de reconnaissance
        self.patterns = self._load_command_patterns()
        
        # Mappings de synonymes
        self.synonyms = {
            'click': ['clique', 'cliquer', 'appuie', 'appuyer', 'tape', 'taper'],
            'type': ['écris', 'écrire', 'tape', 'taper', 'saisi', 'saisir'],
            'screenshot': ['capture', 'photo', 'image', 'copie écran'],
            'scroll': ['scroll', 'défiler', 'défile', 'fait défiler'],
            'window': ['fenêtre', 'fenetre', 'window'],
            'open': ['ouvre', 'ouvrir', 'lance', 'lancer', 'démarre', 'démarrer'],
            'close': ['ferme', 'fermer', 'quitte', 'quitter'],
            'find': ['trouve', 'trouver', 'cherche', 'chercher', 'recherche'],
            'move': ['déplace', 'déplacer', 'bouge', 'bouger'],
            'wait': ['attends', 'attendre', 'pause', 'délai']
        }
        
        print("[PARSER] Parseur de commandes initialisé")
    
    def _load_command_patterns(self) -> Dict[ActionType, List[Dict]]:
        """Charge les patterns de reconnaissance pour chaque type d'action"""
        return {
            ActionType.CLICK: [
                {
                    'pattern': r'clique?\s+(?:sur\s+)?(.+?)(?:\s+à\s+(\d+),?\s*(\d+))?',
                    'groups': ['target', 'x', 'y'],
                    'confidence': 0.9
                },
                {
                    'pattern': r'appui[er]?\s+(?:sur\s+)?(.+)',
                    'groups': ['target'],
                    'confidence': 0.8
                }
            ],
            
            ActionType.TYPE: [
                {
                    'pattern': r'(?:écri[st]?|tape|saisi[st]?)\s+["\'](.+?)["\']',
                    'groups': ['text'],
                    'confidence': 0.95
                },
                {
                    'pattern': r'(?:écri[st]?|tape|saisi[st]?)\s+(.+)',
                    'groups': ['text'],
                    'confidence': 0.8
                }
            ],
            
            ActionType.SCREENSHOT: [
                {
                    'pattern': r'(?:prends?\s+une\s+)?(?:capture|photo|image)(?:\s+d[\'u]\s*écran)?',
                    'groups': [],
                    'confidence': 0.9
                },
                {
                    'pattern': r'copie\s+l[\'e]\s*écran',
                    'groups': [],
                    'confidence': 0.8
                }
            ],
            
            ActionType.FIND_TEXT: [
                {
                    'pattern': r'(?:trouve|cherche|recherche)\s+(?:le\s+texte\s+)?["\'](.+?)["\']',
                    'groups': ['text'],
                    'confidence': 0.9
                },
                {
                    'pattern': r'(?:où\s+est|montre-moi)\s+(.+)',
                    'groups': ['text'],
                    'confidence': 0.7
                }
            ],
            
            ActionType.SCROLL: [
                {
                    'pattern': r'(?:scroll|défile?)\s+(?:vers\s+le\s+)?(haut|bas|gauche|droite)',
                    'groups': ['direction'],
                    'confidence': 0.9
                },
                {
                    'pattern': r'(?:scroll|défile?)\s+de\s+(\d+)',
                    'groups': ['amount'],
                    'confidence': 0.8
                }
            ],
            
            ActionType.KEY_PRESS: [
                {
                    'pattern': r'appui[er]?\s+sur\s+(?:la\s+touche\s+)?(.+)',
                    'groups': ['key'],
                    'confidence': 0.8
                },
                {
                    'pattern': r'(?:ctrl|alt|shift)\s*\+\s*(.+)',
                    'groups': ['combination'],
                    'confidence': 0.9
                }
            ],
            
            ActionType.WINDOW_CONTROL: [
                {
                    'pattern': r'(ferme|ouvre|minimise|maximise|redimensionne)\s+(?:la\s+)?fenêtre',
                    'groups': ['action'],
                    'confidence': 0.9
                },
                {
                    'pattern': r'(ferme|ouvre)\s+(.+)',
                    'groups': ['action', 'target'],
                    'confidence': 0.7
                }
            ],
            
            ActionType.APP_LAUNCH: [
                {
                    'pattern': r'(?:lance|ouvre|démarre)\s+(.+)',
                    'groups': ['app_name'],
                    'confidence': 0.8
                },
                {
                    'pattern': r'va\s+sur\s+(.+)',
                    'groups': ['website'],
                    'confidence': 0.7
                }
            ],
            
            ActionType.FILE_OPERATION: [
                {
                    'pattern': r'(?:crée|créer)\s+(?:un\s+)?(?:dossier|fichier)\s+(.+)',
                    'groups': ['filename'],
                    'confidence': 0.9
                },
                {
                    'pattern': r'(?:supprime|supprimer|efface|effacer)\s+(.+)',
                    'groups': ['filename'],
                    'confidence': 0.8
                }
            ],
            
            ActionType.MOUSE_MOVE: [
                {
                    'pattern': r'(?:déplace|bouge)\s+(?:la\s+)?souris\s+(?:vers\s+)?(\d+),?\s*(\d+)',
                    'groups': ['x', 'y'],
                    'confidence': 0.9
                },
                {
                    'pattern': r'va\s+(?:vers\s+|à\s+)?(\d+),?\s*(\d+)',
                    'groups': ['x', 'y'],
                    'confidence': 0.8
                }
            ],
            
            ActionType.WAIT: [
                {
                    'pattern': r'attends?\s+(\d+(?:\.\d+)?)\s*(seconde|minute)s?',
                    'groups': ['duration', 'unit'],
                    'confidence': 0.9
                },
                {
                    'pattern': r'pause\s+de\s+(\d+)',
                    'groups': ['duration'],
                    'confidence': 0.8
                }
            ],
            
            ActionType.OCR_READ: [
                {
                    'pattern': r'(?:lis|lire|dis-moi)\s+(?:ce\s+qui\s+est\s+)?(?:écrit|affiché)',
                    'groups': [],
                    'confidence': 0.9
                },
                {
                    'pattern': r'que\s+dit\s+l[\'e]\s*écran',
                    'groups': [],
                    'confidence': 0.8
                }
            ]
        }
    
    def parse_command(self, command: str) -> List[ParsedAction]:
        """Parse une commande en langage naturel"""
        command = command.lower().strip()
        
        if not command:
            return []
        
        print(f"[PARSER] Analyse: '{command}'")
        
        # Essayer de matcher chaque type d'action
        actions = []
        
        for action_type, patterns in self.patterns.items():
            for pattern_info in patterns:
                match = re.search(pattern_info['pattern'], command, re.IGNORECASE)
                
                if match:
                    # Extraire les paramètres
                    params = {}
                    for i, group_name in enumerate(pattern_info['groups']):
                        if i + 1 <= len(match.groups()) and match.group(i + 1):
                            params[group_name] = match.group(i + 1).strip()
                    
                    # Post-traitement des paramètres
                    params = self._post_process_parameters(action_type, params)
                    
                    # Créer l'action
                    action = ParsedAction(
                        action_type=action_type,
                        parameters=params,
                        confidence=pattern_info['confidence'],
                        original_text=command,
                        description=self._generate_description(action_type, params)
                    )
                    
                    actions.append(action)
                    break  # Première correspondance trouvée pour ce type
        
        # Trier par confiance décroissante
        actions.sort(key=lambda x: x.confidence, reverse=True)
        
        if actions:
            print(f"[PARSER] {len(actions)} action(s) détectée(s)")
            for action in actions[:3]:  # Afficher les 3 meilleures
                print(f"  - {action.action_type.value}: {action.description} (conf: {action.confidence})")
        else:
            print(f"[PARSER] Aucune action reconnue")
        
        return actions
    
    def _post_process_parameters(self, action_type: ActionType, params: Dict) -> Dict:
        """Post-traite les paramètres selon le type d'action"""
        if action_type == ActionType.CLICK:
            # Convertir coordonnées si présentes
            if 'x' in params and 'y' in params:
                try:
                    params['x'] = int(params['x'])
                    params['y'] = int(params['y'])
                except ValueError:
                    del params['x']
                    del params['y']
        
        elif action_type == ActionType.SCROLL:
            # Mapper direction vers valeurs numériques
            direction_map = {
                'haut': 3, 'up': 3,
                'bas': -3, 'down': -3,
                'gauche': -3, 'left': -3,
                'droite': 3, 'right': 3
            }
            
            if 'direction' in params:
                direction = params['direction'].lower()
                params['clicks'] = direction_map.get(direction, 1)
                params['horizontal'] = direction in ['gauche', 'droite', 'left', 'right']
            
            if 'amount' in params:
                try:
                    params['clicks'] = int(params['amount'])
                except ValueError:
                    params['clicks'] = 1
        
        elif action_type == ActionType.WAIT:
            # Convertir durée en secondes
            if 'duration' in params:
                try:
                    duration = float(params['duration'])
                    unit = params.get('unit', 'seconde').lower()
                    
                    if unit.startswith('minute'):
                        duration *= 60
                    
                    params['seconds'] = duration
                except ValueError:
                    params['seconds'] = 1.0
        
        elif action_type == ActionType.KEY_PRESS:
            # Traiter les combinaisons de touches
            if 'combination' in params:
                combo = params['combination'].lower()
                # Exemple: "ctrl+c" -> ["ctrl", "c"]
                keys = [k.strip() for k in combo.replace('+', ' ').split()]
                params['keys'] = keys
                del params['combination']
            
            if 'key' in params:
                key = params['key'].lower()
                # Mapper noms français vers noms anglais
                key_mapping = {
                    'entrée': 'enter',
                    'entree': 'enter',
                    'espace': 'space',
                    'retour': 'backspace',
                    'suppr': 'delete',
                    'échap': 'escape',
                    'echap': 'escape'
                }
                params['key'] = key_mapping.get(key, key)
        
        elif action_type == ActionType.MOUSE_MOVE:
            # Convertir coordonnées
            if 'x' in params and 'y' in params:
                try:
                    params['x'] = int(params['x'])
                    params['y'] = int(params['y'])
                except ValueError:
                    pass
        
        return params
    
    def _generate_description(self, action_type: ActionType, params: Dict) -> str:
        """Génère une description lisible de l'action"""
        if action_type == ActionType.CLICK:
            target = params.get('target', 'position')
            if 'x' in params and 'y' in params:
                return f"Cliquer sur {target} à ({params['x']}, {params['y']})"
            else:
                return f"Cliquer sur {target}"
        
        elif action_type == ActionType.TYPE:
            text = params.get('text', '')
            return f"Taper '{text[:30]}{'...' if len(text) > 30 else ''}'"
        
        elif action_type == ActionType.SCREENSHOT:
            return "Prendre une capture d'écran"
        
        elif action_type == ActionType.FIND_TEXT:
            text = params.get('text', '')
            return f"Chercher le texte '{text}'"
        
        elif action_type == ActionType.SCROLL:
            direction = "horizontal" if params.get('horizontal') else "vertical"
            clicks = params.get('clicks', 1)
            return f"Défilement {direction} de {clicks}"
        
        elif action_type == ActionType.KEY_PRESS:
            if 'keys' in params:
                return f"Raccourci {'+'.join(params['keys'])}"
            else:
                key = params.get('key', '')
                return f"Appuyer sur {key}"
        
        elif action_type == ActionType.WINDOW_CONTROL:
            action = params.get('action', 'contrôler')
            target = params.get('target', 'fenêtre')
            return f"{action.capitalize()} {target}"
        
        elif action_type == ActionType.APP_LAUNCH:
            app_name = params.get('app_name', params.get('website', ''))
            return f"Lancer {app_name}"
        
        elif action_type == ActionType.FILE_OPERATION:
            filename = params.get('filename', '')
            return f"Opération fichier: {filename}"
        
        elif action_type == ActionType.MOUSE_MOVE:
            x, y = params.get('x', 0), params.get('y', 0)
            return f"Déplacer souris vers ({x}, {y})"
        
        elif action_type == ActionType.WAIT:
            seconds = params.get('seconds', 1)
            return f"Attendre {seconds} seconde(s)"
        
        elif action_type == ActionType.OCR_READ:
            return "Lire le texte à l'écran"
        
        return f"Action {action_type.value}"
    
    def parse_complex_command(self, command: str) -> List[ParsedAction]:
        """Parse une commande complexe avec plusieurs actions"""
        # Diviser par des connecteurs
        separators = [' puis ', ' et ', ' ensuite ', ' après ']
        
        commands = [command]
        for sep in separators:
            new_commands = []
            for cmd in commands:
                new_commands.extend(cmd.split(sep))
            commands = new_commands
        
        # Parser chaque sous-commande
        all_actions = []
        for i, sub_command in enumerate(commands):
            sub_command = sub_command.strip()
            if sub_command:
                actions = self.parse_command(sub_command)
                
                # Ajouter un délai automatique entre actions
                if i > 0 and actions:
                    wait_action = ParsedAction(
                        action_type=ActionType.WAIT,
                        parameters={'seconds': 0.5},
                        confidence=0.8,
                        original_text="délai automatique",
                        description="Pause automatique entre actions"
                    )
                    all_actions.append(wait_action)
                
                all_actions.extend(actions)
        
        return all_actions
    
    def validate_action(self, action: ParsedAction) -> Tuple[bool, str]:
        """Valide qu'une action est exécutable"""
        if action.action_type == ActionType.CLICK:
            if 'target' not in action.parameters:
                return False, "Cible de clic non spécifiée"
        
        elif action.action_type == ActionType.TYPE:
            if 'text' not in action.parameters or not action.parameters['text']:
                return False, "Texte à taper non spécifié"
        
        elif action.action_type == ActionType.MOUSE_MOVE:
            if 'x' not in action.parameters or 'y' not in action.parameters:
                return False, "Coordonnées de déplacement manquantes"
            
            # Vérifier les limites d'écran
            try:
                import pyautogui
                screen_width, screen_height = pyautogui.size()
                x, y = action.parameters['x'], action.parameters['y']
                
                if not (0 <= x < screen_width and 0 <= y < screen_height):
                    return False, f"Coordonnées hors écran: ({x}, {y})"
            except:
                pass
        
        elif action.action_type == ActionType.WAIT:
            seconds = action.parameters.get('seconds', 0)
            if seconds <= 0 or seconds > 60:
                return False, f"Délai invalide: {seconds}s"
        
        return True, "Action valide"
    
    def get_action_help(self) -> Dict[str, List[str]]:
        """Retourne des exemples de commandes pour chaque type d'action"""
        return {
            'Clic': [
                "Clique sur le bouton OK",
                "Clique à 100, 200",
                "Appuie sur Enregistrer"
            ],
            'Frappe': [
                "Écris 'Bonjour le monde'",
                "Tape mon nom",
                "Saisis le mot de passe"
            ],
            'Capture': [
                "Prends une capture d'écran",
                "Fais une photo de l'écran",
                "Copie l'écran"
            ],
            'Recherche': [
                "Trouve le texte 'Connexion'",
                "Cherche 'mot de passe'",
                "Où est le bouton Valider ?"
            ],
            'Défilement': [
                "Scroll vers le bas",
                "Défile vers le haut",
                "Scroll de 5"
            ],
            'Touches': [
                "Appuie sur Entrée",
                "Ctrl+C",
                "Alt+Tab"
            ],
            'Applications': [
                "Lance Chrome",
                "Ouvre Word",
                "Va sur Google"
            ],
            'Attente': [
                "Attends 2 secondes",
                "Pause de 5",
                "Attends 1 minute"
            ]
        }


# Instance globale
command_parser = CommandParser()