"""
Aide simplifiée pour la catégorie MULTIROOM.
"""

MULTIROOM_DESCRIPTION = """\
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mmultiroom\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34mlist    \033[0m : \033[0;90mLister les groupes multiroom\033[0m
  • \033[1;34mcreate  \033[0m : \033[0;90mCréer un groupe multiroom\033[0m
  • \033[1;34mdelete  \033[0m : \033[0;90mSupprimer un groupe multiroom\033[0m
  • \033[1;34minfo    \033[0m : \033[0;90mAfficher les détails d'un groupe\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mmultiroom\033[0m \033[1;34mlist\033[0m
  \033[1;90malexa\033[0m \033[1;32mmultiroom\033[0m \033[1;34mcreate --name "Maison" --devices "Salon,Cuisine"\033[0m
  \033[1;90malexa\033[0m \033[1;32mmultiroom\033[0m \033[1;34mdelete <group_id>\033[0m

\033[0;90mPour plus de détails:\033[0m \033[1;36malexa multiroom --help-web\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Placeholders pour compatibilité avec le code existant
CREATE_HELP = "Voir aide principale: alexa multiroom -h"
DELETE_HELP = "Voir aide principale: alexa multiroom -h"
INFO_HELP = "Voir aide principale: alexa multiroom -h"
LIST_HELP = "Voir aide principale: alexa multiroom -h"
