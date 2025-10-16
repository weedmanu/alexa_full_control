"""
Commandes d'authentification pour la CLI Alexa Voice Control.

Ce module gÃ¨re toutes les opÃ©rations liÃ©es Ã  l'authentification:
- create: CrÃ©er une nouvelle session d'authentification
- delete: Supprimer les cookies d'authentification
- status: VÃ©rifier l'Ã©tat de connexion

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
from pathlib import Path

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter
from core.state_machine import ConnectionState

# Constantes de description simplifiÃ©es
AUTH_DESCRIPTION = "GÃ©rer l'authentification Alexa"
CREATE_HELP = "CrÃ©er une nouvelle session d'authentification"
STATUS_HELP = "VÃ©rifier l'Ã©tat de connexion"


class AuthCommand(BaseCommand):
    """
    Commande d'authentification Alexa.

    GÃ¨re la crÃ©ation et vÃ©rification de l'authentification.

    Actions:
        - create: CrÃ©er une nouvelle session d'authentification
        - status: VÃ©rifier l'Ã©tat de connexion

    Example:
        >>> python alexa.py auth create
        >>> python alexa.py auth status
    """

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes d'authentification.

        Args:
            parser: Sous-parser pour la catÃ©gorie 'auth'
        """
        # Utiliser le formatter universel pour l'ordre exact demandÃ©
        parser.formatter_class = UniversalHelpFormatter

        # Description rÃ©organisÃ©e dans l'ordre demandÃ© :
        # Titre â†’ Usage â†’ Options â†’ Actions â†’ Options d'action â†’ Exemples
        parser.description = AUTH_DESCRIPTION

        # Supprimer l'usage automatique d'argparse
        # (la section Usage est fournie dans la description)
        parser.usage = argparse.SUPPRESS

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action Ã  exÃ©cuter",
            required=True,
        )

        # Action: create
        create_parser = subparsers.add_parser(
            "create",
            help="CrÃ©er une nouvelle session d'authentification",
            description=CREATE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        create_parser.add_argument(
            "--force",
            action="store_true",
            help="Forcer une nouvelle connexion mÃªme si dÃ©jÃ  connectÃ©",
        )
        create_parser.add_argument(
            "--amazon",
            type=str,
            default="amazon.fr",
            help="Domaine Amazon Ã  utiliser (ex: amazon.fr, amazon.de)",
        )
        create_parser.add_argument(
            "--language",
            type=str,
            default="fr-FR",
            help="Langue Ã  utiliser (ex: fr-FR, de-DE)",
        )

        # Action: status
        subparsers.add_parser(
            "status",
            help="VÃ©rifier l'Ã©tat de connexion",
            description=STATUS_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        ExÃ©cute la commande d'authentification.

        Args:
            args: Arguments parsÃ©s

        Returns:
            True si succÃ¨s, False sinon
        """
        if args.action == "create":
            return self._create(args)
        elif args.action == "status":
            return self._status(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _create(self, args: argparse.Namespace) -> bool:
        """
        CrÃ©e une nouvelle session d'authentification.

        Args:
            args: Arguments (force)

        Returns:
            True si succÃ¨s
        """
        try:
            # GÃ©rer les cookies existants selon l'option --force
            force = getattr(args, "force", False)
            if force:
                # Supprimer les cookies existants si --force est spÃ©cifiÃ©
                self._delete_existing_cookies()
            else:
                # VÃ©rifier s'il y a des cookies valides sans --force
                if self._has_valid_cookies():
                    # Afficher le status d'abord
                    self._status(args)
                    # Puis le message d'avertissement
                    print("\033[1;33mâš ï¸  Session d'authentification dÃ©jÃ  active\033[0m")
                    print()
                    print("\033[1;30mðŸ’¡ Pour forcer une nouvelle authentification:\033[0m")
                    print("   \033[1;36malexa auth create --force\033[0m")
                    print()
                    return True  # Retourner True car ce n'est pas une erreur

            # VÃ©rifications prÃ©alables complÃ¨tes
            if not self._check_prerequisites():
                return False

            # Import des modules d'auth (uniquement si nÃ©cessaire)
            from alexa_auth.alexa_cookie_retriever import get_alexa_cookies

            # Obtenir le contexte requis (narrow Optional)
            ctx = self.require_context()

            # Transition state machine seulement si pas dÃ©jÃ  connectÃ©
            if ctx.state_machine.state != ConnectionState.AUTHENTICATED:
                ctx.state_machine.connect()

            # Lancer le processus d'authentification Node.js
            self.logger.info("ðŸ”„ DÃ©marrage du processus d'authentification...")
            self.logger.info("ðŸŒ Connexion au service Amazon Alexa...")

            # RÃ©cupÃ©rer la configuration rÃ©gionale (arguments CLI avec valeurs par dÃ©faut)
            amazon_domain = args.amazon
            language = args.language

            success = get_alexa_cookies(amazon_domain=amazon_domain, language=language)

            if success:
                if ctx.state_machine.state != ConnectionState.AUTHENTICATED:
                    ctx.state_machine.on_connected()
                self.logger.success("âœ… Session crÃ©Ã©e avec succÃ¨s !")
                self.logger.info("ðŸ’¾ Les cookies ont Ã©tÃ© sauvegardÃ©s dans alexa_auth/data/")

                # Invalider le cache d'auth pour forcer rechargement
                if ctx.cache_service:
                    ctx.cache_service.invalidate("auth_data")
                    self.logger.debug("ðŸ—‘ï¸ Cache auth invalidÃ© aprÃ¨s crÃ©ation")

                return True
            else:
                if self.state_machine:
                    self.state_machine.error()
                self.logger.error("âŒ Ã‰chec de la crÃ©ation de session")
                print("âŒ Ã‰chec de la crÃ©ation de session")
                return False

        except Exception as e:
            self.logger.exception("ðŸ’¥ Erreur lors de la crÃ©ation de session")
            if self.state_machine:
                self.state_machine.error()
            self.logger.error(f"âŒ Erreur: {e}")
            return False

    def _status(self, args: argparse.Namespace) -> bool:
        """
        Affiche le statut de connexion.

        Args:
            args: Arguments (utilise l'option globale verbose si dÃ©finie)

        Returns:
            True toujours (ne peut pas Ã©chouer)
        """
        self.logger.info("â„¹ï¸  Ã‰tat de connexion")
        print()

        # Obtenir le contexte requis pour accÃ©der aux services
        try:
            ctx = self.require_context()
        except RuntimeError:
            # Si aucun contexte, afficher un Ã©tat gÃ©nÃ©rique
            state_name = "UNKNOWN"
            can_execute = False
        else:
            # Ã‰tat de la state machine
            state_name = ctx.state_machine.state.name if ctx.state_machine else "UNKNOWN"
            can_execute = ctx.state_machine.can_execute_commands if ctx.state_machine else False

        # Affichage avec couleurs et style amÃ©liorÃ©
        print("\033[1;4;30mðŸ” Ã‰TAT DE CONNEXION\033[0m")  # Gris gras soulignÃ© avec emoji
        print()

        # Colorer l'Ã©tat en vert si authentifiÃ©
        state_display = "\033[32mAUTHENTICATED\033[0m" if state_name == "AUTHENTICATED" else state_name
        cmd_status = "\033[32mOui\033[0m" if can_execute else "\033[31mNon\033[0m"
        print(f"\033[1;30m  Ã‰tat\033[0m                         {state_display}")
        print(f"\033[1;30m  Peut exÃ©cuter commandes\033[0m      {cmd_status}")

        # VÃ©rifier existence des fichiers
        auth_data_dir = Path("alexa_auth/data")
        cookie_file = auth_data_dir / "cookie.txt"
        cookie_json = auth_data_dir / "cookie-resultat.json"

        cookie_txt_exists = cookie_file.exists()
        cookie_txt_status = "\033[32mPrÃ©sent\033[0m" if cookie_txt_exists else "\033[31mManquant\033[0m"
        print(f"\033[1;30m  Fichier cookie.txt\033[0m           {cookie_txt_status}")

        cookie_json_exists = cookie_json.exists()
        cookie_json_status = "\033[32mPrÃ©sent\033[0m" if cookie_json_exists else "\033[31mManquant\033[0m"
        print(f"\033[1;30m  Fichier cookie-resultat.json\033[0m {cookie_json_status}")

        # Afficher les infos du cookie mÃªme sans --verbose
        if cookie_json_exists:
            try:
                import json
                from datetime import datetime

                with open(cookie_json, encoding="utf-8") as f:
                    data = json.load(f)

                # Domaine Amazon
                domain = None
                if "donneesCompletes" in data and "amazonPage" in data["donneesCompletes"]:
                    domain = data["donneesCompletes"]["amazonPage"]
                elif "recapitulatif" in data and "amazonPage" in data["recapitulatif"]:
                    domain = data["recapitulatif"]["amazonPage"]

                if domain:
                    print(f"\033[1;30m  Domaine Amazon\033[0m               {domain}")

                # Date de crÃ©ation et Ã¢ge
                token_date = None
                if "recapitulatif" in data and "tokenDate" in data["recapitulatif"]:
                    token_date = data["recapitulatif"]["tokenDate"]
                elif "donneesCompletes" in data and "tokenDate" in data["donneesCompletes"]:
                    token_date = data["donneesCompletes"]["tokenDate"]

                if token_date:
                    dt = datetime.fromtimestamp(token_date / 1000)  # Convertir ms en s
                    date_str = dt.strftime("%d/%m/%Y %H:%M:%S")

                    # Calculer l'Ã¢ge
                    age_seconds = (datetime.now() - dt).total_seconds()
                    if age_seconds < 3600:
                        age_str = f"{int(age_seconds / 60)} minutes"
                    elif age_seconds < 86400:
                        age_str = f"{int(age_seconds / 3600)} heures"
                    else:
                        age_str = f"{int(age_seconds / 86400)} jours"

                    print(f"\033[1;30m  Date de crÃ©ation\033[0m             {date_str}")
                    print(f"\033[1;30m  Ã‚ge du cookie\033[0m                {age_str}")

                # CSRF token (juste indiquer prÃ©sence)
                if "recapitulatif" in data and "csrf" in data["recapitulatif"]:
                    csrf_status = "\033[32mPrÃ©sent\033[0m"
                    print(f"\033[1;30m  CSRF token\033[0m                   {csrf_status}")

            except Exception as e:
                self.logger.debug(f"Erreur lecture cookie-resultat.json: {e}")

        # Utiliser l'option globale --verbose si elle existe
        verbose = getattr(args, "verbose", False)
        if verbose:
            print()
            print(f"\033[1;30m  RÃ©pertoire auth\033[0m              {auth_data_dir}")

            if cookie_file.exists():
                size = cookie_file.stat().st_size
                size_formatted = f"{size:,}".replace(",", " ")
                print(f"\033[1;30m  Taille cookie.txt\033[0m            {size_formatted} octets")

            if cookie_json.exists():
                size = cookie_json.stat().st_size
                size_formatted = f"{size:,}".replace(",", " ")
                print(f"\033[1;30m  Taille cookie-resultat.json\033[0m  {size_formatted} octets")

        # Recommandation
        if not can_execute:
            print("\nðŸ’¡ Utilisez 'alexa auth create' pour crÃ©er une session")

        print()
        return True

    def _has_valid_cookies(self) -> bool:
        """
        VÃ©rifie si des cookies valides existent dÃ©jÃ .

        Returns:
            True si des cookies valides sont prÃ©sents
        """
        import json
        from pathlib import Path

        cookie_file = Path("alexa_auth/data/cookie-resultat.json")

        if not cookie_file.exists():
            self.logger.debug("ðŸ” Aucun fichier de cookie trouvÃ©")
            return False

        try:
            with open(cookie_file, encoding="utf-8") as f:
                data = json.load(f)

            # VÃ©rifier la prÃ©sence des donnÃ©es essentielles
            recap = data.get("recapitulatif", {})
            if not recap.get("cookie") or not recap.get("csrf"):
                self.logger.debug("âš ï¸ Cookie en cache incomplet")
                return False

            self.logger.debug("âœ… Cookies valides trouvÃ©s")
            return True

        except Exception as e:
            self.logger.debug(f"âŒ Erreur lors de la vÃ©rification du cache: {e}")
            return False

    def _delete_existing_cookies(self) -> None:
        """
        Supprime les cookies existants avant de crÃ©er de nouveaux.
        """
        auth_data_dir = Path("alexa_auth/data")
        files_to_delete = [
            auth_data_dir / "cookie.txt",
            auth_data_dir / "cookie-resultat.json",
            auth_data_dir / "formerDataStore.json",
        ]

        deleted_count = 0
        for file_path in files_to_delete:
            if file_path.exists():
                file_path.unlink()
                self.logger.debug(f"ðŸ—‘ï¸ Cookie supprimÃ©: {file_path}")
                deleted_count += 1

        if deleted_count > 0:
            self.logger.info(f"ðŸ—‘ï¸ {deleted_count} cookie(s) existant(s) supprimÃ©(s)")
        else:
            self.logger.debug("ðŸ” Aucun cookie existant Ã  supprimer")

    def _check_prerequisites(self) -> bool:
        """
        VÃ©rifie tous les prÃ©requis avant l'authentification.

        Returns:
            True si tous les prÃ©requis sont OK
        """
        from typing import List

        issues_found: List[str] = []

        # 1. VÃ©rifier l'environnement virtuel Python
        if not self._check_python_venv():
            issues_found.append("python_venv")

        # 2. VÃ©rifier Node.js
        if not self._check_nodejs():
            issues_found.append("nodejs")

        # 3. VÃ©rifier les dÃ©pendances npm
        if not self._check_npm_dependencies():
            issues_found.append("npm_deps")

        # 4. VÃ©rifier les fichiers requis
        if not self._check_required_files():
            issues_found.append("required_files")

        if issues_found:
            self._show_installation_instructions(issues_found)
            return False

        self.logger.success("âœ… Tous les prÃ©requis vÃ©rifiÃ©s")
        return True

    def _check_python_venv(self) -> bool:
        """VÃ©rifie si l'environnement virtuel Python est activÃ©"""
        import sys

        # VÃ©rifier si on est dans un venv
        in_venv = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)

        if not in_venv:
            return False

        # VÃ©rifier que les packages requis sont installÃ©s
        # Tester la disponibilitÃ© des modules sans importer des symboles inutilisÃ©s
        import importlib.util

        nodeenv_spec = importlib.util.find_spec("nodeenv")
        requests_spec = importlib.util.find_spec("requests")

        # Retourner directement l'existence conjointe des modules
        return nodeenv_spec is not None and requests_spec is not None

    def _check_nodejs(self) -> bool:
        """VÃ©rifie si Node.js est installÃ© via nodeenv"""
        from pathlib import Path

        from alexa_auth.alexa_cookie_retriever import NodeEnvironment

        script_dir = Path("alexa_auth").absolute()
        node_env = NodeEnvironment(script_dir)

        if not node_env.is_installed():
            return False

        # Tester que Node.js fonctionne
        try:
            version = node_env.get_node_version()
            return version is not None and version.startswith("v")
        except Exception:
            return False

    def _check_npm_dependencies(self) -> bool:
        """VÃ©rifie si les dÃ©pendances npm sont installÃ©es"""
        from pathlib import Path

        script_dir = Path("alexa_auth/nodejs")
        node_modules = script_dir / "node_modules"

        if not node_modules.exists():
            return False

        # VÃ©rifier quelques packages clÃ©s
        required_packages = ["alexa-cookie2", "yargs"]
        return all((node_modules / package).exists() for package in required_packages)

    def _check_required_files(self) -> bool:
        """VÃ©rifie si les fichiers requis existent"""
        from pathlib import Path

        required_files = [
            "alexa_auth/nodejs/package.json",
            "alexa_auth/nodejs/alexa-cookie-lib.js",
            "alexa_auth/nodejs/auth-initial.js",
        ]

        return all(Path(file_path).exists() for file_path in required_files)

    def _show_installation_instructions(self, issues):
        """Affiche les instructions d'installation selon les problÃ¨mes dÃ©tectÃ©s"""
        import sys

        self.logger.error("âš ï¸ PrÃ©requis manquants dÃ©tectÃ©s")
        self.logger.info("")
        self.logger.info("ProblÃ¨mes identifiÃ©s:")

        for issue in issues:
            if issue == "python_venv":
                self.logger.info("  Environnement virtuel Python non activÃ© ou packages manquants")
            elif issue == "nodejs":
                self.logger.info("  Node.js non installÃ© via nodeenv")
            elif issue == "npm_deps":
                self.logger.info("  DÃ©pendances npm non installÃ©es")
            elif issue == "required_files":
                self.logger.info("  Fichiers requis manquants")

        self.logger.info("")
        self.logger.info("Instructions d'installation:")

        if sys.platform == "win32":
            # Instructions Windows
            self.logger.info("")
            self.logger.info("  Installation complÃ¨te (recommandÃ©):")
            self.logger.info("     scripts\\install.ps1")
            self.logger.info("")
            self.logger.info("  Installation manuelle:")
            self.logger.info("     1. CrÃ©er/activer le venv Python:")
            self.logger.info("        scripts\\venv_manager.bat create")
            self.logger.info("        scripts\\venv_manager.bat activate")
            self.logger.info("")
            self.logger.info("     2. Installer Node.js et dÃ©pendances:")
            self.logger.info("        python scripts\\install.py")
        else:
            # Instructions Unix/Linux/macOS
            self.logger.info("")
            self.logger.info("  Installation complÃ¨te (recommandÃ©):")
            self.logger.info("     bash scripts/install.sh")
            self.logger.info("")
            self.logger.info("  Installation manuelle:")
            self.logger.info("     1. CrÃ©er/activer le venv Python:")
            self.logger.info("        bash scripts/venv_manager.sh create")
            self.logger.info("        source scripts/venv_manager.sh activate")
            self.logger.info("")
            self.logger.info("     2. Installer Node.js et dÃ©pendances:")
            self.logger.info("        python scripts/install.py")

        self.logger.info("")
        self.logger.info("  Puis relancer l'authentification:")
        self.logger.info("     python alexa auth create")
        self.logger.info("")
        self.logger.info("Conseil: Utilisez l'installation complÃ¨te pour Ã©viter les problÃ¨mes")

