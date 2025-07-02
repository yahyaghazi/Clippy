"""
Interpréteur de commandes système pour l'Assistant IA
Fichier: src/core/command_interpreter.py
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class CommandInterpreter:
    """Interpréteur intelligent pour les commandes système directes"""
    
    def __init__(self):
        # Dictionnaire des commandes système avec patterns de détection
        self.system_commands = {
            # === ALIMENTATION ===
            "shutdown": {
                "patterns": [
                    r"éteins?\s*(le\s*)?pc", r"éteins?\s*(l['''])?ordinateur", 
                    r"arrêt", r"shutdown", r"ferme\s*(le\s*)?pc",
                    r"éteindre", r"arrête\s*(le\s*)?système"
                ],
                "command": "shutdown /s /t 0",
                "description": "Éteindre l'ordinateur",
                "danger_level": "high",
                "confirmation_required": True
            },
            "restart": {
                "patterns": [
                    r"redémarre", r"restart", r"reboot",
                    r"relance\s*(le\s*)?pc", r"redémarrage"
                ],
                "command": "shutdown /r /t 0", 
                "description": "Redémarrer l'ordinateur",
                "danger_level": "high",
                "confirmation_required": True
            },
            "sleep": {
                "patterns": [
                    r"mets?\s*en\s*veille", r"veille", r"sleep",
                    r"hibernation", r"mise\s*en\s*veille"
                ],
                "command": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                "description": "Mettre en veille",
                "danger_level": "low",
                "confirmation_required": False
            },
            
            # === AUDIO ===
            "volume_up": {
                "patterns": [
                    r"monte\s*(le\s*)?son", r"augmente\s*(le\s*)?volume",
                    r"plus\s*fort", r"volume\s*\+", r"son\s*\+"
                ],
                "command": "nircmd.exe changesysvolume 6553",  # +10%
                "description": "Augmenter le volume",
                "danger_level": "low", 
                "confirmation_required": False
            },
            "volume_down": {
                "patterns": [
                    r"baisse\s*(le\s*)?son", r"diminue\s*(le\s*)?volume",
                    r"moins\s*fort", r"volume\s*-", r"son\s*-"
                ],
                "command": "nircmd.exe changesysvolume -6553",  # -10%
                "description": "Diminuer le volume",
                "danger_level": "low",
                "confirmation_required": False
            },
            "mute": {
                "patterns": [
                    r"coupe\s*(le\s*)?son", r"mute", r"silence",
                    r"pas\s*de\s*son", r"muet", r"coupe\s*audio"
                ],
                "command": "nircmd.exe mutesysvolume 2",  # Toggle mute
                "description": "Couper/rétablir le son",
                "danger_level": "low",
                "confirmation_required": False
            },
            
            # === APPLICATIONS ===
            "close_chrome": {
                "patterns": [r"ferme\s*chrome", r"kill\s*chrome", r"arrête\s*chrome"],
                "command": "taskkill /f /im chrome.exe",
                "description": "Fermer Chrome",
                "danger_level": "medium",
                "confirmation_required": False
            },
            "close_firefox": {
                "patterns": [r"ferme\s*firefox", r"kill\s*firefox", r"arrête\s*firefox"],
                "command": "taskkill /f /im firefox.exe",
                "description": "Fermer Firefox", 
                "danger_level": "medium",
                "confirmation_required": False
            },
            "close_notepad": {
                "patterns": [r"ferme\s*notepad", r"ferme\s*bloc.*notes?"],
                "command": "taskkill /f /im notepad.exe",
                "description": "Fermer Notepad",
                "danger_level": "low",
                "confirmation_required": False
            },
            
            # === LANCEMENT D'APPLICATIONS ===
            "open_notepad": {
                "patterns": [
                    r"lance\s*notepad", r"ouvre\s*notepad", 
                    r"lance\s*bloc.*notes?", r"ouvre\s*bloc.*notes?"
                ],
                "command": "start notepad",
                "description": "Ouvrir Notepad",
                "danger_level": "low",
                "confirmation_required": False
            },
            "open_calc": {
                "patterns": [
                    r"lance\s*calculatrice", r"ouvre\s*calculatrice",
                    r"lance\s*calc", r"calculette"
                ],
                "command": "start calc",
                "description": "Ouvrir la calculatrice",
                "danger_level": "low",
                "confirmation_required": False
            },
            "open_paint": {
                "patterns": [r"lance\s*paint", r"ouvre\s*paint"],
                "command": "start mspaint",
                "description": "Ouvrir Paint",
                "danger_level": "low",
                "confirmation_required": False
            },
            
            # === RACCOURCIS SYSTÈME ===
            "show_desktop": {
                "patterns": [
                    r"montre\s*(le\s*)?bureau", r"affiche\s*(le\s*)?bureau",
                    r"minimise\s*tout", r"réduis\s*tout", r"bureau"
                ],
                "command": "nircmd.exe sendkeypress lwin+d",
                "description": "Afficher le bureau",
                "danger_level": "low",
                "confirmation_required": False
            },
            "task_manager": {
                "patterns": [
                    r"gestionnaire.*tâches?", r"task\s*manager",
                    r"ctrl\s*alt\s*del", r"gestionnaire.*processus"
                ],
                "command": "taskmgr",
                "description": "Ouvrir le gestionnaire de tâches",
                "danger_level": "low",
                "confirmation_required": False
            },
            "lock_screen": {
                "patterns": [
                    r"verrouille\s*(l['''])?écran", r"lock\s*screen",
                    r"verrouillage", r"session\s*lock"
                ],
                "command": "rundll32.exe user32.dll,LockWorkStation",
                "description": "Verrouiller la session",
                "danger_level": "medium",
                "confirmation_required": False
            },
            
            # === NETTOYAGE SYSTÈME ===
            "cleanup": {
                "patterns": [
                    r"nettoie\s*(le\s*)?pc", r"nettoyage\s*système",
                    r"vide\s*(la\s*)?corbeille", r"cleanup", r"nettoie\s*disque"
                ],
                "command": "cleanmgr /sagerun:1",
                "description": "Nettoyer le système",
                "danger_level": "medium",
                "confirmation_required": True
            },
            
            # === RÉSEAU ===
            "wifi_off": {
                "patterns": [
                    r"coupe\s*(le\s*)?wifi", r"désactive\s*(le\s*)?wifi",
                    r"wifi\s*off", r"pas\s*de\s*wifi"
                ],
                "command": "netsh interface set interface \"Wi-Fi\" disabled",
                "description": "Désactiver le WiFi",
                "danger_level": "medium",
                "confirmation_required": False
            },
            "wifi_on": {
                "patterns": [
                    r"active\s*(le\s*)?wifi", r"rallume\s*(le\s*)?wifi",
                    r"wifi\s*on", r"remet\s*(le\s*)?wifi"
                ],
                "command": "netsh interface set interface \"Wi-Fi\" enabled",
                "description": "Activer le WiFi",
                "danger_level": "low",
                "confirmation_required": False
            }
        }
        
        print(f"[COMMAND_INTERPRETER] {len(self.system_commands)} commandes système chargées")
    
    def detect_system_command(self, user_input: str) -> Optional[Dict]:
        """Détecte si l'entrée utilisateur correspond à une commande système"""
        user_input_clean = user_input.lower().strip()
        
        print(f"[COMMAND_INTERPRETER] Analyse: '{user_input_clean}'")
        
        for cmd_name, cmd_info in self.system_commands.items():
            for pattern in cmd_info["patterns"]:
                if re.search(pattern, user_input_clean, re.IGNORECASE):
                    print(f"[COMMAND_INTERPRETER] ✅ Détecté: {cmd_name} via pattern '{pattern}'")
                    
                    return {
                        "command_type": "system",
                        "action": cmd_name,
                        "command": cmd_info["command"],
                        "description": cmd_info["description"],
                        "danger_level": cmd_info["danger_level"],
                        "confirmation_required": cmd_info["confirmation_required"],
                        "detected_pattern": pattern,
                        "original_input": user_input
                    }
        
        print(f"[COMMAND_INTERPRETER] ❌ Aucune commande système détectée")
        return None
    
    def is_safe_command(self, command: str) -> Tuple[bool, str]:
        """Vérifie la sécurité d'une commande"""
        dangerous_patterns = [
            r"format\s+[a-z]:", r"del\s+/[fqs]", r"rmdir\s+/s",
            r"reg\s+delete", r"diskpart", r"fdisk",
            r"rm\s+-rf", r"dd\s+if=", r">\\\\\.\\",
            r"while\s*\(\s*true\s*\)", r":\w+\s*goto\s*\w+"
        ]
        
        command_lower = command.lower()
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command_lower):
                return False, f"Commande potentiellement dangereuse détectée: {pattern}"
        
        return True, "Commande validée"
    
    def get_confirmation_message(self, detected_command: Dict) -> str:
        """Génère un message de confirmation pour les commandes dangereuses"""
        action = detected_command["action"]
        description = detected_command["description"]
        danger_level = detected_command["danger_level"]
        
        danger_icons = {
            "high": "🚨",
            "medium": "⚠️", 
            "low": "ℹ️"
        }
        
        icon = danger_icons.get(danger_level, "❓")
        
        if danger_level == "high":
            return f"""{icon} ATTENTION - Action irréversible !

{description}
Commande: {detected_command['command']}

Êtes-vous sûr de vouloir continuer ?
Tapez 'OUI' pour confirmer ou 'NON' pour annuler."""
        
        elif danger_level == "medium":
            return f"""{icon} Confirmation requise

{description}
Cette action peut affecter le système.

Continuer ? (OUI/NON)"""
        
        else:
            return f"{icon} {description}"
    
    def create_enhanced_prompt(self, user_input: str) -> str:
        """Crée un prompt amélioré pour l'IA qui inclut la détection système"""
        
        # Vérifier d'abord si c'est une commande système
        system_cmd = self.detect_system_command(user_input)
        
        if system_cmd:
            # Si c'est une commande système, forcer la création d'un .bat
            return f"""
COMMANDE SYSTÈME DÉTECTÉE !

L'utilisateur demande: "{user_input}"
Action détectée: {system_cmd['description']}
Commande Windows: {system_cmd['command']}
Niveau de danger: {system_cmd['danger_level']}

Tu DOIS répondre avec ce JSON EXACT (aucune explication):
{{
    "action": "creer_et_executer_bat",
    "fichier": "{system_cmd['action']}_command.bat",
    "chemin": "system_commands",
    "instruction": "Commande système: {system_cmd['command']}",
    "type_fichier": "bat",
    "command_content": "{system_cmd['command']}",
    "danger_level": "{system_cmd['danger_level']}",
    "confirmation_required": {str(system_cmd['confirmation_required']).lower()}
}}
"""
        
        # Sinon, prompt normal avec exemples de commandes système
        return f"""
Tu es un assistant IA spécialisé dans la gestion de fichiers ET les commandes système Windows.

EXEMPLES DE COMMANDES SYSTÈME (utilise action "creer_et_executer_bat"):
- "éteins le pc" → {{"action": "creer_et_executer_bat", "fichier": "shutdown.bat", "instruction": "shutdown /s /t 0"}}
- "redémarre" → {{"action": "creer_et_executer_bat", "fichier": "restart.bat", "instruction": "shutdown /r /t 0"}}
- "monte le son" → {{"action": "creer_et_executer_bat", "fichier": "volume_up.bat", "instruction": "nircmd.exe changesysvolume 6553"}}
- "ferme chrome" → {{"action": "creer_et_executer_bat", "fichier": "close_chrome.bat", "instruction": "taskkill /f /im chrome.exe"}}
- "lance notepad" → {{"action": "creer_et_executer_bat", "fichier": "open_notepad.bat", "instruction": "start notepad"}}

EXEMPLES DE GESTION DE FICHIERS (logique normale):
- "crée un script python" → {{"action": "creer", "fichier": "script.py", "chemin": "python", "instruction": "...", "type_fichier": "py"}}
- "lance le fichier test" → {{"action": "lancer", "fichier": "test", "chemin": "", "instruction": "", "type_fichier": ""}}

⚠️ Réponds UNIQUEMENT avec un JSON valide. Aucune explication.

Commande : {user_input}
"""
    
    def list_available_commands(self) -> str:
        """Liste toutes les commandes système disponibles"""
        commands_by_category = {}
        
        for cmd_name, cmd_info in self.system_commands.items():
            # Déterminer la catégorie
            if "shutdown" in cmd_name or "restart" in cmd_name or "sleep" in cmd_name:
                category = "🔌 Alimentation"
            elif "volume" in cmd_name or "mute" in cmd_name:
                category = "🔊 Audio"
            elif "close_" in cmd_name:
                category = "❌ Fermer applications"
            elif "open_" in cmd_name:
                category = "🚀 Lancer applications"
            elif "wifi" in cmd_name:
                category = "🌐 Réseau"
            else:
                category = "⚙️ Système"
            
            if category not in commands_by_category:
                commands_by_category[category] = []
            
            # Prendre le premier pattern comme exemple
            example = cmd_info["patterns"][0].replace(r"\s*", " ").replace(r"\?", "")
            commands_by_category[category].append(f"  • \"{example}\" → {cmd_info['description']}")
        
        result = "📋 Commandes système disponibles:\n\n"
        for category, commands in commands_by_category.items():
            result += f"{category}:\n"
            result += "\n".join(commands)
            result += "\n\n"
        
        return result