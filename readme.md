# 📎 Assistant Clippy IA Moderne - Version Fusionnée

Un assistant IA local moderne inspiré de Clippy avec toutes les fonctionnalités avancées intégrées.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## ✨ Fonctionnalités Complètes

### 🤖 Intelligence Artificielle
- **Assistant IA contextuel** avec suggestions selon l'application active
- **Chat intelligent** pour conversations naturelles
- **Gestion de fichiers IA** - création, modification, exécution
- **Génération de code** dans plusieurs langages

### 📁 Gestionnaire de Fichiers Avancé
- **Création automatique** de scripts, documents, PDFs
- **Résumé de documents** (PDF, Word, TXT)
- **Recherche web → PDF** avec résumés structurés
- **Génération de lettres** et documents professionnels
- **Traduction et correction** de textes

### 🎤 Interface Vocale
- **Reconnaissance vocale** continue en français
- **Synthèse vocale** avec voix française
- **Commandes vocales** pour contrôler l'assistant
- **Mode mains libres** complet

### 👁️ Surveillance Intelligente
- **Détection automatique** des applications actives
- **Suggestions contextuelles** selon votre travail
- **Statistiques d'utilisation** des applications
- **Monitoring non-intrusif** en arrière-plan

### 🔧 Mode Avancé
- **Panel d'outils** avec accès rapide aux fonctions
- **Historique des commandes** avec sauvegarde
- **Informations système** en temps réel
- **Système de rappels** programmables

### 🎭 Personnage Clippy Animé
- **Animations fluides** avec frames multiples
- **Expressions contextuelles** selon l'humeur
- **Interactions visuelles** au clic
- **Style moderne** avec nostalgie rétro

## 📸 Interface

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

## 🚀 Installation Rapide

### Prérequis
- **Python 3.8+**
- **Ollama** installé et configuré
- **Windows/Linux/macOS**

### 1. Cloner et installer
```bash
git clone https://github.com/votre-repo/clippy-ai-moderne.git
cd clippy-ai-moderne

# Environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Dépendances complètes
pip install -r requirements.txt
```

### 2. Configurer Ollama
```bash
# Démarrer Ollama
ollama serve

# Télécharger les modèles (dans un autre terminal)
ollama pull adrienbrault/nous-hermes2pro:Q3_K_M
ollama pull deepseek-coder-v2:16b  # Optionnel pour créativité
```

### 3. Lancer Clippy
```bash
python main.py
```

## 🎮 Guide d'Utilisation

### Contrôles de Base
- **🖱️ Clic sur Clippy** → Nouveau conseil intelligent
- **💬 Bouton Chat** → Discussion avec l'IA
- **🎤 Microphone** → Mode vocal (reconnaissance continue)
- **🔧 Mode Avancé** → Outils et fonctionnalités étendues
- **🔊/🔇 Volume** → Synthèse vocale on/off

### Commandes Texte/Vocales

#### 📁 Gestion de Fichiers
```
"Crée un script Python qui calcule les nombres premiers"
"Génère une lettre de motivation pour développeur"
"Résume le document rapport.pdf"
"Lance le fichier test"
"Traduis ce texte : Hello world"
```

#### 🌐 Recherche Web
```
"Cherche des infos sur l'intelligence artificielle et fais un PDF"
"Explique-moi la blockchain avec sources web"
"Recherche les dernières news sur Python"
```

#### ⏰ Rappels et Organisation
```
"Rappelle-moi d'appeler le client demain à 14h"
"Affiche l'historique des commandes"
"Liste les fichiers du dossier python"
```

#### 🎤 Commandes Vocales Spéciales
```
"Stop" → Arrête l'écoute
"Nouveau conseil" → Force une suggestion
"Mode avancé" → Bascule le panel
"Ferme Clippy" → Arrêt de l'assistant
```

### Fonctionnalités Avancées

