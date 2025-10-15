"""
Aide simplifiée pour la catégorie DND.
"""
# ruff: noqa: E501

DND_DESCRIPTION = """\
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mdnd\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34mstatus    \033[0m : \033[0;90mAfficher le statut du mode Ne pas déranger\033[0m
  • \033[1;34menable    \033[0m : \033[0;90mActiver le mode Ne pas déranger\033[0m
  • \033[1;34mdisable   \033[0m : \033[0;90mDésactiver le mode Ne pas déranger\033[0m
  • \033[1;34mschedule  \033[0m : \033[0;90mProgrammer le mode Ne pas déranger\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mdnd\033[0m \033[1;34menable -d Salon\033[0m
  \033[1;90malexa\033[0m \033[1;32mdnd\033[0m \033[1;34mdisable -d Cuisine\033[0m
  \033[1;90malexa\033[0m \033[1;32mdnd\033[0m \033[1;34mschedule -d Chambre --start 22:00 --end 07:00\033[0m

\033[0;90mPour plus de détails:\033[0m \033[1;36malexa dnd --help-web\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Placeholders pour compatibilité avec le code existant
DISABLE_HELP = "Voir aide principale: alexa dnd -h"
ENABLE_HELP = "Voir aide principale: alexa dnd -h"
SCHEDULE_HELP = "Voir aide principale: alexa dnd -h"
STATUS_HELP = "Voir aide principale: alexa dnd -h"
