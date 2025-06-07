# 🤖 Assistant IA Local - Clippy Moderne

Un assistant IA local moderne inspiré de Clippy, avec intelligence artificielle intégrée via Ollama.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## ✨ Fonctionnalités

- 🤖 **Assistant IA intelligent** avec suggestions contextuelles
- 👁️ **Surveillance système** non-intrusive des applications
- 🎭 **Personnage animé** avec expressions et humeurs
- 🔊 **Synthèse vocale** intégrée (français supporté)
- 💬 **Interface moderne** flottante et déplaçable
- 🔐 **100% local** - aucune donnée envoyée sur Internet
- ⚙️ **Modulaire et extensible**

## 📸 Captures d'écran

```
┌─────────────────────┐
│ 🤖 Assistant IA   🔊│
├─────────────────────┤
│                     │
│       😊            │
│   (Personnage)      │
│                     │
├─────────────────────┤
│ 📱 Opera            │
│ 🕒 Navigation web   │
│                     │
│ 💡 Essaie Ctrl+T   │
│ pour rouvrir un     │
│ onglet fermé !      │
└─────────────────────┘
```

## 🚀 Installation rapide

### Prérequis

- **Python 3.8+**
- **Ollama** installé et configuré
- **Windows** (support Linux/Mac prévu)

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/ai-assistant.git
cd ai-assistant
```

### 2. Installer les dépendances

```bash
# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configurer Ollama

```bash
# Installer Ollama (si pas déjà fait)
# https://ollama.ai

# Démarrer Ollama
ollama serve

# Télécharger un modèle (dans un autre terminal)
ollama pull llama3.2
```

### 4. Lancer l'assistant

```bash
python main.py
```

## 🎮 Utilisation

### Contrôles de base

- **🖱️ Clic sur le personnage** → Nouveau conseil
- **🔄 Bouton bleu** → Actualiser la suggestion
- **🔊 Bouton violet** → Activer/désactiver la voix
- **⚙️ Bouton vert** → Paramètres
- **Glisser la barre de titre** → Déplacer la fenêtre

### Obtenir des suggestions

L'assistant analyse automatiquement votre activité et propose des conseils selon :

- **Application active** (Chrome, VS Code, Word...)
- **Contexte d'utilisation**
- **Heure de la journée**

### Exemples de suggestions

| Application | Suggestion |
|-------------|------------|
| **Chrome/Opera** | "Essaie Ctrl+Shift+T pour rouvrir un onglet fermé !" |
| **VS Code** | "N'oublie pas Ctrl+Shift+P pour la palette de commandes !" |
| **Word** | "Pour une meilleure lisibilité, utilise des paragraphes courts." |
| **PowerShell** | "Tape 'cls' pour nettoyer l'écran et Tab pour l'autocomplétion." |

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `.env` :

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT=15

# Interface
UI_WINDOW_WIDTH=200
UI_WINDOW_HEIGHT=250
DEBUG=false

