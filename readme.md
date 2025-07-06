# 📎 Assistant Clippy IA - Version Stable

Un assistant IA local moderne inspiré de Clippy avec fonctionnalités essentielles.

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## ✨ Fonctionnalités Principales

### 🤖 Intelligence Artificielle
- **Assistant IA contextuel** avec suggestions selon l'application active
- **Chat intelligent** pour conversations naturelles
- **Gestion de fichiers IA** - création de scripts, documents, PDFs
- **Génération de code** dans plusieurs langages (Python, HTML, JS)

### 🎤 Interface Vocale (Optionnelle)
- **Reconnaissance vocale** en français
- **Synthèse vocale** avec voix française
- **Commandes vocales** pour contrôler l'assistant
- **Mode mains libres**

### 👁️ Surveillance Intelligente
- **Détection automatique** des applications actives
- **Suggestions contextuelles** selon votre travail
- **Monitoring non-intrusif** en arrière-plan

### 🎭 Personnage Clippy Animé
- **Animations fluides** selon l'humeur
- **Expressions contextuelles**
- **Interactions visuelles** au clic
- **Style nostalgique** modernisé

## 🚀 Installation Rapide

### Prérequis
- **Python 3.8+**
- **Ollama** installé et configuré
- **Windows/Linux/macOS**

### 1. Installation de base
```bash
# Cloner le projet
git clone https://github.com/votre-repo/clippy-ai.git
cd clippy-ai

# Environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Dépendances minimales
pip install psutil requests
```

### 2. Installation complète (recommandée)
```bash
# Toutes les fonctionnalités
pip install -r requirements.txt
```

### 3. Configurer Ollama
```bash
# Démarrer Ollama (terminal séparé)
ollama serve

# Télécharger un modèle
ollama pull llama3.2
```

### 4. Lancer Clippy
```bash
python main.py
```

## 🎮 Guide d'Utilisation

### Interface de Base
```
┌─────────────────────┐
│ 🤖 Assistant IA  🔊│ ← Barre de titre
├─────────────────────┤
│        😊           │ ← Clippy animé (cliquable)
├─────────────────────┤
│ 📱 Chrome           │
│ 🕒 Navigation web   │ ← Info contextuelle
│                     │
│ 💡 Essaie Ctrl+T   │ ← Suggestion IA
│ pour nouvel onglet  │
└─────────────────────┘
```

### Contrôles
- **🖱️ Clic sur Clippy** → Nouveau conseil
- **💬 Chat** → Discussion avec l'IA
- **🎤 Microphone** → Mode vocal (si disponible)
- **🔊/🔇** → Synthèse vocale on/off
- **🔄** → Actualiser
- **⚙️** → Paramètres

### Commandes Chat/Vocales

#### 📁 Gestion de Fichiers
```
"Crée un script Python qui affiche bonjour"
"Génère un PDF sur l'intelligence artificielle"
"Lance le fichier test"
"Modifie index.html pour ajouter un menu"
"Liste les fichiers du dossier python"
```

#### 💬 Conversation
```
"Comment ça va ?"
"Explique-moi les fonctions Python"
"Donne-moi un conseil productivité"
```

#### 🎤 Commandes Vocales Spéciales
```
"Stop" → Arrête l'écoute
"Nouveau conseil" → Force une suggestion
"Ferme assistant" → Arrêt
```

## ⚙️ Configuration

### Variables d'Environnement
Créez un fichier `.env` (optionnel) :
```env
# Ollama
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT=30

# Interface
UI_WINDOW_WIDTH=300
UI_WINDOW_HEIGHT=400
DEBUG=false

# Fonctionnalités
ENABLE_WEB_RESEARCH=false
```

### Modèles IA Recommandés
| Usage | Modèle | Taille | Performance |
|-------|--------|--------|-------------|
| **Général** | `llama3.2` | ~2GB | Rapide |
| **Français** | `llama3.2` | ~2GB | Bon français |
| **Code** | `codellama` | ~4GB | Spécialisé |
| **Léger** | `llama3.2:1b` | ~1GB | Très rapide |

