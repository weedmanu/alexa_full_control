"""
Commandes d'authentification pour la CLI Alexa Voice Control.

Ce module gère toutes les opérations liées à l'authentification:
- login: Connexion à l'API Alexa
- logout: Déconnexion
- status: Vérifier l'état de connexion
- refresh: Rafraîchir le token d'authentification

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
import subprocess
from pathlib import Path

from cli.base_command import BaseCommand
from cli.command_parser import UniversalHelpFormatter, ActionHelpFormatter
from cli.help_texts.auth_help import (
    AUTH_DESCRIPTION,
    CREATE_HELP,
    DELETE_HELP,
    STATUS_HELP,
    REFRESH_HELP,
)
from core.state_machine import ConnectionState


class AuthCommand(BaseCommand):
    """
    Commande d'authentification Alexa.

    Gère login, logout, status et refresh token.

    Actions:
        - login: Se connecter à l'API Alexa
        - logout: Se déconnecter
        - status: Vérifier l'état de connexion
        - refresh: Rafraîchir le token

    Example:
        >>> python alexa.py auth login
        >>> python alexa.py auth status
        >>> python alexa.py auth refresh
        >>> python alexa.py auth logout
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

        # Action: delete
        delete_parser = subparsers.add_parser(
            "delete",
            help="Supprimer les cookies d'authentification",
            description=DELETE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )

        # Action: status
        status_parser = subparsers.add_parser(
            "status",
            help="Vérifier l'état de connexion",
            description=STATUS_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )

        # Action: refresh
        refresh_parser = subparsers.add_parser(
            "refresh",
            help="Rafraîchir le token d'authentification",
            description=REFRESH_HELP,
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
        elif args.action == "delete":
            return self._delete(args)
        elif args.action == "status":
            return self._status(args)
        elif args.action == "refresh":
            return self._refresh(args)
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
        self.logger.log("AUTH", "Création d'une session d'authentification...")

        try:
            # Vérifier si déjà connecté
            if not args.force and self._check_existing_auth():
                self.logger.log("AUTH", "Cookie valide déjà présent")
                self.logger.log("AUTH", "Affichage de l'état détaillé de la session existante...")
                print()
                print("\033[1;4;33m⚠️  INFORMATION\033[0m")  # Jaune gras souligné avec emoji
                print()
                print("\033[1;30m  Session existante\033[0m             \033[32mValide\033[0m")
                print("\033[1;30m  Cookies présents\033[0m              \033[32mOui\033[0m")
                print("\033[1;30m  Pour forcer la recréation\033[0m     Utilisez \033[1m--force\033[0m")
                print()
                # Afficher les informations d'état comme dans la commande status
                return self._status(args)

            # Vérifications préalables complètes
            if not self._check_prerequisites():
                return False

            # Import des modules d'auth (uniquement si nécessaire)
            from alexa_auth.alexa_cookie_retriever import get_alexa_cookies

            # Transition state machine seulement si pas déjà connecté
            if self.state_machine.state != ConnectionState.AUTHENTICATED:
                self.state_machine.connect()

            # Lancer le processus d'authentification Node.js
            self.logger.log("PROCESS", "Lancement du processus d'authentification Node.js...")
            self.logger.log("AUTH", "Une fenêtre de navigateur va s'ouvrir pour vous connecter à Amazon.")

            success = get_alexa_cookies()

            if success:
                if self.state_machine.state != ConnectionState.AUTHENTICATED:
                    self.state_machine.on_connected()
                self.logger.log("AUTH", "Session créée avec succès !")
                self.logger.log("CACHE", "Les cookies ont été sauvegardés dans alexa_auth/data/")
                
                # Invalider le cache d'auth pour forcer rechargement
                if self.context.cache_service:
                    self.context.cache_service.invalidate("auth_data")
                    self.logger.debug("Cache auth invalidé après création")
                
                return True
            else:
                self.state_machine.error()
                self.error("Échec de la création de session")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la création de session")
            self.state_machine.error()
            self.error(f"Erreur: {e}")
            return False

    def _delete(self, args: argparse.Namespace) -> bool:
        """
        Supprimer les cookies d'authentification.

        Args:
            args: Arguments

        Returns:
            True si succès
        """
        self.logger.log("CLEANUP", "Suppression des cookies...")

        try:
            # Se déconnecter d'abord
            if self.state_machine.state != ConnectionState.DISCONNECTED:
                self.state_machine.disconnect()

            # Supprimer tous les fichiers d'auth
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
                    self.logger.debug(f"Supprimé: {file_path}")
                    deleted_count += 1

            if deleted_count > 0:
                self.success(f"✅ Suppression réussie ({deleted_count} fichier(s))")
                
                # Invalider le cache d'auth
                if self.context.cache_service:
                    self.context.cache_service.invalidate("auth_data")
                    self.logger.debug("Cache auth invalidé après suppression")
            else:
                self.info("Aucun cookie trouvé à supprimer")

            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression")
            self.error(f"Erreur: {e}")
            return False

    def _status(self, args: argparse.Namespace) -> bool:
        """
        Affiche le statut de connexion.

        Args:
            args: Arguments (utilise l'option globale verbose si définie)

        Returns:
            True toujours (ne peut pas échouer)
        """
        self.logger.log("AUTH", "État de connexion:")

        # État de la state machine
        state_name = self.state_machine.state.name if self.state_machine else "UNKNOWN"
        can_execute = self.state_machine.can_execute_commands if self.state_machine else False

        print(f"  État: {state_name}")
        print(f"  Peut exécuter commandes: {'✅ Oui' if can_execute else '❌ Non'}")

        # Vérifier existence des fichiers
        auth_data_dir = Path("alexa_auth/data")
        cookie_file = auth_data_dir / "cookie.txt"
        cookie_json = auth_data_dir / "cookie-resultat.json"

        print(f"  Fichier cookie.txt: {'✅' if cookie_file.exists() else '❌'}")
        print(f"  Fichier cookie-resultat.json: {'✅' if cookie_json.exists() else '❌'}")

        # Utiliser l'option globale --verbose si elle existe
        verbose = getattr(args, 'verbose', False)
        if verbose:
            # Informations détaillées
            print("\n📋 Détails:")
            print(f"  Répertoire auth: {auth_data_dir.absolute()}")

            if cookie_file.exists():
                size = cookie_file.stat().st_size
                print(f"  Taille cookie.txt: {size} octets")

            if cookie_json.exists():
                size = cookie_json.stat().st_size
                print(f"  Taille cookie-resultat.json: {size} octets")

        # Recommandation
        if not can_execute:
            print("\n💡 Utilisez 'alexa auth create' pour créer une session")

        return True

    def _refresh(self, args: argparse.Namespace) -> bool:
        """
        Rafraîchit le token d'authentification.

        Args:
            args: Arguments

        Returns:
            True si succès
        """
        self.logger.log("PROCESS", "Rafraîchissement du token...")

        try:
            # Vérifier si connecté
            if not self._check_existing_auth():
                self.error("Pas de token existant. Utilisez 'auth create' d'abord.")
                return False

            # Transition state machine
            self.state_machine.refresh_token()

            # Import du script de refresh Node.js
            refresh_script = Path("alexa_auth/nodejs/auth-refresh.js")

            if not refresh_script.exists():
                self.error(f"Script de refresh non trouvé: {refresh_script}")
                return False

            # Exécuter le script Node.js
            result = subprocess.run(
                ["node", str(refresh_script)], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                self.state_machine.on_connected()
                self.success("✅ Token rafraîchi avec succès")
                return True
            else:
                self.state_machine.error()
                self.error(f"Échec du rafraîchissement: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.state_machine.error()
            self.error("Timeout lors du rafraîchissement")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors du refresh")
            self.state_machine.error()
            self.error(f"Erreur: {e}")
            return False

    def _check_existing_auth(self) -> bool:
        """
        Vérifie si des credentials existent déjà.

        Returns:
            True si des credentials existent (valides en permanence)
        """
        auth_data_dir = Path("alexa_auth/data")
        cookie_file = auth_data_dir / "cookie.txt"
        cookie_json = auth_data_dir / "cookie-resultat.json"

        return cookie_file.exists() and cookie_json.exists()

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

        self.success("✅ Tous les prérequis vérifiés")
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
        required_packages = ["express", "yargs", "cookie"]
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

        self.error("❌ Prérequis manquants détectés")
        self.info("")
        self.info("📋 Problèmes identifiés:")

        for issue in issues:
            if issue == "python_venv":
                self.info("  ❌ Environnement virtuel Python non activé ou packages manquants")
            elif issue == "nodejs":
                self.info("  ❌ Node.js non installé via nodeenv")
            elif issue == "npm_deps":
                self.info("  ❌ Dépendances npm non installées")
            elif issue == "required_files":
                self.info("  ❌ Fichiers requis manquants")

        self.info("")
        self.info("🔧 Instructions d'installation:")

        if sys.platform == "win32":
            # Instructions Windows
            self.info("")
            self.info("  📦 Installation complète (recommandé):")
            self.info("     scripts\\install.ps1")
            self.info("")
            self.info("  🔧 Installation manuelle:")
            self.info("     1. Créer/activer le venv Python:")
            self.info("        scripts\\venv_manager.bat create")
            self.info("        scripts\\venv_manager.bat activate")
            self.info("")
            self.info("     2. Installer Node.js et dépendances:")
            self.info("        python scripts\\install.py")
        else:
            # Instructions Unix/Linux/macOS
            self.info("")
            self.info("  📦 Installation complète (recommandé):")
            self.info("     bash scripts/install.sh")
            self.info("")
            self.info("  🔧 Installation manuelle:")
            self.info("     1. Créer/activer le venv Python:")
            self.info("        bash scripts/venv_manager.sh create")
            self.info("        source scripts/venv_manager.sh activate")
            self.info("")
            self.info("     2. Installer Node.js et dépendances:")
            self.info("        python scripts/install.py")

        self.info("")
        self.info("  ✅ Puis relancer l'authentification:")
        self.info("     python alexa auth create")
        self.info("")
        self.info("💡 Conseil: Utilisez l'installation complète pour éviter les problèmes")
