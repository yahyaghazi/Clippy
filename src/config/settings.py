"""
Configuration settings for AI Assistant
"""

import os
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class OllamaConfig:
    """Configuration pour Ollama"""
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2"
    timeout: int = 15
    max_tokens: int = 100
    temperature: float = 0.7


@dataclass
class UIConfig:
    """Configuration interface utilisateur"""
    window_width: int = 200
    window_height: int = 250
    always_on_top: bool = True
    background_color: str = "#f0f0f0"
    character_size: int = 80
    
    # Position initiale (offset depuis coin bas-droit)
    initial_x_offset: int = 220
    initial_y_offset: int = 300


@dataclass
class MonitoringConfig:
    """Configuration surveillance système"""
    check_interval: int = 5  # secondes
    score_memory_threshold: int = 50  # MB pour le score
    
    # Processus à ignorer
    ignored_processes: List[str] = None
    
    def __post_init__(self):
        if self.ignored_processes is None:
            self.ignored_processes = [
                'system', 'registry', 'csrss.exe', 'winlogon.exe',
                'dwm.exe', 'svchost.exe', 'services.exe', 'lsass.exe',
                'explorer.exe'  # On peut l'enlever si on veut surveiller l'explorateur
            ]


@dataclass
class AppSettings:
    """Configuration principale de l'application"""
    # Modules de configuration
    ollama: OllamaConfig = None
    ui: UIConfig = None
    monitoring: MonitoringConfig = None
    
    # Paramètres généraux
    debug_mode: bool = False
    log_level: str = "INFO"
    log_file: str = "ai_assistant.log"
    
    def __post_init__(self):
        if self.ollama is None:
            self.ollama = OllamaConfig()
        if self.ui is None:
            self.ui = UIConfig()
        if self.monitoring is None:
            self.monitoring = MonitoringConfig()


# Instance globale des paramètres
settings = AppSettings()


def load_settings_from_env():
    """Charge les paramètres depuis les variables d'environnement"""
    # Ollama
    settings.ollama.base_url = os.getenv("OLLAMA_BASE_URL", settings.ollama.base_url)
    settings.ollama.model = os.getenv("OLLAMA_MODEL", settings.ollama.model)
    settings.ollama.timeout = int(os.getenv("OLLAMA_TIMEOUT", settings.ollama.timeout))
    
    # UI
    settings.ui.window_width = int(os.getenv("UI_WINDOW_WIDTH", settings.ui.window_width))
    settings.ui.window_height = int(os.getenv("UI_WINDOW_HEIGHT", settings.ui.window_height))
    
    # Monitoring
    settings.monitoring.check_interval = int(os.getenv("MONITOR_INTERVAL", settings.monitoring.check_interval))
    
    # Debug
    settings.debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    settings.log_level = os.getenv("LOG_LEVEL", settings.log_level)


def update_setting(section: str, key: str, value):
    """Met à jour un paramètre dynamiquement"""
    if hasattr(settings, section):
        section_obj = getattr(settings, section)
        if hasattr(section_obj, key):
            setattr(section_obj, key, value)
            return True
    return False


# Charger les paramètres au démarrage
load_settings_from_env()