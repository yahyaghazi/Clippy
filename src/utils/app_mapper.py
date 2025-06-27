"""
Mapping des noms d'applications pour un affichage convivial
"""

from typing import Dict, Tuple
import time


class AppMapper:
    """Classe pour mapper les noms de processus vers des noms conviviaux"""
    
    def __init__(self):
        self.app_names: Dict[str, str] = {
            # Navigateurs
            'chrome.exe': 'Chrome',
            'firefox.exe': 'Firefox', 
            'msedge.exe': 'Edge',
            'opera.exe': 'Opera',
            'brave.exe': 'Brave',
            'safari.exe': 'Safari',
            
            # Éditeurs de texte/code
            'notepad.exe': 'Bloc-notes',
            'notepad++.exe': 'Notepad++',
            'code.exe': 'VS Code',
            'sublime_text.exe': 'Sublime Text',
            'atom.exe': 'Atom',
            'vim.exe': 'Vim',
            'emacs.exe': 'Emacs',
            
            # Suite Office
            'winword.exe': 'Word',
            'excel.exe': 'Excel',
            'powerpnt.exe': 'PowerPoint',
            'outlook.exe': 'Outlook',
            'onenote.exe': 'OneNote',
            
            # Développement
            'python.exe': 'Python',
            'node.exe': 'Node.js',
            'java.exe': 'Java',
            'javaw.exe': 'Java',
            'php.exe': 'PHP',
            'ruby.exe': 'Ruby',
            'go.exe': 'Go',
            'rust.exe': 'Rust',
            
            # IDEs
            'pycharm64.exe': 'PyCharm',
            'idea64.exe': 'IntelliJ IDEA',
            'devenv.exe': 'Visual Studio',
            'eclipse.exe': 'Eclipse',
            
            # Système
            'explorer.exe': 'Explorateur',
            'cmd.exe': 'Invite de commandes',
            'powershell.exe': 'PowerShell',
            'conhost.exe': 'Console',
            
            # Communication
            'discord.exe': 'Discord',
            'slack.exe': 'Slack',
            'teams.exe': 'Teams',
            'zoom.exe': 'Zoom',
            'skype.exe': 'Skype',
            'telegram.exe': 'Telegram',
            'whatsapp.exe': 'WhatsApp',
            
            # Multimédia
            'spotify.exe': 'Spotify',
            'vlc.exe': 'VLC',
            'wmplayer.exe': 'Windows Media Player',
            'itunes.exe': 'iTunes',
            'photoshop.exe': 'Photoshop',
            'gimp.exe': 'GIMP',
            
            # Gaming
            'steam.exe': 'Steam',
            'origin.exe': 'Origin',
            'epicgameslauncher.exe': 'Epic Games',
            'battle.net.exe': 'Battle.net',
            
            # Autres
            'winrar.exe': 'WinRAR',
            '7zfm.exe': '7-Zip',
            'totalcmd.exe': 'Total Commander',
            'filezilla.exe': 'FileZilla'
        }
        
        self.context_templates: Dict[str, str] = {
            # Navigateurs
            'Chrome': "Navigation web ({time})",
            'Firefox': "Navigation web ({time})",
            'Edge': "Navigation web ({time})",
            'Opera': "Navigation web ({time})",
            
            # Productivité
            'Word': "Rédaction de document ({time})",
            'Excel': "Travail sur tableur ({time})",
            'PowerPoint': "Création de présentation ({time})",
            'Outlook': "Gestion des emails ({time})",
            
            # Développement
            'VS Code': "Développement ({time})",
            'PyCharm': "Développement Python ({time})",
            'Python': "Programmation Python ({time})",
            'Node.js': "Développement JavaScript ({time})",
            
            # Système
            'PowerShell': "Administration système ({time})",
            'Invite de commandes': "Ligne de commande ({time})",
            'Explorateur': "Gestion de fichiers ({time})",
            
            # Communication
            'Discord': "Communication ({time})",
            'Teams': "Réunion/Communication ({time})",
            'Slack': "Communication d'équipe ({time})",
            
            # Multimédia
            'Spotify': "Écoute de musique ({time})",
            'VLC': "Lecture vidéo/audio ({time})"
        }
    
    def get_display_name(self, process_name: str) -> str:
        """Convertit un nom de processus en nom d'affichage convivial"""
        clean_name = process_name.lower()
        return self.app_names.get(clean_name, process_name.replace('.exe', '').title())
    
    def get_context(self, app_name: str) -> str:
        """Génère un contexte pour l'application"""
        current_time = time.strftime("%H:%M")
        
        if app_name in self.context_templates:
            return self.context_templates[app_name].format(time=current_time)
        else:
            return f"Utilisation de {app_name} ({current_time})"
    
    def add_custom_mapping(self, process_name: str, display_name: str, context_template: str = None):
        """Ajoute un mapping personnalisé"""
        self.app_names[process_name.lower()] = display_name
        
        if context_template:
            self.context_templates[display_name] = context_template
        else:
            self.context_templates[display_name] = f"Utilisation de {display_name} ({{time}})"
    
    def get_app_category(self, app_name: str) -> str:
        """Retourne la catégorie de l'application"""
        categories = {
            'Navigation': ['Chrome', 'Firefox', 'Edge', 'Opera', 'Brave', 'Safari'],
            'Développement': ['VS Code', 'PyCharm', 'Python', 'Node.js', 'Java', 'IntelliJ IDEA'],
            'Bureautique': ['Word', 'Excel', 'PowerPoint', 'Outlook', 'OneNote'],
            'Communication': ['Discord', 'Teams', 'Slack', 'Zoom', 'Skype'],
            'Multimédia': ['Spotify', 'VLC', 'Photoshop', 'GIMP'],
            'Système': ['PowerShell', 'Invite de commandes', 'Explorateur'],
            'Gaming': ['Steam', 'Origin', 'Epic Games']
        }
        
        for category, apps in categories.items():
            if app_name in apps:
                return category
        
        return 'Autre'


# Instance globale
app_mapper = AppMapper()