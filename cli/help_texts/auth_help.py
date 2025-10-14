"""
Aide simplifiée pour la catégorie AUTH.
"""

AUTH_DESCRIPTION = """\
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
\033[1;90mUsage:\033[0m

  \033[1;90malexa\033[0m \033[1;35m[OPTIONS_GLOBALES]\033[0m \033[1;32mauth\033[0m \033[1;34m<ACTION>\033[0m \033[0;34m[OPTIONS_ACTION]\033[0m

\033[1;34mActions et options disponibles:\033[0m

  • \033[1;34mcreate          \033[0m : \033[0;90mCréer une nouvelle session d'authentification\033[0m
  • \033[1;34mcreate --force  \033[0m : \033[0;90mForcer une nouvelle connexion même si un token est déjà présent\033[0m
  • \033[1;34mstatus          \033[0m : \033[0;90mVérifier l'état de connexion\033[0m

\033[1;90mExemples:\033[0m

  \033[1;90malexa\033[0m \033[1;32mauth\033[0m \033[1;34mcreate\033[0m
  \033[1;90malexa\033[0m \033[1;32mauth\033[0m \033[1;34mcreate --force\033[0m
  \033[1;90malexa\033[0m \033[1;32mauth\033[0m \033[1;34mstatus\033[0m

  \033[1;90mAvec une option globale :\033[0m

  \033[1;90malexa\033[0m \033[1;35m--verbose\033[0m \033[1;32mauth\033[0m \033[1;34mstatus\033[0m
  \033[1;90malexa\033[0m \033[1;35m--debug\033[0m \033[1;32mauth\033[0m \033[1;34mcreate\033[0m

\033[0;90mPour plus de détails:\033[0m \033[1;36malexa auth --help-web\033[0m
\033[1;30m──────────────────────────────────────────────────────────────────────\033[0m
"""

# Placeholders pour compatibilité avec le code existant
CREATE_HELP = "Voir aide principale: alexa auth -h"
STATUS_HELP = "Voir aide principale: alexa auth -h"
