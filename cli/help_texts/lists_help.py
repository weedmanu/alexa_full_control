# ruff: noqa: E501

LISTS_DESCRIPTION = """\
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mlists\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34madd\033[0m \033[0;33m"TEXT"\033[0m                                : \033[0;90mAjouter un élément à une liste\033[0m
  • \033[1;34madd\033[0m \033[0;33m"TEXT"\033[0m \033[0;34m--priority\033[0m \033[0;34mLEVEL\033[0m                 : \033[0;90mAjouter une tâche avec priorité (low/medium/high)\033[0m
  • \033[1;34madd\033[0m \033[0;33m"TEXT"\033[0m \033[0;34m--due-date\033[0m \033[0;34mYYYY-MM-DD\033[0m          : \033[0;90mAjouter une tâche avec date d'échéance\033[0m
  • \033[1;34mremove\033[0m \033[0;33m"TEXT"\033[0m                             : \033[0;90mSupprimer un élément\033[0m
  • \033[1;34mclear\033[0m                                        : \033[0;90mVider complètement la liste\033[0m
  • \033[1;34mclear\033[0m \033[0;34m--completed-only\033[0m                     : \033[0;90mSupprimer uniquement les éléments complétés\033[0m
  • \033[1;34mclear\033[0m \033[0;34m--force\033[0m                               : \033[0;90mForcer le vidage avec confirmation automatique\033[0m

\033[1;34mOptions spécifiques aux listes:\033[0m

  • \033[0;34m--list\033[0m \033[0;34mshopping\033[0m                             : \033[0;90mSpécifier la liste de courses (obligatoire)\033[0m
  • \033[0;34m--list\033[0m \033[0;34mtodo\033[0m                                 : \033[0;90mSpécifier la liste de tâches (obligatoire)\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mlists\033[0m \033[0;34m--list\033[0m \033[0;34mshopping\033[0m \033[1;34madd\033[0m \033[0;33m"Pain"\033[0m
  \033[1;90malexa\033[0m \033[1;32mlists\033[0m \033[0;34m--list\033[0m \033[0;34mtodo\033[0m \033[1;34madd\033[0m \033[0;33m"Réviser Python"\033[0m \033[0;34m--priority\033[0m \033[0;34mhigh\033[0m \033[0;34m--due-date\033[0m \033[0;34m2025-10-15\033[0m
  \033[1;90malexa\033[0m \033[1;32mlists\033[0m \033[0;34m--list\033[0m \033[0;34mshopping\033[0m \033[1;34mremove\033[0m \033[0;33m"Pain"\033[0m
  \033[1;90malexa\033[0m \033[1;32mlists\033[0m \033[0;34m--list\033[0m \033[0;34mshopping\033[0m \033[1;34mclear\033[0m
  \033[1;90malexa\033[0m \033[1;32mlists\033[0m \033[0;34m--list\033[0m \033[0;34mshopping\033[0m \033[1;34mclear\033[0m \033[0;34m--force\033[0m

  \033[1;90mGestion des tâches :\033[0m

  \033[1;90malexa\033[0m \033[1;32mlists\033[0m \033[0;34m--list\033[0m \033[0;34mtodo\033[0m \033[1;34madd\033[0m \033[0;33m"Réviser Python"\033[0m
  \033[1;90malexa\033[0m \033[1;32mlists\033[0m \033[0;34m--list\033[0m \033[0;34mtodo\033[0m \033[1;34mremove\033[0m \033[0;33m"Réviser Python"\033[0m

  \033[1;90mUtilisation avec différents appareils :\033[0m

  \033[1;90malexa\033[0m \033[1;32mlists\033[0m \033[0;36m--device\033[0m \033[0;36m"Salon Echo"\033[0m \033[0;34m--list\033[0m \033[0;34mshopping\033[0m \033[1;34madd\033[0m \033[0;33m"Pain"\033[0m
  \033[1;90malexa\033[0m \033[1;32mlists\033[0m \033[0;36m--device\033[0m \033[0;36m"Cuisine"\033[0m \033[0;34m--list\033[0m \033[0;34mshopping\033[0m \033[1;34mremove\033[0m \033[0;33m"Pain"\033[0m
  \033[1;90malexa\033[0m \033[1;32mlists\033[0m \033[0;36m--device\033[0m \033[0;36m"Chambre"\033[0m \033[0;34m--list\033[0m \033[0;34mshopping\033[0m \033[1;34mclear\033[0m

  \033[1;90mAvec une option globale :\033[0m

  \033[1;90malexa\033[0m \033[1;35m--verbose\033[0m \033[1;32mlists\033[0m \033[0;34m--list\033[0m \033[0;34mshopping\033[0m \033[1;34madd\033[0m \033[0;33m"Pain"\033[0m
  \033[1;90malexa\033[0m \033[1;35m--debug\033[0m \033[1;32mlists\033[0m \033[0;34m--list\033[0m \033[0;34mtodo\033[0m \033[1;34mremove\033[0m \033[0;33m"Tâche"\033[0m

\033[0;90mPour plus de détails:\033[0m \033[1;36malexa lists --help-web\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Placeholders pour compatibilité avec le code existant
ADD_HELP = "Voir aide principale: alexa lists -h"
LIST_HELP = "Voir aide principale: alexa lists -h"
COMPLETE_HELP = "Voir aide principale: alexa lists -h"
REMOVE_HELP = "Voir aide principale: alexa lists -h"
CLEAR_HELP = "Voir aide principale: alexa lists -h"
