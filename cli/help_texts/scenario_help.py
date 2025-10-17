"""
Aide simplifiée pour la catégorie SCENARIO.
"""

# ruff: noqa: E501

SCENARIO_DESCRIPTION = """\
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mscenario\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34mlist    \033[0m : \033[0;90mLister les scénarios\033[0m
  • \033[1;34mcreate  \033[0m : \033[0;90mCréer un scénario\033[0m
  • \033[1;34mrun     \033[0m : \033[0;90mExécuter un scénario\033[0m
  • \033[1;34mdelete  \033[0m : \033[0;90mSupprimer un scénario\033[0m
  • \033[1;34mshow    \033[0m : \033[0;90mAfficher détails d'un scénario\033[0m
  • \033[1;34medit    \033[0m : \033[0;90mÉditer les actions d'un scénario\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mscenario\033[0m \033[1;34mlist\033[0m
  \033[1;90malexa\033[0m \033[1;32mscenario\033[0m \033[1;34mcreate --name "Ambiance" --actions '[...]'\033[0m
  \033[1;90malexa\033[0m \033[1;32mscenario\033[0m \033[1;34mrun --name "Ambiance"\033[0m

\033[0;90mPour plus de détails:\033[0m \033[1;36malexa scenario --help-web\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Placeholders pour compatibilité avec le code existant
CREATE_HELP = "Voir aide principale: alexa scenario -h"
DELETE_HELP = "Voir aide principale: alexa scenario -h"
EDIT_HELP = "Voir aide principale: alexa scenario -h"
INFO_HELP = "Voir aide principale: alexa scenario -h"
LIST_HELP = "Voir aide principale: alexa scenario -h"
RUN_HELP = "Voir aide principale: alexa scenario -h"