# Monitoring
MONITOR_INTERVAL=5
```

### Personnalisation de la voix

```python
# Dans le code ou via l'interface
voice_engine.set_voice_properties(
    rate=180,      # Vitesse (mots/minute)
    volume=0.8,    # Volume (0.0 à 1.0)
    voice_id=None  # ID de voix spécifique
)
```

## 🏗️ Architecture

```
AI_chat/
├── src/
│   ├── config/          # Configuration
│   ├── core/           # Logique métier
│   │   ├── ollama_client.py
│   │   └── system_monitor.py
│   ├── ui/             # Interface utilisateur
│   │   ├── main_window.py
│   │   ├── character.py
│   │   └── speech_bubble.py
│   └── utils/          # Utilitaires
│   │   ├── voice_engine.py
│   │   └── app_mapper.py
│   │
│   ├── vision/                 # 🆕 NOUVEAU - Vision système
│   │   ├── __init__.py
│   │   ├── screen_capture.py   # Capture d'écran
│   │   ├── ocr_engine.py       # Reconnaissance texte
│   │   └── visual_analyzer.py  # Analyse visuelle
│   │
│   ├── control/                # 🆕 NOUVEAU - Contrôle système
│   │   ├── __init__.py
│   │   ├── mouse_controller.py # Contrôle souris
│   │   ├── keyboard_controller.py # Contrôle clavier
│   │   └── system_commander.py # Commandes système
│   │
│   └── ai_system/              # 🆕 NOUVEAU - IA système
│       ├── __init__.py
│       ├── command_parser.py   # Parse commandes naturelles
│       ├── action_executor.py  # Exécute les actions
│       └── safety_manager.py   # Sécurité et validations
│
├── requirements_system.txt     # 🆕 Nouvelles dépendances
├── test_system.py             # 🆕 Tests modules système
└── main_system.py             # 🆕 Version système étendue
```

## 🔧 Développement

### Structure du code

- **Modulaire** : Chaque composant dans son module
- **Configuré** : Paramètres centralisés
- **Extensible** : Facile d'ajouter des fonctionnalités
- **Testé** : Tests unitaires inclus

### Ajouter une nouvelle fonctionnalité

1. **Créer le module** dans le bon dossier (`core/`, `ui/`, `utils/`)
2. **Importer** dans `main_window.py`
3. **Configurer** dans `settings.py`
4. **Tester** avec les tests unitaires

### Personnaliser les suggestions

Modifiez `core/ollama_client.py` :

```python
def _create_contextual_prompt(self, app_name, context, category):
    # Ajouter vos propres prompts ici
    custom_prompts = {
        'MonApp': "Conseil spécifique pour MonApp..."
    }
```

## 🐛 Résolution de problèmes

### Problèmes courants

| Problème | Solution |
|----------|----------|
| **"Ollama non connecté"** | `ollama serve` puis relancer |
| **Pas de voix** | Installer `pip install pyttsx3` |
| **Fenêtre disparue** | Clic droit sur la barre des tâches |
| **Applications non détectées** | Vérifier les permissions |

### Debug

Activez le mode debug :

```bash
# Dans .env
DEBUG=true

# Ou en lançant
python main.py --debug
```

### Logs

Les logs se trouvent dans :
- **Console** : Messages temps réel
- **ai_assistant.log** : Fichier de log rotatif

## 🤝 Contribution

### Workflow

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/amazing-feature`)
3. **Commit** vos changes (`git commit -m 'Add amazing feature'`)
4. **Push** vers la branche (`git push origin feature/amazing-feature`)
5. **Ouvrir** une Pull Request

### Guidelines

- **Code** : Suivre PEP 8
- **Tests** : Ajouter des tests pour nouvelles fonctionnalités
- **Documentation** : Mettre à jour la doc
- **Messages** : Commits clairs et descriptifs

## 📊 Roadmap

### Version 1.1 (Prochaine)
- [ ] 🌙 Mode sombre/clair
- [ ] ⌨️ Raccourcis clavier configurables
- [ ] 📊 Statistiques d'utilisation
- [ ] 🎨 Plus d'animations personnage

### Version 1.2
- [ ] 👁️ OCR pour lire le contenu à l'écran
- [ ] 🔗 Intégration avec d'autres modèles IA
- [ ] 🌐 Support multi-langues
- [ ] 📱 Version mobile/web

### Version 2.0
- [ ] 🧠 Apprentissage des habitudes utilisateur
- [ ] 🔌 API pour extensions tierces
- [ ] ☁️ Synchronisation cloud (optionnelle)
- [ ] 🤖 Assistant vocal bidirectionnel

## 📄 License

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour les détails.

## 💖 Remerciements

- **Ollama** pour l'IA locale
- **pyttsx3** pour la synthèse vocale
- **PySide6/Tkinter** pour l'interface
- **psutil** pour la surveillance système
- **Clippy** pour l'inspiration originale ! 📎

## 📞 Support

- 🐛 **Issues** : [GitHub Issues](https://github.com/votre-username/ai-assistant/issues)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/votre-username/ai-assistant/discussions)
- 📧 **Email** : votre-email@example.com

---

**Fait avec ❤️ par [Votre Nom]**

*Un assistant IA local pour une productivité décuplée !* 🚀