#### 🔧 Panel d'Outils
- **📄 Résumer PDF** : Analyse et résume vos documents
- **🌐 Web → PDF** : Recherche + création de rapport
- **📝 Générer Doc** : Lettres, contrats, factures
- **🗂️ Lister Fichiers** : Exploration des dossiers
- **🔤 Traduire** : Traduction instantanée
- **📋 Historique** : Dernières commandes

#### 📊 Surveillance Contextuelle
Clippy détecte automatiquement :
- **Applications actives** (Chrome, VS Code, Word...)
- **Contexte d'utilisation** (développement, navigation, bureautique)
- **Suggestions personnalisées** selon l'activité

### Exemples d'Usage

#### 🧑‍💻 Développeur
```
App détectée: VS Code
💡 "Utilise Ctrl+` pour le terminal intégré"

Commande vocale: "Crée un serveur web Flask basique"
→ Génère automatiquement le code Python
```

#### 📝 Bureautique
```
App détectée: Word
💡 "F7 pour vérifier l'orthographe"

Chat: "Génère une facture pour consulting informatique"
→ Crée un document ODT professionnel
```

#### 🔍 Recherche & Documentation
```
Commande: "Explique-moi React et crée un PDF complet"
→ Recherche sur le web + résumé structuré + PDF stylé

Vocal: "Résume le rapport financier point PDF"
→ Analyse automatique du document
```

## ⚙️ Configuration Avancée

### Variables d'Environnement
Créez un fichier `.env` :
```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=adrienbrault/nous-hermes2pro:Q3_K_M
OLLAMA_TIMEOUT=30

# Interface
UI_WINDOW_WIDTH=350
UI_WINDOW_HEIGHT=450
DEBUG=false

# Monitoring
MONITOR_INTERVAL=5

# Fonctionnalités avancées
ENABLE_WEB_SCRAPING=true
ENABLE_DOCUMENT_GENERATION=true
ENABLE_VOICE_RECOGNITION=true
```

### Personnalisation du Dossier de Travail
```python
# Dans enhanced_file_manager.py
DOSSIER_BASE = r"C:\MonDossier\ClippyFiles"
```

### Modèles IA Recommandés
| Usage | Modèle | Taille | Performance |
|-------|--------|--------|-------------|
| **Général** | `adrienbrault/nous-hermes2pro:Q3_K_M` | ~4GB | Équilibré |
| **Code** | `deepseek-coder-v2:16b` | ~8GB | Spécialisé |
| **Léger** | `llama3.2:3b` | ~2GB | Rapide |
| **Français** | `vigostral-7b-chat` | ~4GB | Optimisé FR |

## 🎨 Personnalisation Clippy

### Images d'Animation
Placez dans le dossier de base :
- `clippy.jpg` - Image principale
- `frame1.png`, `frame2.png`, `frame3.png` - Frames d'animation
- `background.png` - Arrière-plan (optionnel)

### Humeurs du Personnage
```python
# Dans character.py - Nouvelles humeurs
"excited": {
    "eye_shape": "sparkle",
    "mouth_shape": "big_smile", 
    "body_color": "#FFD700",
    "animation": "bounce"
}
```

## 🔧 Résolution de Problèmes

### Problèmes Courants

#### "Ollama non connecté"
```bash
# Démarrer Ollama
ollama serve

# Tester la connexion
curl http://localhost:11434/api/tags

# Vérifier les modèles
ollama list
```

#### "Microphone non disponible"
```bash
# Windows
pip install pyaudio

# Linux
sudo apt install portaudio19-dev python3-pyaudio

