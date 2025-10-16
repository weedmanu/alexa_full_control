# 📖 Guide CLI - Aide et Formatage

**Date** : 16 octobre 2025  
**Version** : 2.0.0  
**Objectif** : Documentation des aides CLI et conventions de formatage

---

## 🎯 Objectif

Fournir une **aide cohérente et professionnelle** à tous les niveaux de la CLI (principal, catégorie, action), garantissant une expérience utilisateur uniforme et intuitive.

---

## 🏗️ Philosophie Générale

### Principes Fondamentaux

- **Cohérence**: Même structure et formatage partout
- **Hiérarchie claire**: Du général au spécifique
- **Robustesse**: Fonctionne même en cas de problèmes
- **Performance**: Génération rapide sans calculs coûteux
- **Accessibilité**: Support `--no-color` pour tous les terminaux

---

## 📊 Structure Hiérarchique des Aides

### Niveau 1 : Aide Principale

**Commande**: `alexa --help` ou `alexa`

**Contenu**:

- Titre général avec emoji
- Résumé des fonctionnalités
- Usage général
- Options globales (`--verbose`, `--debug`, `--no-color`, `--config`)
- Catégories disponibles
- Exemples d'utilisation
- Prérequis essentiels

**Exemple**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       🎙️  ALEXA VOICE CONTROL - Contrôle Avancé d'Alexa
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
  alexa [OPTIONS] <CATEGORIE> <ACTION> [OPTIONS_ACTION]

Catégories:
  auth              Authentification
  device            Gestion des appareils
  music             Contrôle musical
  ...

Pour plus d'aide:
  alexa device --help
```

### Niveau 2 : Aide de Catégorie

**Commande**: `alexa <categorie> --help`

**Contenu**:

- Titre spécifique à la catégorie
- Description détaillée
- Usage
- Options de catégorie
- Actions disponibles
- Exemples spécifiques
- Prérequis de la catégorie

**Exemple**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵  MUSIC - Contrôle de la Musique
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
  alexa music <ACTION> [OPTIONS_ACTION]

Actions:
  play              Jouer de la musique
  stop              Arrêter la musique
  status            État actuel
  ...

Pour plus d'aide:
  alexa music play --help
```

### Niveau 3 : Aide d'Action

**Commande**: `alexa <categorie> <action> --help`

**Contenu**:

- Titre spécifique à l'action
- Description détaillée
- Syntaxe complète
- Arguments requis/optionnels
- Options spécifiques
- Exemples concrets
- Comportement en cas d'erreur

**Exemple**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⏯️  MUSIC PLAY - Jouer de la Musique
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Syntaxe:
  alexa music play [OPTIONS]

Options:
  -d, --device DEVICE    Appareil cible (requis)
  -s, --search SEARCH    Recherche musicale
  -p, --playlist NAME    Playlist à jouer
  --shuffle              Mode mélange
  ...

Exemples:
  alexa music play -d "Salon Echo" -s "Soleil Bleu"
  alexa music play -d "Chambre" --playlist "Relaxation"
```

---

## 🎨 Formatage Visuel

### Convention de Nommage

```
CATEGORIE    : commande de haut niveau (ex: "music")
ACTION       : sous-commande (ex: "play", "stop", "status")
DEVICE       : paramètre entre guillemets (ex: "Salon Echo")
[OPTION]     : option optionnelle
<PARAMETRE>  : paramètre obligatoire
```

### Emojis Standardisés

| Élément      | Emoji | Usage               |
| ------------ | ----- | ------------------- |
| Principal    | 🎙️    | Titre principal     |
| Musique      | 🎵    | Commandes musicales |
| Timer/Alarme | ⏰    | Gestion du temps    |
| Appareil     | 📱    | Gestion appareils   |
| Maison       | 🏠    | Domotique           |
| Auth         | 🔐    | Authentification    |
| Cache        | 💾    | Gestion du cache    |

### Séparateurs

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📝 Bonnes Pratiques

### ✅ À FAIRE

- **Texte court et clair**: Pas de phrases longues
- **Exemples concrets**: Montrer l'utilisation réelle
- **Organisation logique**: Du général au spécifique
- **Cohérence terminologie**: Même terme = même sens partout
- **Tests automatiques**: Vérifier que `--help` fonctionne

### ❌ À ÉVITER

- Jargon technique excessif
- Aides plus longues que la fonctionnalité elle-même
- Enroulement de texte chaotique
- Incohérence dans les formats
- Aide générée dynamiquement (problèmes de perf)

---

## 🔧 Implémentation Technique

### BaseCommand

```python
class BaseCommand:
    """Classe de base pour toutes les commandes."""

    def print_help(self):
        """Affiche l'aide de la commande."""
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  {self.emoji}  {self.category.upper()} - {self.description}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        # ... afficher options, exemples, etc.
```

### Validation des Aides

```bash
# Vérifier que toutes les commandes ont une aide
pytest tests/test_help_system.py -v

# Vérifier la longueur des aides
pytest tests/test_help_length.py -v
```

---

## 📚 Ressources

- Aide principale: `alexa --help`
- Aide par catégorie: `alexa <categorie> --help`
- Aide par action: `alexa <categorie> <action> --help`
- Logs détaillés: `alexa --debug <categorie> <action>`
- Configuration: `alexa --config /chemin/config.json`

---

**Dernière mise à jour** : 16 octobre 2025  
**Responsable** : M@nu
