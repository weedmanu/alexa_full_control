"""
Aide simplifiée pour la catégorie REMINDER.
"""

REMINDER_DESCRIPTION = """\
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mreminder\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34mlist      \033[0m : \033[0;90mLister les rappels\033[0m
  • \033[1;34mcreate    \033[0m : \033[0;90mCréer un rappel\033[0m
  • \033[1;34mdelete    \033[0m : \033[0;90mSupprimer un rappel\033[0m
  • \033[1;34mcomplete  \033[0m : \033[0;90mMarquer un rappel comme terminé\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mreminder\033[0m \033[1;34mlist\033[0m
  \033[1;90malexa\033[0m \033[1;32mreminder\033[0m \033[1;34mcreate -d "Salon" --label "Réunion" --datetime "2025-10-08 14:00"\033[0m
  \033[1;90malexa\033[0m \033[1;32mreminder\033[0m \033[1;34mdelete --id <reminder_id>\033[0m
  \033[1;90malexa\033[0m \033[1;32mreminder\033[0m \033[1;34mcomplete --id <reminder_id>\033[0m

\033[0;90mPour plus de détails:\033[0m \033[1;36malexa reminder --help-web\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Placeholders pour compatibilité avec le code existant
COMPLETE_HELP = "Voir aide principale: alexa reminder -h"
CREATE_HELP = "Voir aide principale: alexa reminder -h"
DELETE_HELP = "Voir aide principale: alexa reminder -h"
LIST_HELP = "Voir aide principale: alexa reminder -h"
