# 📖 Guide d'utilisation

Guide complet pour utiliser efficacement votre Assistant IA Local.

## 🚀 Premier démarrage

### Lancement de l'assistant

1. **Ouvrir un terminal** dans le dossier du projet
2. **Activer l'environnement virtuel** :
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```
3. **Démarrer Ollama** (dans un terminal séparé) :
   ```bash
   ollama serve
   ```
4. **Lancer l'assistant** :
   ```bash
   python main.py
   ```

### Première utilisation

Au premier lancement, vous devriez voir :

```
🚀 Démarrage de l'Assistant IA...
✅ Ollama connecté !
🤖 Assistant IA démarré !
- Fenêtre flottante: 200x250
- IA: ✅
🔍 Surveillance système démarrée
```

Une petite fenêtre apparaît avec :
- 🤖 **Un personnage animé** (cercle vert avec sourire)
- 📝 **Une zone de texte** pour les suggestions
- 🎛️ **Des boutons de contrôle** en haut

## 🎮 Interface utilisateur

### Vue d'ensemble

```
┌─────────────────────────────────┐
│ 🤖 Assistant IA  🔊 🔄 ⚙️ _ ✕ │ ← Barre de titre
├─────────────────────────────────┤
│                                 │
│           😊                    │ ← Personnage animé
│      (cliquable)                │
│                                 │
├─────────────────────────────────┤
│ 📱 Chrome                       │
│ 🕒 Navigation web (14:30)       │ ← Zone d'information
│                                 │
│ 💡 Essaie Ctrl+Shift+T pour    │ ← Suggestion IA
│ rouvrir un onglet fermé !       │
│                                 │
└─────────────────────────────────┘
```

### Boutons de contrôle

| Bouton | Fonction | Description |
|--------|----------|-------------|
| 🔊/🔇 | Voice | Active/désactive la synthèse vocale |
| 🔄 | Refresh | Demande une nouvelle suggestion |
| ⚙️ | Settings | Affiche les informations système |
| _ | Minimize | Cache temporairement (3 secondes) |
| ✕ | Close | Ferme l'assistant |

## 💡 Obtenir des suggestions

### Méthodes pour déclencher l'IA

#### 1. 🖱️ Clic sur le personnage
- **Action** : Cliquer sur le cercle vert
- **Résultat** : Nouvelle suggestion immédiate
- **Avantage** : Plus intuitif et amusant

#### 2. 🔄 Bouton Actualiser
- **Action** : Cliquer sur le bouton bleu 🔄
- **Résultat** : Même effet que le clic personnage
- **Avantage** : Bouton visible

#### 3. 📱 Changement d'application
- **Action** : Ouvrir une autre application (Chrome, Word, etc.)
- **Résultat** : Suggestion automatique après 5-10 secondes
- **Avantage** : Contextuel et automatique

### Types de suggestions

L'assistant adapte ses conseils selon votre contexte :

#### 🌐 Navigateurs Web (Chrome, Firefox, Opera)
```
💡 Essaie Ctrl+Shift+T pour rouvrir un onglet fermé !
💡 Utilise Ctrl+L pour aller directement à la barre d'adresse
💡 Ctrl+Shift+N pour ouvrir une fenêtre de navigation privée
```

#### 💻 Développement (VS Code, IDEs)
```
💡 N'oublie pas Ctrl+Shift+P pour la palette de commandes !
💡 Utilise Ctrl+` pour ouvrir/fermer le terminal intégré
💡 F12 pour déboguer ton code pas à pas
```

#### 📝 Bureautique (Word, Excel)
```
💡 Ctrl+S pour sauvegarder régulièrement ton travail !
💡 F7 pour vérifier l'orthographe de ton document
💡 Utilise les styles pour une mise en forme cohérente
```

#### ⌨️ Terminal (PowerShell, CMD)
```
💡 Tape 'cls' pour nettoyer l'écran
💡 Utilise Tab pour l'autocomplétion
💡 Flèche haut pour rappeler la dernière commande
```

## 🔊 Synthèse vocale

### Activation/Désactivation

- **Bouton** : 🔊 (activé) / 🔇 (désactivé)
- **Par défaut** : Activé si disponible
- **Confirmation** : L'assistant dit "Synthèse vocale activée !" au démarrage

### Fonctionnement

1. **Déclenchement** : À chaque nouvelle suggestion
2. **Contenu** : Seule la partie conseil (après 💡) est lue
3. **Nettoyage** : Émojis et formatage automatiquement supprimés
4. **Queue** : Les messages s'accumulent si plusieurs suggestions rapides

### Personnalisation de la voix

La voix est automatiquement configurée :
- **Vitesse** : 180 mots/minute (optimale)
- **Volume** : 80% (audible mais pas envahissant)
- **Langue** : Français si disponible sur le système

