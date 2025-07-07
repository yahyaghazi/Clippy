# === CORRECTION DU FICHIER src/config/settings.py ===

"""
Configuration settings for AI Assistant
Version corrigée pour éviter les erreurs 404
"""

import os
from typing import Dict, List
from dataclasses import dataclass



@dataclass
class OllamaConfig:
    """Configuration pour Ollama"""
    base_url: str = "http://localhost:11434"
    model: str = "mistral:latest"  # Modèle par défaut changé
    timeout: int = 60  # Timeout en secondes
    max_tokens: int = 1000  # Nombre de jetons maximum
    temperature: float = 0.7 # Température pour la génération de texte


@dataclass
class UIConfig:
    """Configuration interface utilisateur"""
    window_width: int = 300
    window_height: int = 400
    always_on_top: bool = True
    background_color: str = "#f0f0f0"
    character_size: int = 80
    
    # Position initiale (offset depuis coin bas-droit)
    initial_x_offset: int = 320
    initial_y_offset: int = 450


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
                'dwm.exe', 'svchost.exe', 'services.exe', 'lsass.exe'
            ]


@dataclass
class FeaturesConfig:
    """Configuration des fonctionnalités"""
    enable_voice_synthesis: bool = True
    enable_speech_recognition: bool = True
    enable_file_management: bool = True
    enable_web_research: bool = True
    enable_document_generation: bool = True


@dataclass
class AppSettings:
    """Configuration principale de l'application"""
    # Modules de configuration
    ollama: OllamaConfig = None
    ui: UIConfig = None
    monitoring: MonitoringConfig = None
    features: FeaturesConfig = None
    
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
        if self.features is None:
            self.features = FeaturesConfig()


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
    
    # Features
    settings.features.enable_web_research = os.getenv("ENABLE_WEB_RESEARCH", "false").lower() == "true"
    
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