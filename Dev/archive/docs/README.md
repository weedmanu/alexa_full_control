# 📚 Documentation Alexa Full Control

**Dernière mise à jour** : 16 octobre 2025  
**Version** : 2.0.0  
**Public** : Utilisateurs et développeurs

---

## 🎯 Navigation Rapide

### Pour **Utilisateurs CLI**

1. **Première utilisation ?** → [`CLI_HELP_GUIDE.md`](CLI_HELP_GUIDE.md)
2. **Installer le projet ?** → [`INSTALL_UNINSTALL_README.md`](INSTALL_UNINSTALL_README.md)
3. **Problèmes d'auth ?** → [`INSTALL_UNINSTALL_README.md`](INSTALL_UNINSTALL_README.md) + tester `alexa auth create`
4. **Commandes disponibles ?** → `alexa --help` (dans le terminal)

### Pour **Développeurs**

1. **Setup environnement ?** → [`DEVELOPMENT_SETUP.md`](DEVELOPMENT_SETUP.md)
2. **Comprendre l'archi ?** → [`ARCHITECTURE.md`](ARCHITECTURE.md)
3. **Quels endpoints API ?** → [`API_ENDPOINTS.md`](API_ENDPOINTS.md)
4. **Logging/Debug ?** → [`LOGGING_SYSTEM.md`](LOGGING_SYSTEM.md)
5. **QA/Tests ?** → [`DEVELOPMENT_SETUP.md`](DEVELOPMENT_SETUP.md#-outils-de-qualité-de-code)

### Pour **DevOps/Ops**

1. **Installation production ?** → [`INSTALL_UNINSTALL_README.md`](INSTALL_UNINSTALL_README.md)
2. **Logs et monitoring ?** → [`LOGGING_SYSTEM.md`](LOGGING_SYSTEM.md)
3. **Rapports QA ?** → [`CODE_QUALITY_REPORT.md`](CODE_QUALITY_REPORT.md)
4. **Architecture système ?** → [`ARCHITECTURE.md`](ARCHITECTURE.md)

---

## 📖 Guide Complet des Fichiers

### 🔐 **INSTALL_UNINSTALL_README.md**

- Installation complète (nodeenv + pip)
- Configuration d'authentification
- Désinstallation propre
- Prérequis par plateforme

**→ Consulter si** : Vous installez/désinstallez le projet

---

### 🎨 **CLI_HELP_GUIDE.md**

- Structure hiérarchique des aides
- Emojis et formatage CLI
- Bonnes pratiques
- Implémentation technique

**→ Consulter si** : Vous utilisez `alexa --help` ou modifiez l'interface CLI

---

### 🏗️ **ARCHITECTURE.md**

- Refactorisation Phase 1-9
- BaseManager (classe de base)
- Optimisations de performance
- Patterns architecturaux
- Cache multi-niveaux

**→ Consulter si** : Vous contribuez au code ou comprenez l'design du projet

---

### 🔧 **DEVELOPMENT_SETUP.md**

- Configuration Python (.venv à la racine)
- Installation des dépendances
- Outils QA (mypy, ruff, black, pytest, etc.)
- CI/CD GitHub Actions
- Workflow de développement
- Dépannage

**→ Consulter si** : Vous développez localement ou configurez un environnement

---

### 🔌 **API_ENDPOINTS.md**

- Endpoints API Alexa validés
- Authentification et session
- Gestion appareils, volume, musique
- Notifications et rappels
- Fallback strategy
- Endpoints dépréciés

**→ Consulter si** : Vous développez une nouvelle fonctionnalité ou debuggez un appel API

---

### 📋 **LOGGING_SYSTEM.md**

- Logger basique vs Loguru
- Niveaux de logging
- Configuration
- Variables d'environnement
- Fichiers de logs

**→ Consulter si** : Vous debuggez une issue ou configurez les logs

---

### 📊 **CODE_QUALITY_REPORT.md**

- Résultats des outils QA
- Couverture de tests
- Métriques de performance
- Standards respectés

**→ Consulter si** : Vous vérifiez l'état de qualité du code

---

## 🚀 Démarrage Rapide

### Installation (5 min)

```bash
git clone https://github.com/weedmanu/alexa_full_control.git
cd alexa_full_control
python scripts/install.py
```

### Premier Test (2 min)

```bash
python alexa auth create    # Authentifier
python alexa device list    # Lister vos appareils
```

### Développement (10 min)

```bash
# Activer .venv
.\.venv\Scripts\Activate.ps1  # Windows
# ou
source .venv/bin/activate     # Unix/macOS

# Installer dépendances dev
pip install -r requirements-dev.txt

# Lancer la QA
python dev_quality.py --all
```

---

## 🆘 FAQ & Dépannage

### ❓ Erreur d'authentification (404 API)

**Vérifier** :

1. Les cookies sont valides → `alexa auth create` si expiré
2. Domaine correct → Doit être `alexa.amazon.fr` (pas `amazon.fr`)
3. Les logs → `DEBUG=true python alexa device list`

**Voir** : [`INSTALL_UNINSTALL_README.md`](INSTALL_UNINSTALL_README.md)

---

### ❓ Tests échouent localement

**Vérifier** :

1. `.venv` activé → Affichage `(.venv)` dans le terminal
2. Dépendances installées → `pip list | grep pytest`
3. Python version → `python --version` (doit être 3.11+)

**Solution** :

```bash
rm -rf .venv
python -m venv .venv
# Activer .venv
pip install -r requirements-dev.txt
python dev_quality.py --pytest
```

---

### ❓ Comment contribuer ?

1. Fork le projet
2. Créer une branche `feature/ma-fonction`
3. Valider : `python dev_quality.py --all`
4. Créer une PR vers `main`

**Voir** : [`DEVELOPMENT_SETUP.md#-workflow-de-développement-recommandé`](DEVELOPMENT_SETUP.md#-workflow-de-développement-recommandé)

---

## 📞 Support

- **Issues** : GitHub Issues (reporting de bugs)
- **Discussions** : GitHub Discussions (questions générales)
- **PRs** : Toujours bienvenues avec des tests ✨

---

## 📈 Historique de la Documentation

| Date       | Change                                            | Impact            |
| ---------- | ------------------------------------------------- | ----------------- |
| 2025-10-16 | Refactorisation : 16→8 fichiers, 8000→1500 lignes | -81% verbosité ✨ |
| 2025-10-15 | Correction bug Alexa auth (domaine)               | 🐛 fix            |
| 2025-10-08 | Création documentation Phase 1-9                  | 📚 initial        |

---

**Responsable** : M@nu  
**Licence** : MIT  
**Contact** : GitHub Issues
