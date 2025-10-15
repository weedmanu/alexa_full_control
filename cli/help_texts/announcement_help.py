# noqa: E501
# ruff: noqa: E501
"""Aide simplifiée pour la catégorie ANNOUNCEMENT.

\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mannouncement\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34msend   \033[0m : \033[0;90mEnvoyer une annonce\033[0m
  • \033[1;34mlist   \033[0m : \033[0;90mLister les annonces\033[0m
  • \033[1;34mclear  \033[0m : \033[0;90mEffacer les annonces\033[0m
  • \033[1;34mread   \033[0m : \033[0;90mMarquer une annonce comme lue\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mannouncement\033[0m \033[1;34msend "Message important" -d Salon\033[0m
  \033[1;90malexa\033[0m \033[1;32mannouncement\033[0m \033[1;34mlist\033[0m
  \033[1;90malexa\033[0m \033[1;32mannouncement\033[0m \033[1;34mclear\033[0m
  \033[1;90malexa\033[0m \033[1;32mannouncement\033[0m \033[1;34mread <notif_id>\033[0m

\033[0;90mPour plus de détails:\033[0m \033[1;36malexa announcement --help-web\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Description courte utilisée par le parser
ANNOUNCE_DESCRIPTION = "Aide pour la catégorie 'announcement' — envoyer, lister, effacer et lire les annonces."

# Placeholders pour compatibilité avec le code existant
CLEAR_HELP = "Voir aide principale: alexa announcement -h"
LIST_HELP = "Voir aide principale: alexa announcement -h"
READ_HELP = "Voir aide principale: alexa announcement -h"
SEND_HELP = "Voir aide principale: alexa announcement -h"
