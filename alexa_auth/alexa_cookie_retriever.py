#!/usr/bin/env python3

"""
============================================================================
Script de récupération de cookie Alexa - Version Python
Compatible: Windows, macOS, Linux
Utilise nodeenv pour un environnement Node.js isolé
============================================================================
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Ajouter le parent au path pour importer utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import setup_logger

# Configuration du logger
logger = setup_logger(__name__)


class Colors:
    """Codes couleurs ANSI pour le terminal"""

    BLUE = "\033[1;34m"
    YELLOW = "\033[1;33m"
    RED = "\033[1;31m"
    RESET = "\033[0m"

    @staticmethod
    def is_supported():
        """Vérifie si les couleurs sont supportées"""
        return sys.stdout.isatty() and os.name != "nt"


def print_step(message: str):
    """Affiche un message de progression"""
    if Colors.is_supported():
        print(f"{Colors.BLUE}{message}{Colors.RESET}")
    else:
        print(message)


def print_warn(message: str):
    """Affiche un avertissement"""
    if Colors.is_supported():
        print(f"{Colors.YELLOW}{message}{Colors.RESET}")
    else:
        print(f"ATTENTION: {message}")


def print_error(message: str):
    """Affiche une erreur"""
    if Colors.is_supported():
        print(f"{Colors.RED}{message}{Colors.RESET}", file=sys.stderr)
    else:
        print(f"ERREUR: {message}", file=sys.stderr)


class NodeEnvironment:
    """
    Gestionnaire d'environnement Node.js via nodeenv.
    Utilise un environnement Node.js isolé pour l'authentification.
    """

    def __init__(self, script_dir: Path):
        self.script_dir = script_dir
        self.node_env_dir = script_dir / "nodejs" / ".nodeenv"

        # Chemins des exécutables selon la plateforme
        if sys.platform == "win32":
            self.node_executable = self.node_env_dir / "Scripts" / "node.exe"
            self.npm_executable = self.node_env_dir / "Scripts" / "npm.cmd"
        else:
            self.node_executable = self.node_env_dir / "bin" / "node"
            self.npm_executable = self.node_env_dir / "bin" / "npm"

    def is_installed(self) -> bool:
        """Vérifie si nodeenv est installé et configuré"""
        return (
            self.node_env_dir.exists()
            and self.node_executable.exists()
            and self.npm_executable.exists()
        )

    def get_node_version(self) -> Optional[str]:
        """Récupère la version de Node.js installée"""
        if not self.node_executable.exists():
            return None

        try:
            result = subprocess.run(
                [str(self.node_executable), "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def get_npm_version(self) -> Optional[str]:
        """Récupère la version de npm installée"""
        if not self.npm_executable.exists():
            return None

        try:
            result = subprocess.run(
                [str(self.npm_executable), "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def check_and_prepare(self) -> bool:
        """
        Vérifie que nodeenv est installé et prêt.
        Retourne True si tout est OK, False sinon.
        """
        if not self.is_installed():
            print_error("❌ Node.js (nodeenv) n'est pas installé")
            print()
            print("📌 Veuillez exécuter le script d'installation:")
            print("   python scripts/install.py")
            print()
            return False

        # Afficher les versions
        node_version = self.get_node_version()
        npm_version = self.get_npm_version()

        if node_version:
            print_step(f"Node.js utilisé : {node_version}")
        if npm_version:
            logger.debug(f"npm version: {npm_version}")

        return True

    def install_npm_dependencies(self) -> bool:
        """Installe les dépendances npm si nécessaire"""
        nodejs_dir = self.script_dir / "nodejs"
        node_modules = nodejs_dir / "node_modules"

        # Si node_modules existe déjà, ne rien faire
        if node_modules.exists() and any(node_modules.iterdir()):
            logger.debug("Dépendances npm déjà installées")
            return True

        print_step("Installation des dépendances npm...")
        try:
            subprocess.run(
                [str(self.npm_executable), "install", "--no-audit", "--progress=false"],
                cwd=nodejs_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            print_step("✓ Dépendances npm installées")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Erreur lors de l'installation npm: {e}")
            return False


class CookieRetriever:
    """Gestionnaire de récupération de cookie Alexa"""

    def __init__(self, script_dir: Path):
        self.script_dir = script_dir
        self.nodejs_dir = script_dir / "nodejs"
        self.data_dir = script_dir / "data"
        self.cookie_result_file = self.data_dir / "cookie-resultat.json"

        # Créer le répertoire data s'il n'existe pas
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def is_cookie_valid(self) -> bool:
        """Vérifie si les cookies existent et sont complets"""
        if not self.cookie_result_file.exists():
            logger.debug("Aucun fichier de cookie trouvé")
            return False

        try:
            import json

            with open(self.cookie_result_file, encoding="utf-8") as f:
                data = json.load(f)

            # Vérifier la présence des données essentielles
            recap = data.get("recapitulatif", {})
            if not recap.get("cookie") or not recap.get("csrf"):
                logger.debug("Cookie en cache incomplet")
                return False

            # Les cookies Amazon restent valides indéfiniment
            # tant qu'il n'y a pas de changement de mot de passe ou révocation
            logger.debug("Cookies valides trouvés")
            return True

        except Exception as e:
            logger.debug(f"Erreur lors de la vérification du cache: {e}")
            return False

    def launch_cookie_retrieval(self):
        """Lance la récupération automatique du cookie avec refresh token"""
        print_step("Régénération automatique du cookie avec le refresh token...")

        if not self.cookie_result_file.exists():
            print_error("Fichier cookie-resultat.json non trouvé. Lancez d'abord l'installation.")
            sys.exit(1)

        refresh_script = self.nodejs_dir / "refresh-cookie.js"

        # Vérifier que l'exécutable node est trouvable
        import shutil

        node_cmd = shutil.which("node") or (str(self.nodejs_dir / "node") if (self.nodejs_dir / "node").exists() else None)
        if not node_cmd:
            print_error("Node.js introuvable pour rafraîchir le cookie")
            sys.exit(1)

        try:
            subprocess.run([node_cmd, str(refresh_script)], cwd=self.nodejs_dir, check=True)
        except subprocess.CalledProcessError as e:
            print_error(f"Échec du rafraîchissement du cookie: {e}")
            sys.exit(1)

    def launch_initial_setup(self, email: str, password: str, mfa_secret: Optional[str] = None):
        """Lance le processus d'authentification initial"""

        # Vérifier d'abord le cache
        if self.is_cookie_valid():
            print_step("✓ Cookie valide trouvé en cache, authentification non nécessaire")
            return

        print_step("Lancement de l'authentification initiale...")

        # Utiliser Node.js de nodeenv
        node_env = NodeEnvironment(self.script_dir)
        node_executable = node_env.node_executable

        # Utilise le script refactorisé
        setup_script = self.nodejs_dir / "auth-initial.js"

        cmd = [str(node_executable), str(setup_script), "--email", email, "--password", password]

        if mfa_secret:
            cmd.extend(["--mfaSecret", mfa_secret])

        # Vérifier que node existe avant d'appeler
        import shutil

        node_cmd = shutil.which(str(node_executable)) or shutil.which("node") or (str(node_executable) if node_executable.exists() else None)
        if not node_cmd:
            print_error("Node.js introuvable pour l'authentification initiale")
            sys.exit(1)

        try:
            subprocess.run([node_cmd, str(setup_script), "--email", email, "--password", password], cwd=self.nodejs_dir, check=True)
        except subprocess.CalledProcessError as e:
            print_error(f"Échec de l'authentification initiale: {e}")
            sys.exit(1)


