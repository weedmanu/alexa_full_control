# noqa: E501
# ruff: noqa: E501
"""Aide simplifiée pour la catégorie ALARM.

\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32malarm\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34mcreate   \033[0m : \033[0;90mCréer une nouvelle alarme\033[0m
  • \033[1;34mlist     \033[0m : \033[0;90mLister toutes les alarmes\033[0m
  • \033[1;34mdelete   \033[0m : \033[0;90mSupprimer une alarme\033[0m
  • \033[1;34mupdate   \033[0m : \033[0;90mModifier une alarme existante\033[0m
  • \033[1;34menable   \033[0m : \033[0;90mActiver une alarme\033[0m
  • \033[1;34mdisable  \033[0m : \033[0;90mDésactiver une alarme\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32malarm\033[0m \033[1;34mcreate -d "Chambre" --time 07:30 --label "Réveil"\033[0m
  \033[1;90malexa\033[0m \033[1;32malarm\033[0m \033[1;34mlist -d "Chambre"\033[0m
  \033[1;90malexa\033[0m \033[1;32malarm\033[0m \033[1;34mdelete -d "Chambre" --id <alarm_id>\033[0m
  \033[1;90malexa\033[0m \033[1;32malarm\033[0m \033[1;34menable -d "Chambre" --id <alarm_id>\033[0m

\033[0;90mPour plus de détails:\033[0m \033[1;36malexa alarm --help-web\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Description courte utilisée par le parser
ALARM_DESCRIPTION = "Aide pour la catégorie 'alarm' — création, liste, suppression et gestion des alarmes."

# Placeholders pour compatibilité avec le code existant
CREATE_HELP = "Voir aide principale: alexa alarm -h"
DELETE_HELP = "Voir aide principale: alexa alarm -h"
DISABLE_HELP = "Voir aide principale: alexa alarm -h"
ENABLE_HELP = "Voir aide principale: alexa alarm -h"
LIST_HELP = "Voir aide principale: alexa alarm -h"
UPDATE_HELP = "Voir aide principale: alexa alarm -h"
