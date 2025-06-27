# 📦 Guide d'installation détaillé

Ce guide vous accompagne pas à pas pour installer et configurer l'Assistant IA Local.

## 🎯 Prérequis système

### Système d'exploitation
- ✅ **Windows 10/11** (recommandé)
- ⚠️ **Linux** (support expérimental)
- ⚠️ **macOS** (support expérimental)

### Logiciels requis
- **Python 3.8+** ([Télécharger](https://python.org))
- **Ollama** ([Télécharger](https://ollama.ai))
- **Git** (optionnel, pour cloner le repo)

### Ressources système
- **RAM** : 4GB minimum, 8GB recommandé
- **CPU** : Processeur moderne (Intel i5/AMD Ryzen 5+)
- **Espace disque** : 2GB pour Ollama + modèles

## 🚀 Installation étape par étape

### Étape 1 : Préparer l'environnement

#### 1.1 Vérifier Python

```bash
# Vérifier la version Python
python --version
# Doit afficher Python 3.8.x ou plus récent

# Si Python n'est pas installé :
# Windows : https://python.org/downloads/
# Linux : sudo apt install python3 python3-pip
# macOS : brew install python3
```

#### 1.2 Installer Ollama

**Windows :**
1. Télécharger depuis [ollama.ai](https://ollama.ai)
2. Exécuter l'installateur `.exe`
3. Redémarrer le terminal

**Linux/macOS :**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 1.3 Tester Ollama

```bash
# Démarrer Ollama
ollama serve

# Dans un autre terminal, tester
ollama --version
```

### Étape 2 : Obtenir le code

#### Option A : Téléchargement direct
1. [Télécharger le ZIP](https://github.com/votre-repo/ai-assistant/archive/main.zip)
2. Extraire dans un dossier de votre choix
3. Ouvrir un terminal dans ce dossier

#### Option B : Git clone
```bash
git clone https://github.com/votre-repo/ai-assistant.git
cd ai-assistant
```

### Étape 3 : Environnement virtuel

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate
# Linux/macOS :
source venv/bin/activate

# Vérifier l'activation (le prompt doit changer)
# Vous devriez voir (venv) au début de votre ligne de commande
```

### Étape 4 : Installer les dépendances

```bash
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

#### Dépendances installées :
- `psutil` - Surveillance système
- `requests` - Communication HTTP
- `pyttsx3` - Synthèse vocale
- `pywin32` - APIs Windows (Windows uniquement)

### Étape 5 : Configurer Ollama

```bash
# Démarrer Ollama (dans un terminal séparé)
ollama serve

# Télécharger un modèle IA
ollama pull llama3.2

# Modèles alternatifs (optionnel) :
# ollama pull llama3.2:1b    # Plus léger, plus rapide
# ollama pull mistral        # Alternative à Llama
# ollama pull codellama      # Spécialisé code
```

#### Vérification Ollama :
```bash
# Lister les modèles installés
ollama list

# Tester un modèle
ollama run llama3.2 "Dis bonjour"
```

### Étape 6 : Premier lancement

```bash
# Dans le dossier ai-assistant, avec venv activé
python main.py
```

#### Ce que vous devriez voir :
```
🚀 Démarrage de l'Assistant IA...
✅ Ollama connecté !
🤖 Assistant IA démarré !
- Fenêtre flottante: 200x250
- IA: ✅
🔍 Surveillance système démarrée
```

## ⚙️ Configuration avancée

### Fichier de configuration

Créez un fichier `.env` dans le dossier racine :

```env
# Configuration Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT=15

# Interface utilisateur
UI_WINDOW_WIDTH=200
UI_WINDOW_HEIGHT=250
UI_ALWAYS_ON_TOP=true

# Surveillance
MONITOR_INTERVAL=5
DEBUG=false

# Synthèse vocale
VOICE_RATE=180
VOICE_VOLUME=0.8
```

### Personnalisation des modèles

#### Modèles recommandés par usage :

| Usage | Modèle | Taille | Vitesse |
|-------|--------|--------|---------|
| **Usage général** | `llama3.2` | ~4GB | Normale |
| **Réactivité max** | `llama3.2:1b` | ~1GB | Rapide |
| **Code/Dev** | `codellama` | ~7GB | Normale |
| **Français** | `mistral` | ~4GB | Rapide |

#### Changer de modèle :

```bash
# Télécharger un nouveau modèle
ollama pull llama3.2:1b

# Modifier dans .env
OLLAMA_MODEL=llama3.2:1b

# Ou directement dans settings.py
```

## 🔧 Résolution des problèmes d'installation

### Problème : "Python n'est pas reconnu"

**Solution :**
1. Réinstaller Python avec "Add to PATH" coché
2. Ou ajouter manuellement Python au PATH
3. Redémarrer le terminal

### Problème : "pip install échoue"

**Solutions :**
```bash
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer avec --user si permissions
pip install --user -r requirements.txt

# Force reinstall
pip install --force-reinstall -r requirements.txt
```

### Problème : "Ollama non connecté"

**Solutions :**
1. Vérifier qu'Ollama tourne : `ollama serve`
2. Tester manuellement : `curl http://localhost:11434`
3. Redémarrer Ollama
4. Vérifier le firewall

### Problème : "pyttsx3 ne fonctionne pas"

**Windows :**
```bash
# Installer les composants vocaux Windows
pip install pywin32
python -m win32api
```

**Linux :**
```bash
# Installer espeak
sudo apt install espeak espeak-data libespeak-dev
```

### Problème : "Fenêtre n'apparaît pas"

**Solutions :**
1. Vérifier l'écran (fenêtre peut être hors zone visible)
2. Redimensionner/repositionner dans le code
3. Vérifier les permissions d'affichage

## 📋 Vérification de l'installation

### Checklist complète

- [ ] Python 3.8+ installé et dans le PATH
- [ ] Ollama installé et démarré (`ollama serve`)
- [ ] Modèle IA téléchargé (`ollama list`)
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`pip list`)
- [ ] Assistant démarre sans erreur
- [ ] Interface s'affiche
- [ ] Suggestions IA fonctionnent
- [ ] Synthèse vocale marche (optionnel)

### Test complet

```bash
# Script de test automatique
python -c "
import psutil
import requests
import pyttsx3
print('✅ Toutes les dépendances importées')

# Test Ollama
try:
    r = requests.get('http://localhost:11434/api/tags', timeout=3)
    print('✅ Ollama accessible')
except:
    print('❌ Ollama non accessible')
"
```

## 🚀 Démarrage automatique (optionnel)

### Windows - Tâche planifiée

1. Ouvrir "Planificateur de tâches"
2. Créer une tâche de base
3. Déclencheur : À l'ouverture de session
4. Action : Démarrer `C:\chemin\vers\venv\Scripts\python.exe C:\chemin\vers\main.py`

### Linux - Service systemd

```bash
# Créer le service
sudo nano /etc/systemd/system/ai-assistant.service

[Unit]
Description=AI Assistant
After=network.target

[Service]
Type=simple
User=votre-user
WorkingDirectory=/chemin/vers/ai-assistant
ExecStart=/chemin/vers/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target

# Activer le service
sudo systemctl enable ai-assistant
sudo systemctl start ai-assistant
```

## 📞 Support installation

Si vous rencontrez des problèmes :

1. **Vérifiez** cette documentation
2. **Consultez** les [Issues GitHub](https://github.com/votre-repo/issues)
3. **Créez** une nouvelle issue avec :
   - Votre OS et version
   - Version Python
   - Message d'erreur complet
   - Étapes reproduisant le problème

---

**Installation réussie ?** Passez au [Guide d'utilisation](usage.md) ! 🎉