"""
Aide simplifiée pour la catégorie ROUTINE.
"""

# ruff: noqa: E501

ROUTINE_DESCRIPTION = """\
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mroutine\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

  \033[1;90mou\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mroutine\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m \033[1;36m<DEVICE>\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34mlist\033[0m                                                          : \033[0;90mLister les routines\033[0m
  • \033[1;34mlist\033[0m \033[0;34m--only-active\033[0m                                           : \033[0;90mAfficher uniquement les routines activées\033[0m
  • \033[1;34minfo\033[0m \033[0;36m--name "ROUTINE"\033[0m \033[1;36m--device "DEVICE"\033[0m                 : \033[0;90mAfficher les détails d'une routine\033[0m
  • \033[1;34mexecute\033[0m \033[0;36m--name "ROUTINE"\033[0m \033[1;36m--device "DEVICE"\033[0m              : \033[0;90mExécuter une routine sur un appareil\033[0m
  • \033[1;34menable\033[0m \033[0;36m--name "ROUTINE"\033[0m \033[1;36m--device "DEVICE"\033[0m               : \033[0;90mActiver une routine\033[0m
  • \033[1;34mdisable\033[0m \033[0;36m--name "ROUTINE"\033[0m \033[1;36m--device "DEVICE"\033[0m              : \033[0;90mDésactiver une routine\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mroutine\033[0m \033[1;34mlist\033[0m
  \033[1;90malexa\033[0m \033[1;32mroutine\033[0m \033[1;34mlist\033[0m \033[0;34m--only-active\033[0m
  \033[1;90malexa\033[0m \033[1;32mroutine\033[0m \033[1;34minfo\033[0m \033[0;36m--name\033[0m \033[0;36m"Solange"\033[0m \033[1;36m--device\033[0m \033[1;36m"Salon Echo"\033[0m
  \033[1;90malexa\033[0m \033[1;32mroutine\033[0m \033[1;34mexecute\033[0m \033[0;36m--name\033[0m \033[0;36m"Solange"\033[0m \033[1;36m--device\033[0m \033[1;36m"Salon Echo"\033[0m
  \033[1;90malexa\033[0m \033[1;32mroutine\033[0m \033[1;34menable\033[0m \033[0;36m--name\033[0m \033[0;36m"Solange"\033[0m \033[1;36m--device\033[0m \033[1;36m"Salon Echo"\033[0m
  \033[1;90malexa\033[0m \033[1;32mroutine\033[0m \033[1;34mdisable\033[0m \033[0;36m--name\033[0m \033[0;36m"Solange"\033[0m \033[1;36m--device\033[0m \033[1;36m"Salon Echo"\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Placeholders pour compatibilité avec le code existant
DISABLE_HELP = "Voir aide principale: alexa routine -h"
ENABLE_HELP = "Voir aide principale: alexa routine -h"
EXECUTE_HELP = "Voir aide principale: alexa routine -h"
INFO_HELP = "Voir aide principale: alexa routine -h"
LIST_HELP = "Voir aide principale: alexa routine -h"
