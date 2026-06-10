# 🦖 Jurassic DNA Fusion (JDF)

Un mod Minecraft (NeoForge 1.21.1) où l'on recrée des dinosaures à partir
d'ADN fossile, où l'on fabrique des hybrides… et où l'on peut **s'injecter
l'ADN des créatures pour gagner leurs capacités**, voire se transformer.

## 🚀 Démarrer

Prérequis : Java 21+ (Java 25 installé ✔)

```powershell
# Lancer Minecraft avec le mod (depuis le dossier jdf-mod)
.\gradlew.bat runClient

# Compiler le .jar distribuable (build\libs\jdf-1.0.0.jar)
.\gradlew.bat build
```

Astuce IDE : ouvre le dossier `jdf-mod` dans IntelliJ IDEA (Community suffit),
il importera le projet Gradle tout seul et tu auras les configurations
`runClient` / `runServer` prêtes à l'emploi.

## 🎮 Contenu actuel (v1.0.0 — prototype "gene-splicing")

| Item | Utilisation |
|---|---|
| 💉 **Seringue** | Clic droit sur une créature → extrait son ADN. Maintenir clic droit ensuite → tu t'injectes l'ADN ! |
| 🟠 **Ambre** | Décoratif pour l'instant — contiendra des moustiques préhistoriques. |
| 🦴 **Bloc de fossile** | Décoratif pour l'instant — génèrera sous terre plus tard. |

### Table ADN → capacités (60 s)

| ADN de… | Capacité obtenue |
|---|---|
| Poulet | Chute lente |
| Lapin | Super saut II |
| Chèvre | Super saut III |
| Cheval | Vitesse II |
| Chat / Ocelot | Vision nocturne |
| Tortue / Axolotl | Respiration aquatique |
| Dauphin | Grâce du dauphin |
| Golem de fer | Force + Résistance |
| Autre créature | ADN incompatible → nausée 🤢 |

Le code de cette table est dans
`src/main/java/com/yahya/jdf/item/SyringeItem.java` (méthode `applyDnaEffects`)
— c'est le meilleur endroit pour expérimenter !

## 🗺️ Roadmap

### Phase 1 — Boucle ADN (en cours)
- [x] Seringue : extraction + injection d'ADN
- [x] Effets selon la créature source
- [ ] Recette de craft de la seringue (survie)
- [ ] Qualité/pureté de l'ADN (échantillons dégradés)

### Phase 2 — Archéologie
- [ ] Génération des blocs de fossile sous terre (par biome/profondeur)
- [ ] Ambre minable avec moustiques → ADN de dino aléatoire
- [ ] Table de nettoyage de fossiles → fragments d'ADN d'espèces précises

### Phase 3 — Les dinosaures 🦕
- [ ] GeckoLib pour les modèles/animations
- [ ] Séquenceur d'ADN (machine + GUI) : fragments → génome complet
- [ ] Incubateur → œufs → bébés dinos qui grandissent
- [ ] Premiers dinos : Velociraptor, Tricératops, T-Rex, Dilophosaure
- [ ] Apprivoisement / enclos / comportements (meutes de raptors !)

### Phase 4 — Hybridation
- [ ] Mélange de deux génomes → hybrides (stats/textures mélangées)
- [ ] Instabilité génétique : plus l'hybride est puissant, plus il est imprévisible

### Phase 5 — Fusion joueur ⭐ (l'idée phare)
- [ ] Niveaux d'imprégnation : injections répétées = capacités permanentes
- [ ] Capacités actives (rugissement du T-Rex, charge du tricé, morsure…)
- [ ] Transformations visibles (griffes, queue, peau écailleuse… modèle joueur custom)
- [ ] Coût : instabilité génétique, faim accrue, "rejet" si on mélange trop d'ADN
- [ ] Sérum de purge pour redevenir 100 % humain

## 🧩 Architecture du code

```
src/main/java/com/yahya/jdf/
├── JurassicDnaFusion.java      # Point d'entrée du mod
├── JdfClient.java              # Point d'entrée client (rendu)
├── item/
│   └── SyringeItem.java        # La seringue (extraction + injection)
└── registry/
    ├── ModItems.java           # Enregistrement des items
    ├── ModBlocks.java          # Enregistrement des blocs
    ├── ModCreativeTabs.java    # Onglet créatif
    └── ModDataComponents.java  # Données attachées aux items (ADN stocké)
```

Les ressources (textures, modèles, traductions FR/EN, loot tables) sont dans
`src/main/resources/`. Les textures sont générées par `tools/make_textures.ps1`
(pixel art en texte → PNG), pratique en attendant de vraies textures.

## 📚 Ressources utiles

- Documentation NeoForge : https://docs.neoforged.net/
- Discord NeoForged : https://discord.neoforged.net/
- GeckoLib (animations) : https://github.com/bernie-g/geckolib