def get_alexa_cookies(amazon_domain: str = "amazon.fr", language: str = "fr-FR"):
    """Fonction principale pour récupérer les cookies Alexa (interface CLI)"""
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    # Définir les variables d'environnement pour la configuration régionale
    os.environ["AMAZON_DOMAIN"] = amazon_domain
    os.environ["LANGUAGE"] = language

    # Vérifier l'environnement Node.js
    node_env = NodeEnvironment(script_dir)
    if not node_env.check_and_prepare():
        return False

    # Installer les dépendances npm si nécessaire
    if not node_env.install_npm_dependencies():
        return False

    # Gestionnaire de récupération de cookie
    retriever = CookieRetriever(script_dir)

    # Authentification via navigateur (recommandé)
    retriever.launch_initial_setup("", "", None)
    return True


def main():
    """Fonction principale"""
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    # Vérifier l'environnement Node.js
    node_env = NodeEnvironment(script_dir)
    if not node_env.check_and_prepare():
        sys.exit(1)

    # Installer les dépendances npm si nécessaire
    if not node_env.install_npm_dependencies():
        sys.exit(1)

    # Récupérer les variables d'environnement
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    mfa_secret = os.getenv("MFA_SECRET")

    # Gestionnaire de récupération de cookie
    retriever = CookieRetriever(script_dir)

    # Détecter le mode d'opération
    if email and password:
        # Mode installation initiale avec credentials
        retriever.launch_initial_setup(email, password, mfa_secret)
    else:
        # Mode installation initiale via navigateur (pas de credentials)
        retriever.launch_initial_setup("", "", None)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nInterrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
