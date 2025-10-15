# Guide de formatage des aides CLI

## 📋 Vue d'ensemble

Ce guide documente le système modulaire de formatage des aides CLI pour garantir une cohérence visuelle parfaite à travers tous les niveaux de `-h`.

## 🎨 Correspondance Ligne d'usage → Fonctions de formatage

### Ligne d'usage complète (alexa -h)

```
alexa [OPTIONS_GLOBALES] <CATEGORIE> [OPTIONS_CATEGORIE] [<SOUS-CATEGORIE>] [OPTIONS_SOUS-CATEGORIE] [<ACTION>] [OPTIONS_ACTION]
```

### Fonctions disponibles pour chaque champ

| Champ d'usage              | Couleur         | Fonction de formatage                           | Utilisation                                             |
| -------------------------- | --------------- | ----------------------------------------------- | ------------------------------------------------------- |
| `[OPTIONS_GLOBALES]`       | Magenta clair   | `format_global_options()`                       | Affiche les options `-h`, `-v`, `--verbose`, etc.       |
| `<CATEGORIE>`              | **Vert gras**   | `format_current_category(name, desc, emoji)`    | Section "Catégorie actuelle" avec séparateurs VERTS     |
| `[OPTIONS_CATEGORIE]`      | Vert clair      | `format_category_options(text)`                 | Section "Options de la catégorie actuelle"              |
| `<SOUS-CATEGORIE>`         | **Cyan gras**   | `format_current_subcategory(name, desc, emoji)` | Section "Sous-catégorie actuelle" avec séparateurs CYAN |
| `[OPTIONS_SOUS-CATEGORIE]` | Cyan clair      | `format_subcategory_options(text)`              | Section "Options de la sous-catégorie actuelle"         |
| `<ACTION>`                 | **Orange gras** | `format_actions(actions_list)`                  | Section "Actions disponibles" avec séparateurs ORANGE   |
| `[OPTIONS_ACTION]`         | Orange clair    | `format_action_options(options_list)`           | Section "Options d'action"                              |

## 🎯 Codes couleurs ANSI

```python
# Couleurs des champs de la ligne d'usage
Colors.MAGENTA        = '\033[1;35m'      # OPTIONS_GLOBALES (titre)
Colors.MAGENTA_LIGHT  = '\033[0;35m'      # OPTIONS_GLOBALES (contenu)
Colors.GREEN          = '\033[1;32m'      # CATEGORIE (gras)
Colors.GREEN_LIGHT    = '\033[0;32m'      # OPTIONS_CATEGORIE (clair)
Colors.CYAN           = '\033[1;36m'      # SOUS-CATEGORIE (gras)
Colors.CYAN_LIGHT     = '\033[0;36m'      # OPTIONS_SOUS-CATEGORIE (clair)
Colors.ORANGE         = '\033[1;38;5;208m'  # ACTION (gras)
Colors.ORANGE_LIGHT   = '\033[0;38;5;208m'  # OPTIONS_ACTION (clair)
```

## 📦 Autres fonctions communes

| Fonction                                               | Description               | Couleur        |
| ------------------------------------------------------ | ------------------------- | -------------- |
| `format_header(emoji, title)`                          | En-tête principal centré  | Blanc gras     |
| `format_features(items, show_title)`                   | Liste des fonctionnalités | Gris           |
| `format_usage(category, subcategory, action, is_main)` | Ligne d'usage colorée     | Multi-couleurs |
| `format_examples(examples)`                            | Exemples d'utilisation    | Jaune          |
| `format_prerequisites(prereqs)`                        | Prérequis essentiels      | Rouge          |

## 🔧 Exemples d'utilisation

### Aide de catégorie (ex: auth -h)

