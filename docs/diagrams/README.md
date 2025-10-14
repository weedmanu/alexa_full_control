# 📊 Diagrammes du Système de Cache

Ce dossier contient les diagrammes PlantUML illustrant le fonctionnement du système de cache multi-niveaux d'Alexa Advanced Control.

## 📁 Fichiers disponibles

1. **`cache_flow_diagram.puml`** - Flux de cache détaillé avec les 3 scénarios
2. **`cache_architecture.puml`** - Architecture globale du système
3. **`cache_state_machine.puml`** - Machine à états du cache
4. **`cache_performance.puml`** - Comparaison des performances

## 🎨 Visualisation des Diagrammes

### Option 1 : Extension VS Code (Recommandé)

1. **Installer l'extension PlantUML** :

```vscode-extensions
jebbs.plantuml
```

2. **Ouvrir un fichier `.puml`** dans VS Code

3. **Prévisualiser** :
   - Appuyer sur **Alt+D** pour ouvrir la prévisualisation
   - Ou clic droit → **PlantUML: Preview Current Diagram**

### Option 2 : En ligne

1. Ouvrir https://www.plantuml.com/plantuml/
2. Copier le contenu d'un fichier `.puml`
3. Coller dans l'éditeur en ligne
4. Le diagramme s'affiche automatiquement

### Option 3 : Java PlantUML (Local)

```powershell
# Télécharger plantuml.jar
curl -O https://sourceforge.net/projects/plantuml/files/plantuml.jar

# Générer tous les diagrammes en PNG
java -jar plantuml.jar docs/diagrams/*.puml

# Ou un seul fichier
java -jar plantuml.jar docs/diagrams/cache_flow_diagram.puml
```

## 📖 Contenu des Diagrammes

### 1. Cache Flow Diagram

**Scénarios couverts :**

- ✅ **Scénario 1** : Cache mémoire valide (< 5 min) → ⚡ **1-2 ms**
- ⚠️ **Scénario 2** : Cache mémoire expiré → Lecture disque (sans TTL) → 💾 **10-50 ms**
- ❌ **Scénario 3** : Pas de cache → Appel API → 🌐 **200-1000 ms**

### 2. Architecture

Montre l'interaction entre :

- **CLI Commands** → Point d'entrée utilisateur
- **DeviceManager** → Gestion logique du cache
- **Cache Mémoire** → Niveau 1 (Volatile, TTL 5 min)
- **CacheService + Disque** → Niveau 2 (Persistent, sans TTL)
- **Amazon API** → Dernier recours

### 3. State Machine

États du cache :

- **Empty** : Premier démarrage, aucun cache
- **BothValid** : État optimal, mémoire + disque valides
- **DiskOnly** : Après expiration mémoire (> 5 min)

### 4. Performance Comparison

Diagramme d'activité montrant :

- Chemins de décision (cache valide ou non)
- Latence pour chaque niveau
- Probabilité d'occurrence

## 🔄 Génération Automatique

Pour régénérer tous les diagrammes :

```powershell
# Activer l'environnement virtuel
venv\Scripts\activate

# Exécuter le script de génération
python scripts/generate_cache_plantuml.py
```

## 📝 Intégration dans la Documentation

Les diagrammes sont référencés dans `docs/CACHE_SYSTEM.md` avec des liens vers les fichiers `.puml` sources.

## 🎯 Cas d'Usage

Ces diagrammes sont utiles pour :

- **Comprendre** le flux de cache lors d'une commande
- **Déboguer** les performances
- **Documenter** l'architecture pour les contributeurs
- **Optimiser** le système de cache

## 🔧 Personnalisation

Pour modifier un diagramme :

1. Éditer le fichier `.puml` correspondant
2. Prévisualiser en temps réel avec l'extension VS Code
3. Ou régénérer avec le script Python

## 📚 Ressources

- [Documentation PlantUML officielle](https://plantuml.com/)
- [Guide PlantUML - Séquences](https://plantuml.com/sequence-diagram)
- [Guide PlantUML - Composants](https://plantuml.com/component-diagram)
- [Guide PlantUML - États](https://plantuml.com/state-diagram)
