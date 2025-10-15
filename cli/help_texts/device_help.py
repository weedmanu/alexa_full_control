# ruff: noqa: E501
"""
Aide simplifiée pour la catégorie DEVICE.

\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mdevice\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

  \033[1;90mou\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mdevice\033[0m \033[1;34m<ACTION>\033[0m \033[1;33m<COMMANDE>\033[0m \033[1;36m[DEVICE]\033[0m \033[0;33m[OPTIONS_COMMANDE]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34mlist\033[0m                                          : \033[0;90mLister tous les appareils\033[0m
  • \033[1;34mlist\033[0m \033[0;34m--refresh\033[0m                                : \033[0;90mForcer la resynchronisation avant d'afficher\033[0m
  • \033[1;34mlist\033[0m \033[0;34m--filter\033[0m \033[0;34m"PATTERN"\033[0m                       : \033[0;90mFiltrer les appareils par nom (recherche partielle)\033[0m
  • \033[1;34mlist\033[0m \033[0;34m--online-only\033[0m                            : \033[0;90mAfficher uniquement les appareils en ligne\033[0m
  • \033[1;34minfo\033[0m \033[0;36m--device "DEVICE"\033[0m                        : \033[0;90mAfficher les informations d'un appareil\033[0m
  • \033[1;34mvolume\033[0m \033[1;33mget\033[0m \033[0;36m--device "DEVICE"\033[0m                  : \033[0;90mRécupérer le volume d'un appareil\033[0m
  • \033[1;34mvolume\033[0m \033[1;33mset\033[0m \033[0;36m--device "DEVICE"\033[0m \033[0;33m--level VOLUME\033[0m   : \033[0;90mParamétrer le volume d'un appareil en % (0-100)\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mdevice\033[0m list
  \033[1;90malexa\033[0m \033[1;32mdevice\033[0m \033[1;34mlist\033[0m \033[0;34m--refresh\033[0m
  \033[1;90malexa\033[0m \033[1;32mdevice\033[0m \033[1;34mlist\033[0m \033[0;34m--filter\033[0m \033[0;34m"Echo"\033[0m
  \033[1;90malexa\033[0m \033[1;32mdevice\033[0m \033[1;34mlist\033[0m \033[0;34m--online-only\033[0m
  \033[1;90malexa\033[0m \033[1;32mdevice\033[0m \033[1;34minfo\033[0m \033[0;36m--device "Salon Echo"\033[0m
  \033[1;90malexa\033[0m \033[1;32mdevice\033[0m \033[1;34mvolume\033[0m \033[1;33mget\033[0m \033[0;36m--device "Salon Echo"\033[0m
  \033[1;90malexa\033[0m \033[1;32mdevice\033[0m \033[1;34mvolume\033[0m \033[1;33mset\033[0m \033[0;36m--device "Salon Echo"\033[0m \033[0;33m--level\033[0m \033[0;33m50\033[0m

  \033[1;90mAvec une option globale :\033[0m

  \033[1;90malexa\033[0m \033[1;35m--verbose\033[0m \033[1;32mdevice\033[0m \033[1;34mlist\033[0m
  \033[1;90malexa\033[0m \033[1;35m--debug\033[0m \033[1;32mdevice\033[0m \033[1;34mlist\033[0m

\033[0;90mPour plus de détails:\033[0m \033[1;36malexa device --help-web\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Placeholders pour compatibilité avec le code existant
INFO_HELP = "Voir aide principale: alexa device -h"
LIST_HELP = "Voir aide principale: alexa device -h"
VOLUME_HELP = "Voir aide principale: alexa device -h"

# Description constant exported for CLI help imports
DEVICE_DESCRIPTION = (
    "Gestion des appareils (liste, informations, contrôle du volume). "
    'Exemples: "alexa device list", "alexa device info --device "Salon Echo"", '
    '"alexa device volume set --device "Salon Echo" --level 50".'
)