```python
from utils.help_formatter import (
    format_header,
    format_features,
    format_global_options,
    format_current_category,
    format_category_options,
    format_actions,
    format_examples,
    format_prerequisites
)

def get_auth_category_help() -> str:
    sections = []

    # 1. Header
    sections.append(format_header("🔐", "AUTHENTIFICATION AMAZON ALEXA"))

    # 2. Fonctionnalités
    sections.append(format_features([
        "Authentification sécurisée",
        "Gestion automatique des tokens"
    ], show_title=True))

    # 3. Options globales
    sections.append(format_global_options())

    # 4. Catégorie actuelle (VERT GRAS comme <CATEGORIE>)
    sections.append(format_current_category(
        "auth",
        "Gestion de l'authentification",
        "🔐"  # Emoji personnalisé
    ))

    # 5. Options de catégorie (VERT CLAIR)
    sections.append(format_category_options(
        "Aucune option pour cette catégorie"
    ))

    # 6. Actions (ORANGE GRAS comme <ACTION>)
    sections.append(format_actions([
        {"name": "create", "desc": "Créer une session"},
        {"name": "status", "desc": "Vérifier l'état"}
    ]))

    # 7. Exemples
    sections.append(format_examples([
        "alexa auth create",
        "alexa auth status"
    ]))

    # 8. Prérequis
    sections.append(format_prerequisites([
        "Authentification requise",
        "Connexion internet"
    ]))

    return "\n\n".join(sections) + "\n"
```

### Aide de sous-catégorie (ex: timer countdown -h)

```python
from utils.help_formatter import (
    format_header,
    format_features,
    format_global_options,
    format_current_category,
    format_category_options,
    format_current_subcategory,
    format_subcategory_options,
    format_actions,
    format_examples,
    format_prerequisites
)

def get_countdown_subcategory_help() -> str:
    sections = []

    # Catégorie parente (VERT)
    sections.append(format_current_category(
        "timer",
        "Gestion du temps",
        "⏱️"
    ))

    # Sous-catégorie actuelle (CYAN GRAS comme <SOUS-CATEGORIE>)
    sections.append(format_current_subcategory(
        "countdown",
        "Minuteurs et décomptes",
        "⏰"
    ))

    # Options de sous-catégorie (CYAN CLAIR)
    sections.append(format_subcategory_options(
        "Aucune option pour cette sous-catégorie"
    ))

    # Actions...
    sections.append(format_actions([...]))

    return "\n\n".join(sections) + "\n"
```

## ✅ Règles de cohérence

1. **Les séparateurs doivent TOUJOURS avoir la même couleur que le champ correspondant** :

   - Section "Catégorie actuelle" → séparateurs **VERTS** (comme `<CATEGORIE>`)
   - Section "Sous-catégorie actuelle" → séparateurs **CYAN** (comme `<SOUS-CATEGORIE>`)
   - Section "Actions disponibles" → séparateurs **ORANGE** (comme `<ACTION>`)

2. **Les options utilisent la version claire de la couleur** :

   - Options de catégorie → vert clair (`GREEN_LIGHT`)
   - Options de sous-catégorie → cyan clair (`CYAN_LIGHT`)
   - Options d'action → orange clair (`ORANGE_LIGHT`)

3. **Toujours utiliser les fonctions centralisées** de `utils/help_formatter.py` pour garantir la cohérence

## 📝 Checklist de validation

- [ ] Les séparateurs de "Catégorie actuelle" sont **verts gras** (comme `auth` dans la ligne d'usage)
- [ ] Les séparateurs de "Sous-catégorie actuelle" sont **cyan gras** (comme `countdown`)
- [ ] Les séparateurs d"Actions disponibles" sont **orange gras** (comme `create`)
- [ ] Les options utilisent les couleurs claires appropriées
- [ ] Toutes les sections utilisent les fonctions centralisées de `help_formatter.py`
- [ ] L'emoji de chaque section correspond au contexte

## 🔍 Tests visuels

Pour vérifier que les couleurs s'affichent correctement :

```bash
# Aide principale
python alexa -h

# Aide de catégorie
python alexa auth -h
python alexa timer -h

# Aide de sous-catégorie
python alexa timer countdown -h

# Aide d'action
python alexa auth create -h
```

Vérifiez visuellement que :

- Les couleurs correspondent à la ligne d'usage
- Les séparateurs ont la bonne couleur
- Aucun texte n'apparaît en gris alors qu'il devrait être coloré
