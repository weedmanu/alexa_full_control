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
from cli.command_parser import UniversalHelpFormatter, ActionHelpFormatter
from cli.help_texts.auth_help import (
    AUTH_DESCRIPTION,
    CREATE_HELP,
    STATUS_HELP,
)
from core.state_machine import ConnectionState


class AuthCommand(BaseCommand):
    """
    Commande d'authentification Alexa.

    Gère la création et vérification de l'authentification.

    Actions:
        - create: Créer une nouvelle session d'authentification
        - status: Vérifier l'état de connexion

    Example:
        >>> python alexa.py auth create
        >>> python alexa.py auth status
    """

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes d'authentification.

        Args:
            parser: Sous-parser pour la catégorie 'auth'
        """
        # Utiliser le formatter universel pour l'ordre exact demandé
        parser.formatter_class = UniversalHelpFormatter

        # Description réorganisée dans l'ordre demandé : Titre → Usage → Options → Actions → Options d'action → Exemples
        parser.description = AUTH_DESCRIPTION

        # Supprimer l'usage automatique d'argparse (on a notre propre section Usage dans la description)
        parser.usage = argparse.SUPPRESS

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        # Action: create
        create_parser = subparsers.add_parser(
            "create",
            help="Créer une nouvelle session d'authentification",
            description=CREATE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        create_parser.add_argument(
            "--force",
            action="store_true",
            help="Forcer une nouvelle connexion même si déjà connecté",
        )
        create_parser.add_argument(
            "--amazon",
            type=str,
            default="amazon.fr",
            help="Domaine Amazon à utiliser (ex: amazon.fr, amazon.de)",
        )
        create_parser.add_argument(
            "--language",
            type=str,
            default="fr-FR",
            help="Langue à utiliser (ex: fr-FR, de-DE)",
        )

        # Action: status
        status_parser = subparsers.add_parser(
            "status",
            help="Vérifier l'état de connexion",
            description=STATUS_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande d'authentification.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
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
        Crée une nouvelle session d'authentification.

        Args:
            args: Arguments (force)

        Returns:
            True si succès
        """
        try:
            # Gérer les cookies existants selon l'option --force
            force = getattr(args, 'force', False)
            if force:
                # Supprimer les cookies existants si --force est spécifié
                self._delete_existing_cookies()
            else:
                # Vérifier s'il y a des cookies valides sans --force
                if self._has_valid_cookies():
                    # Afficher le status d'abord
                    self._status(args)
                    # Puis le message d'avertissement
                    print("\033[1;33m⚠️  Session d'authentification déjà active\033[0m")
                    print()
                    print("\033[1;30m💡 Pour forcer une nouvelle authentification:\033[0m")
                    print("   \033[1;36malexa auth create --force\033[0m")
                    print()
                    return True  # Retourner True car ce n'est pas une erreur

            # Vérifications préalables complètes
            if not self._check_prerequisites():
                return False

            # Import des modules d'auth (uniquement si nécessaire)
            from alexa_auth.alexa_cookie_retriever import get_alexa_cookies

            # Transition state machine seulement si pas déjà connecté
            if self.state_machine.state != ConnectionState.AUTHENTICATED:
                self.state_machine.connect()

            # Lancer le processus d'authentification Node.js
            self.logger.info("🔄 Démarrage du processus d'authentification...")
            self.logger.info("🌐 Connexion au service Amazon Alexa...")

            # Récupérer la configuration régionale (arguments CLI avec valeurs par défaut)
            amazon_domain = args.amazon
            language = args.language

            success = get_alexa_cookies(amazon_domain=amazon_domain, language=language)

            if success:
                if self.state_machine.state != ConnectionState.AUTHENTICATED:
                    self.state_machine.on_connected()
                self.logger.success("✅ Session créée avec succès !")
                self.logger.info("💾 Les cookies ont été sauvegardés dans alexa_auth/data/")
                
                # Invalider le cache d'auth pour forcer rechargement
                if self.context.cache_service:
                    self.context.cache_service.invalidate("auth_data")
                    self.logger.debug("🗑️ Cache auth invalidé après création")
                
                return True
            else:
                self.state_machine.error()
                self.logger.error("❌ Échec de la création de session")
                print("❌ Échec de la création de session")
                return False

        except Exception as e:
            self.logger.exception("💥 Erreur lors de la création de session")
            self.state_machine.error()
            self.logger.error(f"❌ Erreur: {e}")
            return False

    def _status(self, args: argparse.Namespace) -> bool:
        """
        Affiche le statut de connexion.

        Args:
            args: Arguments (utilise l'option globale verbose si définie)

        Returns:
            True toujours (ne peut pas échouer)
        """
        self.logger.info("ℹ️  État de connexion")
        print()

        # État de la state machine
        state_name = self.state_machine.state.name if self.state_machine else "UNKNOWN"
        can_execute = self.state_machine.can_execute_commands if self.state_machine else False

        # Affichage avec couleurs et style amélioré
        print("\033[1;4;30m🔐 ÉTAT DE CONNEXION\033[0m")  # Gris gras souligné avec emoji
        print()
        
        # Colorer l'état en vert si authentifié
        state_display = "\033[32mAUTHENTICATED\033[0m" if state_name == "AUTHENTICATED" else state_name
        cmd_status = "\033[32mOui\033[0m" if can_execute else "\033[31mNon\033[0m"
        print(f"\033[1;30m  État\033[0m                         {state_display}")
        print(f"\033[1;30m  Peut exécuter commandes\033[0m      {cmd_status}")
        
        # Vérifier existence des fichiers
        auth_data_dir = Path("alexa_auth/data")
        cookie_file = auth_data_dir / "cookie.txt"
        cookie_json = auth_data_dir / "cookie-resultat.json"

        cookie_txt_exists = cookie_file.exists()
        cookie_txt_status = "\033[32mPrésent\033[0m" if cookie_txt_exists else "\033[31mManquant\033[0m"
        print(f"\033[1;30m  Fichier cookie.txt\033[0m           {cookie_txt_status}")

        cookie_json_exists = cookie_json.exists()
        cookie_json_status = "\033[32mPrésent\033[0m" if cookie_json_exists else "\033[31mManquant\033[0m"
        print(f"\033[1;30m  Fichier cookie-resultat.json\033[0m {cookie_json_status}")

        # Afficher les infos du cookie même sans --verbose
        if cookie_json_exists:
            try:
                import json
                from datetime import datetime
                
                with open(cookie_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Domaine Amazon
                domain = None
                if "donneesCompletes" in data and "amazonPage" in data["donneesCompletes"]:
                    domain = data["donneesCompletes"]["amazonPage"]
                elif "recapitulatif" in data and "amazonPage" in data["recapitulatif"]:
                    domain = data["recapitulatif"]["amazonPage"]
                
                if domain:
                    print(f"\033[1;30m  Domaine Amazon\033[0m               {domain}")
                
                # Date de création et âge
                token_date = None
                if "recapitulatif" in data and "tokenDate" in data["recapitulatif"]:
                    token_date = data["recapitulatif"]["tokenDate"]
                elif "donneesCompletes" in data and "tokenDate" in data["donneesCompletes"]:
                    token_date = data["donneesCompletes"]["tokenDate"]
                
                if token_date:
                    dt = datetime.fromtimestamp(token_date / 1000)  # Convertir ms en s
                    date_str = dt.strftime("%d/%m/%Y %H:%M:%S")
                    
                    # Calculer l'âge
                    age_seconds = (datetime.now() - dt).total_seconds()
                    if age_seconds < 3600:
                        age_str = f"{int(age_seconds / 60)} minutes"
                    elif age_seconds < 86400:
                        age_str = f"{int(age_seconds / 3600)} heures"
                    else:
                        age_str = f"{int(age_seconds / 86400)} jours"
                    
                    print(f"\033[1;30m  Date de création\033[0m             {date_str}")
                    print(f"\033[1;30m  Âge du cookie\033[0m                {age_str}")
                
                # CSRF token (juste indiquer présence)
                if "recapitulatif" in data and "csrf" in data["recapitulatif"]:
                    csrf_status = "\033[32mPrésent\033[0m"
                    print(f"\033[1;30m  CSRF token\033[0m                   {csrf_status}")
                
            except Exception as e:
                self.logger.debug(f"Erreur lecture cookie-resultat.json: {e}")

        # Utiliser l'option globale --verbose si elle existe
        verbose = getattr(args, 'verbose', False)
        if verbose:
            print()
            print(f"\033[1;30m  Répertoire auth\033[0m              {auth_data_dir}")
            
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
            print("\n💡 Utilisez 'alexa auth create' pour créer une session")

        print()
        return True

    def _has_valid_cookies(self) -> bool:
        """
        Vérifie si des cookies valides existent déjà.

        Returns:
            True si des cookies valides sont présents
        """
        from pathlib import Path
        import json

        cookie_file = Path("alexa_auth/data/cookie-resultat.json")

        if not cookie_file.exists():
            self.logger.debug("🔍 Aucun fichier de cookie trouvé")
            return False

        try:
            with open(cookie_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Vérifier la présence des données essentielles
            recap = data.get("recapitulatif", {})
            if not recap.get("cookie") or not recap.get("csrf"):
                self.logger.debug("⚠️ Cookie en cache incomplet")
                return False

            self.logger.debug("✅ Cookies valides trouvés")
            return True

        except Exception as e:
            self.logger.debug(f"❌ Erreur lors de la vérification du cache: {e}")
            return False

    def _delete_existing_cookies(self) -> None:
        """
        Supprime les cookies existants avant de créer de nouveaux.
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
                self.logger.debug(f"🗑️ Cookie supprimé: {file_path}")
                deleted_count += 1

        if deleted_count > 0:
            self.logger.info(f"🗑️ {deleted_count} cookie(s) existant(s) supprimé(s)")
        else:
            self.logger.debug("🔍 Aucun cookie existant à supprimer")

    def _check_prerequisites(self) -> bool:
        """
        Vérifie tous les prérequis avant l'authentification.

        Returns:
            True si tous les prérequis sont OK
        """
        from typing import List

        issues_found: List[str] = []

        # 1. Vérifier l'environnement virtuel Python
        if not self._check_python_venv():
            issues_found.append("python_venv")

        # 2. Vérifier Node.js
        if not self._check_nodejs():
            issues_found.append("nodejs")

        # 3. Vérifier les dépendances npm
        if not self._check_npm_dependencies():
            issues_found.append("npm_deps")

        # 4. Vérifier les fichiers requis
        if not self._check_required_files():
            issues_found.append("required_files")

        if issues_found:
            self._show_installation_instructions(issues_found)
            return False

        self.logger.success("✅ Tous les prérequis vérifiés")
        return True

    def _check_python_venv(self) -> bool:
        """Vérifie si l'environnement virtuel Python est activé"""
        import sys

        # Vérifier si on est dans un venv
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

        if not in_venv:
            return False

        # Vérifier que les packages requis sont installés
        try:
            import requests
            import nodeenv
        except ImportError:
            return False

        return True

    def _check_nodejs(self) -> bool:
        """Vérifie si Node.js est installé via nodeenv"""
        from pathlib import Path
        from alexa_auth.alexa_cookie_retriever import NodeEnvironment

        script_dir = Path("alexa_auth").absolute()
        node_env = NodeEnvironment(script_dir)

        if not node_env.is_installed():
            return False

        # Tester que Node.js fonctionne
        try:
            version = node_env.get_node_version()
            return version is not None and version.startswith('v')
        except:
            return False

    def _check_npm_dependencies(self) -> bool:
        """Vérifie si les dépendances npm sont installées"""
        from pathlib import Path

        script_dir = Path("alexa_auth/nodejs")
        node_modules = script_dir / "node_modules"

        if not node_modules.exists():
            return False

        # Vérifier quelques packages clés
        required_packages = ["alexa-cookie2", "yargs"]
        for package in required_packages:
            if not (node_modules / package).exists():
                return False

        return True

    def _check_required_files(self) -> bool:
        """Vérifie si les fichiers requis existent"""
        from pathlib import Path

        required_files = [
            "alexa_auth/nodejs/package.json",
            "alexa_auth/nodejs/alexa-cookie-lib.js",
            "alexa_auth/nodejs/auth-initial.js",
        ]

        for file_path in required_files:
            if not Path(file_path).exists():
                return False

        return True

    def _show_installation_instructions(self, issues):
        """Affiche les instructions d'installation selon les problèmes détectés"""
        import sys

        self.logger.error("⚠️ Prérequis manquants détectés")
        self.logger.info("")
        self.logger.info("Problèmes identifiés:")

        for issue in issues:
            if issue == "python_venv":
                self.logger.info("  Environnement virtuel Python non activé ou packages manquants")
            elif issue == "nodejs":
                self.logger.info("  Node.js non installé via nodeenv")
            elif issue == "npm_deps":
                self.logger.info("  Dépendances npm non installées")
            elif issue == "required_files":
                self.logger.info("  Fichiers requis manquants")

        self.logger.info("")
        self.logger.info("Instructions d'installation:")

        if sys.platform == "win32":
            # Instructions Windows
            self.logger.info("")
            self.logger.info("  Installation complète (recommandé):")
            self.logger.info("     scripts\\install.ps1")
            self.logger.info("")
            self.logger.info("  Installation manuelle:")
            self.logger.info("     1. Créer/activer le venv Python:")
            self.logger.info("        scripts\\venv_manager.bat create")
            self.logger.info("        scripts\\venv_manager.bat activate")
            self.logger.info("")
            self.logger.info("     2. Installer Node.js et dépendances:")
            self.logger.info("        python scripts\\install.py")
        else:
            # Instructions Unix/Linux/macOS
            self.logger.info("")
            self.logger.info("  Installation complète (recommandé):")
            self.logger.info("     bash scripts/install.sh")
            self.logger.info("")
            self.logger.info("  Installation manuelle:")
            self.logger.info("     1. Créer/activer le venv Python:")
            self.logger.info("        bash scripts/venv_manager.sh create")
            self.logger.info("        source scripts/venv_manager.sh activate")
            self.logger.info("")
            self.logger.info("     2. Installer Node.js et dépendances:")
            self.logger.info("        python scripts/install.py")

        self.logger.info("")
        self.logger.info("  Puis relancer l'authentification:")
        self.logger.info("     python alexa auth create")
        self.logger.info("")
        self.logger.info("Conseil: Utilisez l'installation complète pour éviter les problèmes")