## 🔧 Résolution de Problèmes

### Problèmes Courants

#### "Ollama non connecté"
```bash
# Vérifier Ollama
ollama serve

# Tester
curl http://localhost:11434/api/tags

# Télécharger un modèle
ollama pull llama3.2
```

#### "Microphone non disponible"
```bash
# Windows
pip install pyaudio

# Linux
sudo apt install python3-pyaudio portaudio19-dev

# macOS
brew install portaudio
```

#### "Module X non trouvé"
```bash
# Réinstaller les dépendances
pip install -r requirements.txt

# Ou installation minimale
pip install psutil requests
```

#### Fenêtre invisible
- Vérifier la barre des tâches
- Alt+Tab pour voir toutes les fenêtres
- Redémarrer l'assistant

### Mode Debug
```bash
# Activer les logs détaillés
DEBUG=true python main.py
```

## 📋 Fonctionnalités par Dépendance

### Installation Minimale (`psutil requests`)
- ✅ Surveillance des applications
- ✅ Suggestions IA contextuelles
- ✅ Chat intelligent
- ✅ Interface graphique
- ❌ Synthèse vocale
- ❌ Reconnaissance vocale
- ❌ Génération PDF

### Installation Complète (toutes dépendances)
- ✅ Toutes les fonctionnalités ci-dessus
- ✅ Synthèse vocale française
- ✅ Reconnaissance vocale
- ✅ Génération PDF/documents
- ✅ Clippy animé avec images

## 🏗️ Structure du Projet

```
clippy-ai/
├── src/
│   ├── core/
│   │   ├── ollama_client.py        # Client IA
│   │   ├── system_monitor.py       # Surveillance
│   │   └── file_manager.py         # Gestion fichiers
│   ├── ui/
│   │   ├── main_window.py          # Interface principale
│   │   ├── character.py            # Personnage Clippy
│   │   ├── speech_bubble.py        # Bulles dialogue
│   │   └── chat_widget.py          # Widget chat
│   ├── utils/
│   │   ├── voice_engine.py         # Synthèse vocale
│   │   ├── speech_recognition_engine.py # Reconnaissance
│   │   ├── app_mapper.py           # Mapping applications
│   │   └── logger.py               # Logs
│   └── config/
│       └── settings.py             # Configuration
├── main.py                         # Point d'entrée
├── requirements.txt                # Dépendances
└── README.md                       # Documentation
```

## 🎯 Utilisation Avancée

### Personnalisation des Suggestions
L'IA s'adapte automatiquement selon l'application :

#### 🌐 Navigateurs (Chrome, Firefox, Edge)
```
💡 "Essaie Ctrl+Shift+T pour rouvrir un onglet fermé"
💡 "Utilise Ctrl+L pour aller à la barre d'adresse"
💡 "F12 pour ouvrir les outils de développeur"
```

#### 💻 Développement (VS Code, IDEs)
```
💡 "Ctrl+Shift+P pour la palette de commandes"
💡 "Ctrl+` pour ouvrir le terminal intégré"
💡 "F5 pour déboguer ton code"
```

#### 📝 Bureautique (Word, Excel)
```
💡 "Ctrl+S pour sauvegarder régulièrement"
💡 "F7 pour vérifier l'orthographe"
💡 "Ctrl+Z pour annuler la dernière action"
```

### Génération de Fichiers

#### Scripts Python
```
Chat: "Crée un script qui lit un CSV"
→ Génère automatiquement un script Python complet

Chat: "Modifie le script pour ajouter des graphiques"
→ Met à jour le code existant
```

#### Pages Web
```
Chat: "Crée une page HTML avec menu de navigation"
→ Génère HTML/CSS complet