# macOS
brew install portaudio
```

#### "Fonctionnalités avancées limitées"
```bash
# Installer toutes les dépendances optionnelles
pip install fpdf2 PyMuPDF beautifulsoup4 duckduckgo-search
pip install odfpy schedule dateparser
```

#### "Images Clippy manquantes"
1. Téléchargez les images depuis le dossier `assets/`
2. Placez-les dans `Documents/AI_Assistant_Files/`
3. Redémarrez Clippy

### Mode Debug
```bash
# Lancer avec debug complet
DEBUG=true python main.py
```

### Logs Détaillés
```bash
# Voir les logs en temps réel
tail -f ai_assistant.log
```

## 📊 Statistiques et Monitoring

### Panel Informations Système
En mode avancé, Clippy affiche :
- **Utilisation CPU/RAM** en temps réel
- **Applications les plus utilisées** avec durée
- **Statut des services** (IA, microphone, etc.)
- **Espace disque** du dossier de travail

### Historique Intelligent
- **Sauvegarde automatique** de toutes les commandes
- **Recherche** dans l'historique
- **Statistiques d'usage** par fonctionnalité
- **Export** des données en JSON

## 🚀 Utilisation Avancée

### Automatisation avec Rappels
```python
# Programmation de tâches récurrentes
"Rappelle-moi de faire les sauvegardes tous les vendredis à 17h"
"Alerte-moi dans 2 heures pour la réunion"
```

### Intégration dans Workflows
```bash
# Utilisation en ligne de commande
python -c "from src.core.enhanced_file_manager import enhanced_file_manager; print(enhanced_file_manager.process_command('liste les fichiers python'))"
```

### API et Extensions
```python
# Ajouter de nouvelles commandes
def custom_action(instruction: str) -> str:
    # Votre logique personnalisée
    return "Action personnalisée exécutée"

# Intégrer dans le gestionnaire
enhanced_file_manager.custom_actions["ma_commande"] = custom_action
```

## 🤝 Contribution et Développement

### Structure du Code Fusionné
```
clippy-ai-moderne/
├── src/
│   ├── core/
│   │   ├── enhanced_file_manager.py    # 🆕 Gestionnaire unifié
│   │   ├── ollama_client.py            # Client IA
│   │   └── system_monitor.py           # Surveillance
│   ├── ui/
│   │   ├── enhanced_main_window.py     # 🆕 Interface complète
│   │   ├── character.py                # Personnage Clippy
│   │   ├── speech_bubble.py            # Bulles dialogue
│   │   └── chat_widget.py              # Widget chat
│   ├── utils/
│   │   ├── voice_engine.py             # Synthèse vocale
│   │   ├── speech_recognition_engine.py # Reconnaissance
│   │   └── app_mapper.py               # Mapping applications
│   └── config/
│       └── settings.py                 # Configuration
├── main.py                             # 🆕 Lanceur unifié
├── requirements.txt                    # 🆕 Dépendances complètes
└── README.md                           # 🆕 Documentation fusionnée
```

### Fonctionnalités Fusionnées
✅ **Interface moderne** avec Tkinter stylé  
✅ **Gestionnaire de fichiers** avec IA complète  
✅ **Web scraping** → PDF automatique  
✅ **Génération de documents** professionnels  
✅ **Reconnaissance/synthèse vocale** française  
✅ **Système de rappels** programmables  
✅ **Historique intelligent** avec sauvegarde  
✅ **Mode avancé** avec outils étendus  
✅ **Animation Clippy** avec frames multiples  
✅ **Surveillance contextuelle** des applications  

### Guidelines de Contribution
1. **Fork** le projet
2. **Créer** une branche feature
3. **Tester** avec toutes les dépendances
4. **Documenter** les nouvelles fonctionnalités
5. **Soumettre** une Pull Request

## 📄 Licence et Crédits

### Licence MIT
Ce projet est sous licence MIT - voir [LICENSE](LICENSE) pour détails.

### Remerciements
- **Microsoft Clippy** pour l'inspiration originale 📎
- **Ollama** pour l'IA locale accessible
- **Communauté Python** pour les excellentes bibliothèques
- **Tous les contributeurs** qui ont aidé à fusionner les fonctionnalités

### Versions
- **v1.0** - Assistant IA de base avec surveillance
- **v1.5** - Ajout chat et reconnaissance vocale  
- **v2.0** - 🆕 **Version fusionnée complète** avec toutes les fonctionnalités Clippy

---

**📎 Clippy IA Moderne - L'assistant qui vous accompagne vraiment !** 🚀

*Développé avec ❤️ pour la productivité moderne*