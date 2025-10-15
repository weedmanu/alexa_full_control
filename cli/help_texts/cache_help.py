# ruff: noqa: E501
"""Aide simplifiée pour la catégorie CACHE.

\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mcache\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34mstatus\033[0m                              : \033[0;90mAfficher l'état du cache\033[0m
  • \033[1;34mrefresh\033[0m                             : \033[0;90mRafraîchir le cache depuis l'API\033[0m
  • \033[1;34mrefresh\033[0m \033[0;34m--category\033[0m \033[0;36mCATEGORY\033[0m      : \033[0;90mRafraîchir une catégorie spécifique (devices, smart_home, alarms_and_reminders, all)\033[0m
  • \033[1;34mshow\033[0m \033[0;34m--category\033[0m \033[0;36mCATEGORY\033[0m          : \033[0;90mAfficher le contenu JSON d'une catégorie\033[0m
  • \033[1;34mclear\033[0m                               : \033[0;90mVider complètement le cache\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mcache\033[0m \033[1;34mstatus\033[0m
  \033[1;90malexa\033[0m \033[1;32mcache\033[0m \033[1;34mrefresh\033[0m
  \033[1;90malexa\033[0m \033[1;32mcache\033[0m \033[1;34mrefresh\033[0m \033[0;34m--category\033[0m \033[0;36mdevices\033[0m
  \033[1;90malexa\033[0m \033[1;32mcache\033[0m \033[1;34mshow\033[0m \033[0;34m--category\033[0m \033[0;36mdevices\033[0m
  \033[1;90malexa\033[0m \033[1;32mcache\033[0m \033[1;34mclear\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Description courte utilisée par le parser
CACHE_DESCRIPTION = "Aide pour la catégorie 'cache' — inspection et gestion du cache local."

# Placeholders pour compatibilité avec le code existant
CLEAR_HELP = "Voir aide principale: alexa cache -h"
REFRESH_HELP = "Voir aide principale: alexa cache -h"
SHOW_HELP = "Voir aide principale: alexa cache -h"
STATUS_HELP = "Voir aide principale: alexa cache -h"
