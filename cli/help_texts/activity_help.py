"""
Aide simplifiée pour la catégorie ACTIVITY.
"""

ACTIVITY_DESCRIPTION = """\
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mactivity\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34mlist         \033[0m : \033[0;90mLister les activités récentes\033[0m
  • \033[1;34minfo         \033[0m : \033[0;90mAfficher les détails d'une activité\033[0m
  • \033[1;34mlastdevice   \033[0m : \033[0;90mAfficher le dernier appareil utilisé\033[0m
  • \033[1;34mlastcommand  \033[0m : \033[0;90mAfficher la dernière commande vocale\033[0m
  • \033[1;34mlastresponse \033[0m : \033[0;90mAfficher la dernière réponse d'Alexa\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mactivity\033[0m \033[1;34mlist\033[0m
  \033[1;90malexa\033[0m \033[1;32mactivity\033[0m \033[1;34mlist --limit 50\033[0m
  \033[1;90malexa\033[0m \033[1;32mactivity\033[0m \033[1;34minfo <activity_id>\033[0m
  \033[1;90malexa\033[0m \033[1;32mactivity\033[0m \033[1;34mlastdevice\033[0m
  \033[1;90malexa\033[0m \033[1;32mactivity\033[0m \033[1;34mlastcommand -d "Salon Echo"\033[0m
  \033[1;90malexa\033[0m \033[1;32mactivity\033[0m \033[1;34mlastresponse\033[0m

\033[0;90mPour plus de détails:\033[0m \033[1;36malexa activity --help-web\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Placeholders pour compatibilité avec le code existant
INFO_HELP = "Voir aide principale: alexa activity -h"
LIST_HELP = "Voir aide principale: alexa activity -h"
