# 🚀 Guide d'Installation - Alexa Advanced Control

## 📋 Prérequis

- **Python 3.8+** : [Télécharger Python](https://www.python.org/downloads/)
- **pip** : Inclus avec Python
- **Connexion Internet** : Pour télécharger les dépendances

## 🎯 Installation Rapide

### Windows, Linux, macOS

```bash
# Installation normale
python scripts/install.py

# Installation avec réinstallation forcée
python scripts/install.py --force

# Installation sans tests (plus rapide)
python scripts/install.py --skip-tests
```

## 📦 Ce qui est installé

### Dans le projet (.venv)

- ✅ Environnement virtuel Python (`.venv/`)
- ✅ Dépendances du projet (requests, loguru, beautifulsoup4, etc.)
- ✅ Node.js v20.17.0 (via nodeenv)
- ✅ Packages npm (alexa-cookie2, yargs)

### Outils de développement (globaux)

Les outils suivants sont installés **globalement** et disponibles partout :

- 🎨 **Formatage** : black, autopep8, isort
- 🔍 **Analyse** : pylint, flake8, ruff, mypy, vulture, bandit
- 🧪 **Tests** : pytest, pytest-cov, pytest-mock, tox
- 📊 **Qualité** : coverage, pre-commit
- 📚 **Documentation** : sphinx, diagrams
- 📦 **Build** : pyinstaller
- 📦 **Build** : (outil global, non listé par défaut)

## 🔧 Utilisation après installation

### 1. Activer l'environnement virtuel

**Windows (PowerShell/CMD) :**

```powershell
.venv\Scripts\Activate.ps1  # PowerShell
.venv\Scripts\activate.bat   # CMD
```

**Linux/macOS :**

```bash
source .venv/bin/activate
```

### 2. Créer l'authentification Alexa

```bash
python alexa auth create
```

### 3. Utiliser les commandes

```bash
# Afficher l'aide
python alexa --help

# Lister les appareils
python alexa device list

# Contrôler la musique
python alexa music play -d "Salon Echo" -s "Soleil bleu"

# Créer un timer
python alexa timer create -d "Cuisine" --duration 10 --label "Pâtes"
```

## 🗑️ Désinstallation

```bash
# Désinstallation complète (interactive)
python scripts/install.py --uninstall

IMPORTANT: Ne lancez pas la désinstallation depuis l'environnement virtuel du projet (.venv).
Quittez le venv avec `deactivate` avant d'exécuter la commande.
```

Supprime :

- L'environnement virtuel `.venv/`
- L'environnement Node.js `.nodeenv/`
- Les caches Python `__pycache__/`

**Note :** Les outils de développement globaux ne sont pas supprimés.

## 🔄 Réinstallation

Si vous rencontrez des problèmes :

```bash
# Réinstallation complète (supprime et réinstalle)
python scripts/install.py --force
```

## ❓ Résolution de problèmes

### Erreur "Python n'est pas reconnu"

**Solution :** Ajoutez Python au PATH système.

- **Windows** : Réinstallez Python avec l'option "Add to PATH"
- **Linux/macOS** : Installez via votre gestionnaire de paquets

### Erreur "Module 'nodeenv' introuvable"

**Solution :** Le script installe automatiquement nodeenv. Si l'erreur persiste :

```bash
pip install nodeenv>=1.8.0
python scripts/install.py --force
```

### Erreur "Permission denied"

**Solution :**

- **Windows** : Exécutez en tant qu'administrateur
- **Linux/macOS** : N'utilisez PAS `sudo`, créez un venv avec vos droits utilisateur

### L'installation se bloque

**Solution :**

1. Annulez avec `Ctrl+C`
2. Nettoyez :
   ```bash
   python scripts/install.py --uninstall
   ```
3. Réessayez :
   ```bash
   python scripts/install.py --force
   ```

## 🛠️ Options avancées

### Options disponibles

```bash
python scripts/install.py --help
```

| Option         | Description                                                        |
| -------------- | ------------------------------------------------------------------ |
| `--force`      | Force la réinstallation (supprime l'installation existante)        |
| `--skip-tests` | Saute les tests de configuration finale (installation plus rapide) |
| `--uninstall`  | Désinstalle complètement le projet (interactive)                   |

### Installation sans interaction

Pour une installation automatique (CI/CD) :

```bash
python scripts/install.py --force --skip-tests
```

## 📁 Structure après installation

```
alexa_advanced_control/
├── .venv/                    # Environnement virtuel Python
│   ├── Scripts/ (Windows)
│   └── bin/ (Linux/macOS)
├── alexa_auth/
│   └── nodejs/
│       └── .nodeenv/         # Environnement Node.js
├── data/                     # Données de configuration
├── scripts/
│   └── install.py           # Script d'installation
└── alexa                    # Point d'entrée principal
```

## 🌐 Compatibilité

| OS            | Status      | Testé        |
| ------------- | ----------- | ------------ |
| Windows 10/11 | ✅ Supporté | ✅ Oui       |
| Ubuntu 20.04+ | ✅ Supporté | ✅ Oui       |
| macOS 11+     | ✅ Supporté | ✅ Oui       |
| Debian 11+    | ✅ Supporté | ⚠️ Non testé |

## 💡 Conseils

- **Toujours activer .venv** avant d'utiliser les commandes Alexa
- **Les outils dev sont globaux** : black, pytest, etc. disponibles partout
- **Node.js est isolé** : pas de conflit avec votre installation système
- **Mise à jour** : Réexécutez `python scripts/install.py --force`

## 📞 Support

En cas de problème :

1. Consultez cette documentation
2. Vérifiez les logs d'installation
3. Essayez `python scripts/install.py --force`
4. Ouvrez une issue sur GitHub (si applicable)

---

**Version:** 2.0.0  
**Date:** Octobre 2025  
**Auteur:** M@nu

## 📝 Changements récents

- Titre d'installation mis à jour : désormais affiché comme "🚀 INSTALLATION ALEXA ADVANCED CONTROL" lors du lancement du script.
- Ajout de l'alias court `--dry` (équivalent de `--dry-run`) pour simuler l'installation sans exécuter les commandes.
- Amélioration de l'affichage : les messages longs sont maintenant wrapés proprement et la sortie affiche les versions de pip sous la forme courte (ex. `pip 25.2`).

Extrait d'exécution (mode dry-run) :

```
══════════════════════════════════════════════════════════════════════════════
║                   🚀 INSTALLATION ALEXA ADVANCED CONTROL                   ║
══════════════════════════════════════════════════════════════════════════════

ℹ️  Système: Windows 11

✅  pip disponible (pip 25.2)

ℹ️  [dry-run] Commande simulée: C:\Python313\python.exe -m venv C:\...\.venv (cwd=...)
✅  Environnement virtuel créé
```

Ces changements améliorent la lisibilité de l'installation et permettent un test sans risque grâce à `--dry`.