## 🎭 États du personnage

Le personnage change d'expression selon l'activité :

| Humeur | Apparence | Quand |
|--------|-----------|-------|
| **Neutral** 😐 | Sourire léger, bleu | État par défaut |
| **Thinking** 🤔 | Yeux plissés, orange | Génération IA en cours |
| **Happy** 😊 | Grand sourire, vert | Suggestion générée |
| **Working** 🔧 | Concentré, bleu foncé | Système occupé |

### Animations

- **Bounce** : Rebond quand content
- **Sway** : Balancement en réflexion  
- **Pulse** : Pulsation pendant le travail

## 📊 Surveillance d'activité

### Applications détectées

L'assistant reconnaît automatiquement :

#### 🌐 Navigateurs
- Chrome, Firefox, Edge, Opera, Brave, Safari

#### 💻 Développement
- VS Code, PyCharm, IntelliJ, Visual Studio, Sublime Text

#### 📝 Bureautique
- Word, Excel, PowerPoint, Outlook, OneNote

#### ⌨️ Système
- PowerShell, CMD, Explorateur Windows

#### 💬 Communication
- Discord, Teams, Slack, Zoom, Skype

#### 🎵 Multimédia
- Spotify, VLC, Photoshop, GIMP

### Fréquence de détection

- **Intervalle** : Vérification toutes les 5 secondes
- **Déclenchement** : Seulement si changement d'application
- **Optimisation** : Pas de ralentissement système

## ⚙️ Configuration

### Paramètres système

Cliquer sur ⚙️ affiche :
```
Assistant IA v1.0

Modèle: llama3.2
Statut IA: ✅ Connecté
Intervalle: 5s
```

### Personnalisation avancée

Pour modifier les paramètres, éditer `.env` :

```env
# Modèle IA
OLLAMA_MODEL=llama3.2        # ou mistral, codellama
OLLAMA_TIMEOUT=15            # Timeout en secondes

# Interface
UI_WINDOW_WIDTH=250          # Largeur fenêtre
UI_WINDOW_HEIGHT=300         # Hauteur fenêtre

# Surveillance
MONITOR_INTERVAL=3           # Fréquence (secondes)
DEBUG=true                   # Mode debug
```

## 🔧 Résolution de problèmes

### Problèmes courants

#### "Ollama non connecté"

**Symptôme** : Message d'erreur dans la bulle
```
🔌 Ollama non connecté (Connexion refusée)
```

**Solutions** :
1. Vérifier qu'Ollama tourne : `ollama serve`
2. Tester manuellement : `ollama run llama3.2 "test"`
3. Redémarrer Ollama
4. Vérifier le port 11434

#### Pas de suggestions

**Symptôme** : Le personnage ne réagit pas aux changements d'apps

**Solutions** :
1. Cliquer sur le personnage pour forcer une suggestion
2. Vérifier que l'application est dans la liste supportée
3. Attendre 5-10 secondes après changement d'app
4. Redémarrer l'assistant

#### Synthèse vocale ne fonctionne pas

**Symptôme** : Bouton 🔇 grisé, pas de son

**Solutions** :
```bash
# Réinstaller pyttsx3
pip uninstall pyttsx3
pip install pyttsx3

# Tester manuellement
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"
```

#### Fenêtre disparue

**Symptôme** : Assistant lancé mais fenêtre invisible

**Solutions** :
1. Vérifier la barre des tâches
2. Alt+Tab pour voir toutes les fenêtres
3. Redémarrer l'assistant
4. Vérifier position d'écran (multi-moniteurs)

### Mode debug

Activer pour diagnostiquer :

```bash
# Dans .env
DEBUG=true

# Ou en lançant
python main.py
```

Vous verrez alors :
```
[DEBUG] Analyse des processus en cours...
[DEBUG] App intéressante: chrome.exe (score: 150.2)
[DEBUG OLLAMA] Génération pour Chrome - Navigation web
[DEBUG UI] Mise à jour bulle avec: ...
```

## 💡 Conseils d'utilisation

### Optimiser les suggestions

1. **Gardez des apps ouvertes** : Plus d'applications = plus de contexte
2. **Variez vos activités** : L'IA apprend de la diversité
3. **Cliquez régulièrement** : Obtenez des conseils frais
4. **Utilisez la voix** : Plus immersif et pratique

### Workflow recommandé

1. **Matin** : Lancer l'assistant avec le PC
2. **Travail** : Laisser tourner en arrière-plan
3. **Changement d'activité** : Observer les nouvelles suggestions
4. **Pause** : Cliquer pour des conseils généraux
5. **Soir** : Fermer proprement avec ✕

### Bonnes pratiques

- **Position** : Placer dans un coin non gênant
- **Volume** : Ajuster selon l'environnement
- **Fréquence** : Ne pas abuser du clic (laiss