Chat: "Ajoute un formulaire de contact"
→ Enrichit la page existante
```

#### Rapports PDF
```
Chat: "Génère un PDF sur la cybersécurité"
→ Recherche + rédaction + PDF stylé

Chat: "Crée un rapport sur Python"
→ Guide complet avec exemples
```

## 🔐 Sécurité et Vie Privée

### Données Locales
- ✅ **Tout fonctionne en local** - aucune donnée envoyée à des serveurs externes
- ✅ **Ollama local** - l'IA tourne sur votre machine
- ✅ **Fichiers locaux** - création dans vos dossiers
- ✅ **Pas de télémétrie** - aucun tracking

### Permissions Requises
- **Lecture processus** - pour détecter l'application active
- **Création fichiers** - dans le dossier Documents/AI_Assistant_Files
- **Microphone** - seulement si reconnaissance vocale activée
- **Réseau local** - communication avec Ollama (localhost:11434)

## 🚀 Performance et Optimisation

### Ressources Système
- **RAM** : ~50-100MB pour l'interface
- **CPU** : Minimal (surveillance passive)
- **Réseau** : Aucun (sauf Ollama local)
- **Stockage** : ~10MB + modèles Ollama

### Optimisations
- **Surveillance efficace** - vérification toutes les 5 secondes
- **Thread séparés** - UI responsive
- **Cache intelligent** - évite les requêtes répétitives
- **Gestion mémoire** - nettoyage automatique

## 🤝 Contribution et Développement

### Ajouter de Nouvelles Applications
```python
# Dans src/utils/app_mapper.py
self.app_names.update({
    'mon_app.exe': 'Mon Application',
    'autre_app.exe': 'Autre App'
})
```

### Nouveaux Types de Fichiers
```python
# Dans src/core/file_manager.py
def _generate_basic_code(self, instruction: str, file_type: str) -> str:
    if file_type.lower() == "mon_type":
        return "# Template pour mon type"
```

### Personnaliser les Suggestions IA
```python
# Dans src/core/ollama_client.py
def _create_contextual_prompt(self, app_name: str, context: str, category: str) -> str:
    if app_name == "MonApp":
        return "Prompt spécialisé pour MonApp..."
```

## 📈 Roadmap et Améliorations

### Version 1.1 (Prochaine)
- [ ] Interface sombre/claire
- [ ] Raccourcis clavier globaux
- [ ] Historique des suggestions
- [ ] Notifications système

### Version 1.2 (Future)
- [ ] Plugins tiers
- [ ] API REST locale
- [ ] Support multi-langues
- [ ] Thèmes personnalisés

### Contributions Bienvenues
- 🐛 **Bug reports** - Issues GitHub
- 💡 **Suggestions** - Discussions
- 🔧 **Pull Requests** - Améliorations
- 📖 **Documentation** - Guides d'usage

## 📞 Support et Communauté

### Obtenir de l'Aide
1. **README** - Documentation complète
2. **Issues GitHub** - Problèmes techniques
3. **Discussions** - Questions générales

### Signaler un Bug
Incluez dans votre rapport :
- OS et version Python
- Logs d'erreur complets
- Étapes pour reproduire
- Configuration Ollama

### Proposer une Fonctionnalité
- Décrivez l'usage prévu
- Justifiez la valeur ajoutée
- Proposez une implémentation

## 📄 Licence et Crédits

### Licence MIT
Ce projet est sous licence MIT - voir [LICENSE](LICENSE) pour détails.

### Remerciements
- **Microsoft Clippy** - Inspiration originale 📎
- **Ollama** - IA locale accessible
- **Communauté Python** - Écosystème fantastique
- **Contributeurs** - Améliorations continues

### Versions
- **v1.0** - Version stable avec fonctionnalités essentielles
- **v0.9** - Version bêta avec toutes les fonctionnalités
- **v0.5** - Prototype initial

---

**📎 Développé avec ❤️ pour la productivité moderne**

*Assistant IA local, privé et personnalisable pour tous*