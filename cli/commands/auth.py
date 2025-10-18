"""
Commandes d'authentification pour la CLI Alexa Voice Control.

Ce module gère toutes les opérations liées à l'authentification:
- create: Créer une nouvelle session d'authentification
- delete: Supprimer les cookies d'authentification
- status: Vérifier l'état de connexion

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
from pathlib import Path

from cli.base_command import BaseCommand
from cli.command_parser import UniversalHelpFormatter
from core.state_machine import ConnectionState

# Constantes de description simplifiées
AUTH_DESCRIPTION = "Gérer l'authentification Alexa."
CREATE_HELP = "Créer une nouvelle session d'authentification."
STATUS_HELP = "Vérifier l'état de connexion."


class AuthCommand(BaseCommand):
    """
    Commande d'authentification Alexa.

    G…re la cr…ation et v…rification de l'authentification.

    Actions:
        - create: Cr…er une nouvelle session d'authentification
        - status: V…rifier l'…tat de connexion

    Example:
        >>> python alexa.py auth create
        >>> python alexa.py auth status
    """

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes d'authentification.

        Args:
            parser: Sous-parser pour la cat…gorie 'auth'
        """
        # Utiliser le formatter universel pour l'ordre exact demand…
        parser.formatter_class = UniversalHelpFormatter

        # Description r…organis…e dans l'ordre demand… :
        # Titre ? Usage ? Options ? Actions ? Options d'action ? Exemples
        parser.description = AUTH_DESCRIPTION

        # Supprimer l'usage automatique d'argparse
        # (la section Usage est fournie dans la description)
        parser.usage = argparse.SUPPRESS

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action … ex…cuter",
            required=True,
        )

        # Action: create
        create_parser = subparsers.add_parser(
            "create",
            help="Cr…er une nouvelle session d'authentification",
            description=CREATE_HELP,
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )
        create_parser.add_argument(
            "--force",
            action="store_true",
            help="Forcer une nouvelle connexion m…me si d…j… connect…",
        )
        create_parser.add_argument(
            "--amazon",
            type=str,
            default="amazon.fr",
            help="Domaine Amazon … utiliser (ex: amazon.fr, amazon.de)",
        )
        create_parser.add_argument(
            "--language",
            type=str,
            default="fr-FR",
            help="Langue … utiliser (ex: fr-FR, de-DE)",
        )

        # Action: status
        subparsers.add_parser(
            "status",
            help="V…rifier l'…tat de connexion",
            description=STATUS_HELP,
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Ex…cute la commande d'authentification.

        Args:
            args: Arguments pars…s

        Returns:
            True si succ…s, False sinon
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
        Cr…e une nouvelle session d'authentification.

        Args:
            args: Arguments (force)

        Returns:
            True si succ…s
        """
        try:
            # G…rer les cookies existants selon l'option --force
            force = getattr(args, "force", False)
            if force:
                # Supprimer les cookies existants si --force est sp…cifi…
                self._delete_existing_cookies()
            else:
                # V…rifier s'il y a des cookies valides sans --force
                if self._has_valid_cookies():
                    # Afficher le status d'abord
                    self._status(args)
                    # Puis le message d'avertissement
                    print("\033[1;33m??  Session d'authentification d…j… active\033[0m")
                    print()
                    print("\033[1;30m?? Pour forcer une nouvelle authentification:\033[0m")
                    print("   \033[1;36malexa auth create --force\033[0m")
                    print()
                    return True  # Retourner True car ce n'est pas une erreur

            # V…rifications pr…alables compl…tes
            if not self._check_prerequisites():
                return False

            # Import des modules d'auth (uniquement si n…cessaire)
            from alexa_auth.alexa_cookie_retriever import get_alexa_cookies

            # Obtenir le contexte requis (narrow Optional)
            ctx = self.require_context()

            # Transition state machine seulement si pas d…j… connect…
            if ctx.state_machine.state != ConnectionState.AUTHENTICATED:
                ctx.state_machine.connect()

            # Lancer le processus d'authentification Node.js
            self.logger.info("?? D…marrage du processus d'authentification...")
            self.logger.info("?? Connexion au service Amazon Alexa...")

            # R…cup…rer la configuration r…gionale (arguments CLI avec valeurs par d…faut)
            amazon_domain = args.amazon
            language = args.language

            success = get_alexa_cookies(amazon_domain=amazon_domain, language=language)

            if success:
                if ctx.state_machine.state != ConnectionState.AUTHENTICATED:
                    ctx.state_machine.on_connected()
                self.logger.success("? Session cr……e avec succ…s !")
                self.logger.info("?? Les cookies ont …t… sauvegard…s dans alexa_auth/data/")

                # Invalider le cache d'auth pour forcer rechargement
                if ctx.cache_service:
                    ctx.cache_service.invalidate("auth_data")
                    self.logger.debug("??? Cache auth invalid… apr…s cr…ation")

                return True
            else:
                if self.state_machine:
                    self.state_machine.error()
                self.logger.error("? …chec de la cr…ation de session")
                print("? …chec de la cr…ation de session")
                return False

        except Exception as e:
            self.logger.exception("?? Erreur lors de la cr…ation de session")
            if self.state_machine:
                self.state_machine.error()
            self.logger.error(f"? Erreur: {e}")
            return False

    def _status(self, args: argparse.Namespace) -> bool:
        """
        Affiche le statut de connexion.

        Args:
            args: Arguments (utilise l'option globale verbose si d…finie)

        Returns:
            True toujours (ne peut pas …chouer)
        """
        self.logger.info("??  …tat de connexion")
        print()

        # Obtenir le contexte requis pour acc…der aux services
        try:
            ctx = self.require_context()
        except RuntimeError:
            # Si aucun contexte, afficher un …tat g…n…rique
            state_name = "UNKNOWN"
            can_execute = False
        else:
            # …tat de la state machine
            state_name = ctx.state_machine.state.name if ctx.state_machine else "UNKNOWN"
            can_execute = ctx.state_machine.can_execute_commands if ctx.state_machine else False

        # Affichage avec couleurs et style am…lior…
        print("\033[1;4;30m?? …TAT DE CONNEXION\033[0m")  # Gris gras soulign… avec emoji
        print()

        # Colorer l'…tat en vert si authentifi…
        state_display = "\033[32mAUTHENTICATED\033[0m" if state_name == "AUTHENTICATED" else state_name
        cmd_status = "\033[32mOui\033[0m" if can_execute else "\033[31mNon\033[0m"
        print(f"\033[1;30m  …tat\033[0m                         {state_display}")
        print(f"\033[1;30m  Peut ex…cuter commandes\033[0m      {cmd_status}")

        # V…rifier existence des fichiers
        auth_data_dir = Path("alexa_auth/data")
        cookie_file = auth_data_dir / "cookie.txt"
        cookie_json = auth_data_dir / "cookie-resultat.json"

        cookie_txt_exists = cookie_file.exists()
        cookie_txt_status = "\033[32mPr…sent\033[0m" if cookie_txt_exists else "\033[31mManquant\033[0m"
        print(f"\033[1;30m  Fichier cookie.txt\033[0m           {cookie_txt_status}")

        cookie_json_exists = cookie_json.exists()
        cookie_json_status = "\033[32mPr…sent\033[0m" if cookie_json_exists else "\033[31mManquant\033[0m"
        print(f"\033[1;30m  Fichier cookie-resultat.json\033[0m {cookie_json_status}")

        # Afficher les infos du cookie m…me sans --verbose
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

                # Date de cr…ation et …ge
                token_date = None
                if "recapitulatif" in data and "tokenDate" in data["recapitulatif"]:
                    token_date = data["recapitulatif"]["tokenDate"]
                elif "donneesCompletes" in data and "tokenDate" in data["donneesCompletes"]:
                    token_date = data["donneesCompletes"]["tokenDate"]

                if token_date:
                    dt = datetime.fromtimestamp(token_date / 1000)  # Convertir ms en s
                    date_str = dt.strftime("%d/%m/%Y %H:%M:%S")

                    # Calculer l'…ge
                    age_seconds = (datetime.now() - dt).total_seconds()
                    if age_seconds < 3600:
                        age_str = f"{int(age_seconds / 60)} minutes"
                    elif age_seconds < 86400:
                        age_str = f"{int(age_seconds / 3600)} heures"
                    else:
                        age_str = f"{int(age_seconds / 86400)} jours"

                    print(f"\033[1;30m  Date de cr…ation\033[0m             {date_str}")
                    print(f"\033[1;30m  …ge du cookie\033[0m                {age_str}")

                # CSRF token (juste indiquer pr…sence)
                if "recapitulatif" in data and "csrf" in data["recapitulatif"]:
                    csrf_status = "\033[32mPr…sent\033[0m"
                    print(f"\033[1;30m  CSRF token\033[0m                   {csrf_status}")

            except Exception as e:
                self.logger.debug(f"Erreur lecture cookie-resultat.json: {e}")

        # Utiliser l'option globale --verbose si elle existe
        verbose = getattr(args, "verbose", False)
        if verbose:
            print()
            print(f"\033[1;30m  R…pertoire auth\033[0m              {auth_data_dir}")

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
            print("\n?? Utilisez 'alexa auth create' pour cr…er une session")

        print()
        return True

    def _has_valid_cookies(self) -> bool:
        """
        V…rifie si des cookies valides existent d…j….

        Returns:
            True si des cookies valides sont pr…sents
        """
        import json
        from pathlib import Path

        cookie_file = Path("alexa_auth/data/cookie-resultat.json")

        if not cookie_file.exists():
            self.logger.debug("?? Aucun fichier de cookie trouv…")
            return False

        try:
            with open(cookie_file, encoding="utf-8") as f:
                data = json.load(f)

            # V…rifier la pr…sence des donn…es essentielles
            recap = data.get("recapitulatif", {})
            if not recap.get("cookie") or not recap.get("csrf"):
                self.logger.debug("?? Cookie en cache incomplet")
                return False

            self.logger.debug("? Cookies valides trouv…s")
            return True

        except Exception as e:
            self.logger.debug(f"? Erreur lors de la v…rification du cache: {e}")
            return False

    def _delete_existing_cookies(self) -> None:
        """
        Supprime les cookies existants avant de cr…er de nouveaux.
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
                self.logger.debug(f"??? Cookie supprim…: {file_path}")
                deleted_count += 1

        if deleted_count > 0:
            self.logger.info(f"??? {deleted_count} cookie(s) existant(s) supprim…(s)")
        else:
            self.logger.debug("?? Aucun cookie existant … supprimer")

    def _check_prerequisites(self) -> bool:
        """
        V…rifie tous les pr…requis avant l'authentification.

        Returns:
            True si tous les pr…requis sont OK
        """
        from typing import List

        issues_found: List[str] = []

        # 1. V…rifier l'environnement virtuel Python
        if not self._check_python_venv():
            issues_found.append("python_venv")

        # 2. V…rifier Node.js
        if not self._check_nodejs():
            issues_found.append("nodejs")

        # 3. V…rifier les d…pendances npm
        if not self._check_npm_dependencies():
            issues_found.append("npm_deps")

        # 4. V…rifier les fichiers requis
        if not self._check_required_files():
            issues_found.append("required_files")

        if issues_found:
            self._show_installation_instructions(issues_found)
            return False

        self.logger.success("? Tous les pr…requis v…rifi…s")
        return True

    def _check_python_venv(self) -> bool:
        """V…rifie si l'environnement virtuel Python est activ…"""
        import sys

        # V…rifier si on est dans un venv
        in_venv = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)

        if not in_venv:
            return False

        # V…rifier que les packages requis sont install…s
        # Tester la disponibilit… des modules sans importer des symboles inutilis…s
        import importlib.util

        nodeenv_spec = importlib.util.find_spec("nodeenv")
        requests_spec = importlib.util.find_spec("requests")

        # Retourner directement l'existence conjointe des modules
        return nodeenv_spec is not None and requests_spec is not None

    def _check_nodejs(self) -> bool:
        """V…rifie si Node.js est install… via nodeenv"""
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
        """V…rifie si les d…pendances npm sont install…es"""
        from pathlib import Path

        script_dir = Path("alexa_auth/nodejs")
        node_modules = script_dir / "node_modules"

        if not node_modules.exists():
            return False

        # V…rifier quelques packages cl…s
        required_packages = ["alexa-cookie2", "yargs"]
        return all((node_modules / package).exists() for package in required_packages)

    def _check_required_files(self) -> bool:
        """V…rifie si les fichiers requis existent"""
        from pathlib import Path

        required_files = [
            "alexa_auth/nodejs/package.json",
            "alexa_auth/nodejs/alexa-cookie-lib.js",
            "alexa_auth/nodejs/auth-initial.js",
        ]

        return all(Path(file_path).exists() for file_path in required_files)

    def _show_installation_instructions(self, issues):
        """Affiche les instructions d'installation selon les probl…mes d…tect…s"""
        import sys

        self.logger.error("?? Pr…requis manquants d…tect…s")
        self.logger.info("")
        self.logger.info("Probl…mes identifi…s:")

        for issue in issues:
            if issue == "python_venv":
                self.logger.info("  Environnement virtuel Python non activ… ou packages manquants")
            elif issue == "nodejs":
                self.logger.info("  Node.js non install… via nodeenv")
            elif issue == "npm_deps":
                self.logger.info("  D…pendances npm non install…es")
            elif issue == "required_files":
                self.logger.info("  Fichiers requis manquants")

        self.logger.info("")
        self.logger.info("Instructions d'installation:")

        if sys.platform == "win32":
            # Instructions Windows
            self.logger.info("")
            self.logger.info("  Installation compl…te (recommand…):")
            self.logger.info("     scripts\\install.ps1")
            self.logger.info("")
            self.logger.info("  Installation manuelle:")
            self.logger.info("     1. Cr…er/activer le venv Python:")
            self.logger.info("        scripts\\venv_manager.bat create")
            self.logger.info("        scripts\\venv_manager.bat activate")
            self.logger.info("")
            self.logger.info("     2. Installer Node.js et d…pendances:")
            self.logger.info("        python scripts\\install.py")
        else:
            # Instructions Unix/Linux/macOS
            self.logger.info("")
            self.logger.info("  Installation compl…te (recommand…):")
            self.logger.info("     bash scripts/install.sh")
            self.logger.info("")
            self.logger.info("  Installation manuelle:")
            self.logger.info("     1. Cr…er/activer le venv Python:")
            self.logger.info("        bash scripts/venv_manager.sh create")
            self.logger.info("        source scripts/venv_manager.sh activate")
            self.logger.info("")
            self.logger.info("     2. Installer Node.js et d…pendances:")
            self.logger.info("        python scripts/install.py")

        self.logger.info("")
        self.logger.info("  Puis relancer l'authentification:")
        self.logger.info("     python alexa auth create")
        self.logger.info("")
        self.logger.info("Conseil: Utilisez l'installation compl…te pour …viter les probl…mes")
