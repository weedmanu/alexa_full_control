# noqa: E501
# ruff: noqa: E501
"""Textes d'aide pour la commande 'calendar'.

Contient toutes les descriptions et exemples d'utilisation
pour la gestion du calendrier Alexa.

Auteur: M@nu
Date: 12 octobre 2025
"""

CALENDAR_DESCRIPTION = "Aide pour la catégorie 'calendar' — gestion des événements, ajout, suppression et affichage."

LIST_HELP = """
Lister les événements du calendrier

Usage:
  alexa calendar list [OPTIONS]

Options:
  --days N          Nombre de jours à afficher (défaut: 30)
  --limit N         Nombre maximum d'événements (défaut: 50)
  --json            Afficher au format JSON

Exemples:
  alexa calendar list
  alexa calendar list --days 7
  alexa calendar list --limit 10
  alexa calendar list --json

Notes:
  Les événements sont synchronisés depuis votre compte Amazon.
  Seuls les événements futurs sont affichés.
"""

ADD_HELP = """
Ajouter un événement au calendrier

Usage:
  alexa calendar add --title "TITRE" --start "DATE_HEURE" [OPTIONS]

Options requises:
  --title "TEXT"        Titre de l'événement
  --start "DATETIME"    Date/heure de début (format: YYYY-MM-DD HH:MM)

Options facultatives:
  --end "DATETIME"      Date/heure de fin (défaut: +1h après le début)
  --location "TEXT"     Lieu de l'événement
  --description "TEXT"  Description de l'événement

Exemples:
  alexa calendar add --title "Réunion équipe" --start "2025-10-15 14:00"
  alexa calendar add --title "Conférence" --start "2025-10-20 09:00" --end "2025-10-20 17:00" --location "Paris" --description "Conférence annuelle"
  alexa calendar add --title "Dentiste" --start "2025-10-18 10:30" --location "Cabinet Dr. Martin"

Notes:
  Les formats de date acceptés:
    - YYYY-MM-DD HH:MM  (ex: 2025-10-15 14:00)
    - DD/MM/YYYY HH:MM  (ex: 15/10/2025 14:00)

  Si --end n'est pas spécifié, la durée est de 1 heure par défaut.
"""

DELETE_HELP = """
Supprimer un événement du calendrier

Usage:
  alexa calendar delete --id EVENT_ID

Options:
  --id EVENT_ID         ID de l'événement à supprimer

Exemples:
  alexa calendar delete --id evt_12345
  alexa calendar list
  alexa calendar delete --id evt_67890

Notes:
  L'ID de l'événement peut être trouvé avec:
    alexa calendar list --json

  La suppression est immédiate et irréversible.
"""

INFO_HELP = """
Afficher les détails d'un événement

Usage:
  alexa calendar info --id EVENT_ID

Options:
  --id EVENT_ID         ID de l'événement
  --json                Afficher au format JSON

Exemples:
  alexa calendar info --id evt_12345
  alexa calendar info --id evt_12345 --json

Notes:
  Affiche toutes les informations:
    - Titre
    - Date/heure de début et fin
    - Lieu
    - Description
    - Participants (si applicable)
"""
