# config.py
"""Configuration et constantes de l'application"""

# Configuration des modèles IA
MODEL_INFO = {
    "llama3": "🦙 Llama 3 - Polyvalent et performant",
    "mistral": "🌪️ Mistral - Rapide et efficace", 
    "codellama": "💻 CodeLlama - Spécialisé en code",
    "gemma": "💎 Gemma - Équilibré et précis",
    "llava": "🌋 LlaVa - Analyse les images" 
}

# Types de fichiers supportés
SUPPORTED_FILE_TYPES = [
    "pdf", "docx", "doc", "xlsx", "xls", "pptx", "ppt", 
    "txt", "csv", "rtf", "png", "jpg", "jpeg", "gif", "bmp", "tiff"
]

# Extensions d'images
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']

# Types MIME d'images
IMAGE_MIME_TYPES = ['image/', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff']

# Configuration Streamlit
PAGE_CONFIG = {
    "page_title": "Assistant IA",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# CSS personnalisé
CUSTOM_CSS = """
<style>
.main-header {
    text-align: center;
    padding: 1rem 0;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 2rem;
}
.chat-message-user {
    background-color: #e3f2fd;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
}
.chat-message-assistant {
    background-color: #f5f5f5;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
}
.sidebar-info {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
.multi-file-container {
    background-color: #f8f9fa;
    border: 2px dashed #dee2e6;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}
.file-item {
    background-color: white;
    border: 1px solid #e9ecef;
    border-radius: 5px;
    padding: 0.5rem;
    margin: 0.5rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.pending-files {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}
.analysis-section {
    background-color: #d1ecf1;
    border: 1px solid #b8daff;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
"""

# Paramètres par défaut
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1200  # Augmenté pour les analyses multi-fichiers
DEFAULT_MODEL_INDEX = 1  # Mistral par défaut

# Messages d'aide
HELP_MESSAGES = {
    "file_formats": "Formats supportés: PDF, Word, Excel, PowerPoint, Images (PNG/JPG/JPEG/GIF/BMP/TIFF), Texte, CSV, RTF",
    "multi_upload": "💡 Vous pouvez uploader plusieurs fichiers et poser une question globale",
    "image_model_suggestion": "🖼️ Image détectée - Utilisez le modèle LlaVa pour une analyse optimale",
    "image_model_warning": "⚠️ Pour une analyse optimale des images, utilisez le modèle LlaVa",
    "llava_suggestion": "💡 Pour analyser les images, utilisez le modèle LlaVa",
    "ollama_check": "💡 Vérifiez que le modèle Ollama est bien démarré",
    "multi_analysis": "🔍 Analyse croisée de tous les documents en cours...",
    "pending_files": "📁 Fichiers en attente d'analyse. Ajoutez une question pour lancer l'analyse globale."
}