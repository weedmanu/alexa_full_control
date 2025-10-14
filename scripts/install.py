#!/usr/bin/env python3
"""
Script d'installation cross-platform pour Alexa Advanced Control.

Ce script installe automatiquement tous les composants nécessaires :
- Environnement virtuel Python (.venv)
- Dépendances Python depuis requirements.txt
- Node.js via nodeenv
- Packages npm (alexa-cookie2, yargs)
- Configuration et tests

Supporte Windows, Linux et macOS.

NOTE: Ce script remplace install.ps1, install.bat, install.sh,
uninstall.ps1, uninstall.bat et uninstall.sh pour une solution unifiée.
"""

import argparse
import platform
import shutil
import subprocess
import sys

# textwrap is imported locally where needed to avoid global dependency at import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configuration
PYTHON_MIN_VERSION = (3, 8)
NODE_VERSION = "20.17.0"
REQUIRED_PACKAGES = [
    "nodeenv>=1.8.0",
    "requests",
    "beautifulsoup4",
    "lxml",
    "selenium",
    "loguru",
    "requests-cache",
    "typing-extensions",
    "pybreaker",
]


class CLIError(Exception):
    """Exception utilisée pour remonter une erreur vers le wrapper CLI.

    Contient un code de sortie dans `.code` et un message optionnel dans `.message`.
    """

    def __init__(self, code: int = 1, message: Optional[str] = None):
        super().__init__(message)
        self.code = code
        self.message = message


class Colors:
    """Gestion des couleurs pour l'affichage cross-platform."""

    # Codes ANSI
    RESET = "\033[0m"

    # Couleurs principales utilisées
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"

    @staticmethod
    def supports_color() -> bool:
        """Vérifie si le terminal supporte les couleurs."""
        if platform.system() == "Windows":
            try:
                import colorama

                colorama.init()
                return True
            except ImportError:
                return False
        return True

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Colorise le texte si supporté."""
        if not Colors.supports_color():
            return text
        return f"{color}{text}{Colors.RESET}"


class Logger:
    """Gestionnaire de logging avec couleurs."""

    @staticmethod
    def _display_width(text: str) -> int:
        """Approximate visible width of text in monospace terminal.

        Uses unicodedata.east_asian_width: characters classified as W or F count as 2,
        combining marks count as 0, others as 1. This is a lightweight wcwidth
        approximation sufficient for centering headers with emojis.
        """
        import unicodedata

        width = 0
        for ch in text:
            if unicodedata.category(ch) == "Mn":
                # non-spacing mark
                continue
            ea = unicodedata.east_asian_width(ch)
            if ea in ("F", "W"):
                width += 2
            else:
                width += 1
        return width

    @staticmethod
    def _truncate_to_width(text: str, max_width: int) -> str:
        """
        Tronque le texte pour qu'il tienne dans max_width (approx display width).
        Ajoute '...' si le texte a été tronqué.
        """
        disp = 0
        out = []
        import unicodedata

        for ch in text:
            if unicodedata.category(ch) == "Mn":
                # non-spacing mark
                continue
            ea = unicodedata.east_asian_width(ch)
            w = 2 if ea in ("F", "W") else 1
            if disp + w > max_width - 3:
                out.append("...")
                break
            out.append(ch)
            disp += w
        return "".join(out)

    @staticmethod
    def header(msg: str, emoji: str = "🔧") -> None:
        """Affiche un en-tête stylisé."""
        # Utiliser la même logique que `step` pour garantir un rendu uniforme
        # Use a stable fixed width to avoid dynamic growth and wrapping artifacts
        width = 78
        border = "═" * width

        # Prepare lines (support multi-line). Prepend emoji to the first line only.
        lines = str(msg).splitlines() or [""]
        if emoji:
            if emoji in {"ℹ️", "⚠️", "⚙️"}:
                lines[0] = f"{emoji}  {lines[0]}"
            else:
                lines[0] = f"{emoji} {lines[0]}"

        inner_width = width - 2

        print()
        print(Colors.colorize(border, Colors.CYAN))
        for line_text in lines:
            # Truncate visible text to inner_width using display width
            truncated = Logger._truncate_to_width(line_text, inner_width)
            disp = Logger._display_width(truncated)
            left_pad = (inner_width - disp) // 2
            right_pad = inner_width - disp - left_pad
            visible = truncated
            line = " " * left_pad + visible + " " * right_pad
            print(Colors.colorize("║", Colors.CYAN) + line + Colors.colorize("║", Colors.CYAN))
        print(Colors.colorize(border, Colors.CYAN))
        print()

    @staticmethod
    def step(msg: str, emoji: str = "⚡") -> None:
        """Affiche une étape en cours."""
        # Reuse same rendering as header to keep consistent borders
        Logger.header(msg, emoji)

    @staticmethod
    def progress(msg: str) -> None:
        """Affiche une progression."""
        Logger._internal_wrap_and_print("⏳", f"{msg}...", Colors.MAGENTA)

    @staticmethod
    def success(msg: str, emoji: str = "✅") -> None:
        """Affiche un succès."""
        # Simple one-line success message
        Logger._internal_wrap_and_print(emoji, msg, Colors.GREEN)

    @staticmethod
    def error(msg: str, emoji: str = "❌") -> None:
        """Affiche une erreur."""
        Logger._wrap_and_print(emoji, msg, Colors.RED)

    @staticmethod
    def warning(msg: str, emoji: str = "⚠️") -> None:
        """Affiche un avertissement."""
        Logger._internal_wrap_and_print(emoji, msg, Colors.YELLOW)

    @staticmethod
    def info(msg: str, emoji: str = "ℹ️") -> None:
        """Affiche une information."""
        Logger._internal_wrap_and_print(emoji, msg, Colors.CYAN)

    @staticmethod
    def _internal_wrap_and_print(emoji: str, msg: str, color: str, max_width: int = 78) -> None:
        """Wrap long messages to max_width and print with emoji prefix.

        The first printed line is prefixed with the emoji and two spaces; subsequent
        lines are aligned under the message (no emoji).
        """
        import textwrap

        # Normalize msg to a single string
        text = str(msg)

        # Prevent adjacent emojis: if msg starts with a non-alphanumeric character
        # (likely an emoji), strip it to avoid double emojis like "✅ 🎉 ...".
        if text and not text.lstrip()[0].isalnum():
            text = text.lstrip("".join(set(text) - set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")))

        def _strip_edge_emojis(s: str) -> str:
            """Remove known emoji prefixes and suffixes from a string ends.

            This ensures messages won't contain an emoji immediately after the
            Logger-provided emoji prefix (avoids sequences like "✅ 🎉 ...").
            """
            s2 = s.strip()
            EMOJI_PREFIXES = [
                "🎉",
                "🚀",
                "✅",
                "ℹ️",
                "⚠️",
                "⚙️",
                "🆘",
                "🔧",
                "⚡",
                "🔍",
                "🐍",
                "📦",
                "🟢",
                "📖",
                "🗑️",
            ]
            changed = True
            while changed:
                changed = False
                for e in EMOJI_PREFIXES:
                    # Leading emoji removal: this branch is defensive and often
                    # won't be hit because previous lstrip usually removes leading
                    # non-alphanumeric characters. Keep for parity with various
                    # emoji sequences but mark as no-cover for testing.
                    if s2.startswith(e):  # pragma: no cover - defensive
                        s2 = s2[len(e) :].lstrip()
                        changed = True
                        break
                if changed:  # pragma: no cover - defensive continue when leading emojis removed
                    continue
                for e in EMOJI_PREFIXES:
                    if s2.endswith(e):
                        s2 = s2[: -len(e)].rstrip()
                        changed = True
                        break
            return s2

        text = _strip_edge_emojis(text)
        # Compute available width after emoji and two spaces
        prefix = f"{emoji}  "
        avail = max_width - len(prefix)
        if avail <= 20:
            avail = max_width - 4

        wrapped = textwrap.wrap(text, width=avail) or [""]
        first = wrapped[0]
        print(Colors.colorize(prefix + first, color))
        for line in wrapped[1:]:
            print(Colors.colorize(" " * len(prefix) + line, color))

    @staticmethod
    def _wrap_and_print(emoji: str, msg: str, color: str, max_width: int = 78) -> None:
        """Backward-compatible wrapper kept for older callsites."""
        return Logger._internal_wrap_and_print(emoji, msg, color, max_width=max_width)


class SystemChecker:
    """Vérifications système cross-platform."""

    @staticmethod
    def get_platform_info() -> Dict[str, str]:
        """Retourne les informations sur la plateforme."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }

    @staticmethod
    def check_python_version() -> Tuple[bool, str]:
        """Vérifie la version de Python."""
        version = sys.version_info
        current = f"{version.major}.{version.minor}.{version.micro}"

        # Compare major/minor only against the minimum required
        if (version.major, version.minor) >= PYTHON_MIN_VERSION:
            return True, f"Python {current} détecté"
        else:
            min_version = f"{PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]}"
            return False, f"Python {current} détecté (minimum requis: {min_version})"

    @staticmethod
    def check_pip() -> Tuple[bool, str]:
        """Vérifie la disponibilité de pip."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            out = result.stdout.strip() if result.stdout else ""
            # Typical output: 'pip 25.2 from C:\...\site-packages\pip (python 3.13)'
            # We extract the first two tokens to display only the name and version.
            parts = out.split()
            if len(parts) >= 2:
                version_short = f"{parts[0]} {parts[1]}"
            else:
                version_short = out or "version inconnue"
            return True, f"pip disponible ({version_short})"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, "pip n'est pas disponible"

    @staticmethod
    def check_disk_space(path: Path, required_gb: float = 2.0) -> Tuple[bool, str]:
        """Vérifie l'espace disque disponible (utilise shutil.disk_usage pour compatibilité)."""
        try:
            usage = shutil.disk_usage(str(path))
            free_bytes = usage.free
            free_gb = free_bytes / (1024**3)
            if free_gb >= required_gb:
                return True, f"{free_gb:.1f} GB disponibles"
            else:
                return False, f"{free_gb:.1f} GB disponibles (<{required_gb}GB requis)"
        except Exception:
            return True, "Impossible de vérifier l'espace disque"


class PackageInstaller:
    """Gestionnaire d'installation des packages."""

    def __init__(self, install_dir: Path, dry_run: bool = False):
        self.install_dir = install_dir
        self.venv_path = install_dir / ".venv"
        self.dry_run = dry_run

    def run_command(
        self, cmd: List[str], cwd: Optional[Path] = None, capture_output: bool = False
    ) -> Any:
        """Exécute une commande avec gestion d'erreurs.

        Si `self.dry_run` est True, la commande n'est pas exécutée — on logue
        simplement ce qui aurait été exécuté et on retourne un objet simulé.
        """
        cmd_display = " ".join(cmd)
        cwd_display = str(cwd or self.install_dir)
        if self.dry_run:
            Logger.info(f"[dry-run] Commande simulée: {cmd_display} (cwd={cwd_display})")

            class _FakeResult:
                stdout = ""
                stderr = ""

            return _FakeResult()

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.install_dir,
                capture_output=capture_output,
                text=True,
                check=True,
            )
            return result
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Commande échouée: {cmd_display}\n{e.stderr}")

    def create_venv(self) -> None:
        """Crée l'environnement virtuel Python (.venv)."""
        Logger.step("Création de l'environnement virtuel")
        self.run_command([sys.executable, "-m", "venv", str(self.venv_path)])
        Logger.success("Environnement virtuel créé")

    def get_venv_python(self) -> Path:
        """Retourne le chemin vers python dans le .venv."""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"

    def get_venv_pip(self) -> Path:
        """Retourne le chemin vers pip dans le .venv."""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"

    def upgrade_pip(self) -> None:
        """Met à jour pip dans le .venv."""
        Logger.step("Mise à jour de pip")
        venv_pip = self.get_venv_pip()
        self.run_command([str(venv_pip), "install", "--upgrade", "pip"])
        Logger.success("pip mis à jour")

    def install_python_packages(self) -> None:
        """Installe les packages Python."""
        Logger.step("Installation des packages Python")

        venv_pip = self.get_venv_pip()
        requirements_file = self.install_dir / "requirements.txt"

        if requirements_file.exists():
            Logger.info("Installation depuis requirements.txt")
            self.run_command([str(venv_pip), "install", "-r", str(requirements_file)])
        else:
            Logger.info("requirements.txt non trouvé, installation manuelle")
            # Installation des packages essentiels
            for package in REQUIRED_PACKAGES:
                try:
                    self.run_command([str(venv_pip), "install", package])
                except RuntimeError:
                    Logger.warning(f"Échec d'installation de {package}")

        Logger.success("Packages Python installés")

    def install_nodejs(self) -> None:
        """Installe Node.js via nodeenv."""
        Logger.step(f"Installation de Node.js v{NODE_VERSION}")

        nodejs_dir = self.install_dir / "alexa_auth" / "nodejs"
        nodejs_dir.mkdir(parents=True, exist_ok=True)

        venv_python = self.get_venv_python()

        # Installation via nodeenv
        self.run_command(
            [str(venv_python), "-m", "nodeenv", f"--node={NODE_VERSION}", "--prebuilt", ".nodeenv"],
            cwd=nodejs_dir,
        )

        Logger.success(f"Node.js v{NODE_VERSION} installé")

    def get_nodejs_paths(self) -> Tuple[Path, Path]:
        """Retourne les chemins vers node et npm."""
        nodejs_dir = self.install_dir / "alexa_auth" / "nodejs" / ".nodeenv"

        if platform.system() == "Windows":
            node_path = nodejs_dir / "node.exe"
            npm_path = nodejs_dir / "npm.cmd"
        else:
            bin_dir = nodejs_dir / "bin"
            node_path = bin_dir / "node"
            npm_path = bin_dir / "npm"

        return node_path, npm_path

    def install_npm_packages(self) -> None:
        """Installe les packages npm."""
        Logger.step("Installation des packages npm")

        node_path, npm_path = self.get_nodejs_paths()

        # Vérification que Node.js fonctionne
        try:
            result = self.run_command([str(node_path), "--version"], capture_output=True)
            Logger.success(f"Node.js {result.stdout.strip()} fonctionnel")
        except RuntimeError:
            raise RuntimeError("Node.js n'est pas fonctionnel")

        # Installation des packages
        packages = ["alexa-cookie2", "yargs"]
        for package in packages:
            Logger.progress(f"Installation de {package}")
            try:
                self.run_command([str(npm_path), "install", package])
                Logger.success(f"{package} installé")
            except RuntimeError:
                Logger.warning(f"Échec d'installation de {package}")

    def create_data_directory(self) -> None:
        """Crée le dossier data si nécessaire."""
        data_dir = self.install_dir / "data"
        if not data_dir.exists():
            Logger.step("Création du dossier data")
            data_dir.mkdir(parents=True, exist_ok=True)
            Logger.success("Dossier data créé")

    def test_configuration(self) -> None:
        """Teste la configuration finale."""
        Logger.step("Test de la configuration")

        venv_python = self.get_venv_python()
        node_path, _ = self.get_nodejs_paths()

        # Test Python
        try:
            # Use `python -V` to get a compact version string (shorter than an inline -c command)
            result = self.run_command([str(venv_python), "-V"], capture_output=True)
            # Some Python versions print version to stderr; prefer stdout then stderr
            out = ""
            if getattr(result, "stdout", None):
                out = result.stdout.strip()
            elif getattr(result, "stderr", None):
                out = result.stderr.strip()
            version = out or "version inconnue"
            Logger.success(f"Test Python réussi ({version})")
        except RuntimeError:
            Logger.error("Test Python échoué")

        # Test Node.js
        try:
            self.run_command(
                [str(node_path), "-e", "console.log('Node.js OK')"], capture_output=True
            )
            Logger.success("Test Node.js réussi")
        except RuntimeError:
            Logger.error("Test Node.js échoué")


class InstallationManager:
    """Gestionnaire principal de l'installation."""

    def __init__(
        self,
        install_dir: Path,
        force: bool = False,
        skip_tests: bool = False,
        dry_run: bool = False,
        non_interactive: bool = False,
    ):
        self.install_dir = install_dir.resolve()
        self.force = force
        self.skip_tests = skip_tests
        self.dry_run = dry_run
        self.non_interactive = non_interactive
        self.installer = PackageInstaller(self.install_dir, dry_run=self.dry_run)

    def check_existing_installation(self) -> bool:
        """Vérifie s'il y a une installation existante."""
        venv_exists = (self.install_dir / ".venv").exists()
        nodeenv_exists = (self.install_dir / "alexa_auth" / "nodejs" / ".nodeenv").exists()

        return venv_exists or nodeenv_exists

    def cleanup_existing_installation(self) -> None:
        """Nettoie l'installation existante."""
        Logger.warning("Installation existante détectée")
        if not self.force:
            if not self.non_interactive:
                response = (
                    input("Voulez-vous nettoyer l'installation précédente? (o/N): ").strip().lower()
                )
                if response not in ["o", "oui", "yes", "y"]:
                    Logger.info("Installation annulée par l'utilisateur")
                    sys.exit(0)
            else:
                # non_interactive mode: assume yes
                Logger.info("Non-interactive: suppression confirmée")

        Logger.progress("Nettoyage en cours")

        # Suppression du .venv
        venv_path = self.install_dir / ".venv"
        if venv_path.exists():
            if self.dry_run:
                Logger.info(f"[dry-run] Suppression simulée: {venv_path}")
            else:
                shutil.rmtree(venv_path, ignore_errors=True)

        # Suppression de nodeenv
        nodeenv_path = self.install_dir / "alexa_auth" / "nodejs" / ".nodeenv"
        if nodeenv_path.exists():
            if self.dry_run:
                Logger.info(f"[dry-run] Suppression simulée: {nodeenv_path}")
            else:
                shutil.rmtree(nodeenv_path, ignore_errors=True)

        Logger.success("Nettoyage terminé")

    def show_uninstall_summary(self) -> None:
        """Affiche un petit résumé après la désinstallation."""
        # Note: referenced from tests; keep even if vulture thinks it's unused.
        # VULTURE_KEEP
        Logger.header("DÉSINSTALLATION TERMINÉE", "🗑️")
        print()
        Logger.success("Les fichiers .venv et nodeenv ont été supprimés (si présents)")
        print()
        Logger.header("COMMANDES UTILES APRÈS DÉSINSTALLATION", "⌨️")
        print()
        if platform.system() == "Windows":
            print("Vérifier suppression .venv: Test-Path .\\.venv  # PowerShell")
        else:
            print("Vérifier suppression .venv: [ -d .venv ] && echo exist || echo missing  # Bash")
        # Show the removal command on a separate indented line to avoid very long lines
        print("Supprimer nodeenv manuellement:")
        print("  Remove-Item -Recurse -Force .\\alexa_auth\\nodejs\\.nodeenv  # PowerShell")
        print("ou: rm -rf alexa_auth/nodejs/.nodeenv  # Bash")
        print()
        Logger.info("Pour réinstaller: python scripts/install.py")

    def run_system_checks(self) -> None:
        """Effectue les vérifications système."""
        Logger.header("VÉRIFICATIONS SYSTÈME", "🔍")

        # Informations système
        platform_info = SystemChecker.get_platform_info()
        Logger.info(f"Système: {platform_info['system']} {platform_info['release']}")

        # Vérification Python
        Logger.step("Vérification de Python")
        python_ok, python_msg = SystemChecker.check_python_version()
        if python_ok:
            Logger.success(python_msg)
        else:
            Logger.error(python_msg)
            Logger.info("Installez Python depuis: https://python.org")
            sys.exit(1)

        # Vérification pip
        Logger.step("Vérification de pip")
        pip_ok, pip_msg = SystemChecker.check_pip()
        if pip_ok:
            Logger.success(pip_msg)
        else:
            Logger.error(pip_msg)
            sys.exit(1)

        # Vérification espace disque
        Logger.step("Vérification de l'espace disque")
        disk_ok, disk_msg = SystemChecker.check_disk_space(self.install_dir)
        if disk_ok:
            Logger.success(disk_msg)
        else:
            Logger.warning(disk_msg)

    def run_installation(self) -> None:
        """Effectue l'installation complète."""
        # Nettoyage si nécessaire
        if self.check_existing_installation():
            self.cleanup_existing_installation()

        # Environnement Python
        Logger.header("ENVIRONNEMENT PYTHON", "🐍")
        self.installer.create_venv()
        self.installer.upgrade_pip()

        # Dépendances Python
        Logger.header("DÉPENDANCES PYTHON", "📦")
        self.installer.install_python_packages()

        # Environnement Node.js
        Logger.header("ENVIRONNEMENT NODE.JS", "🟢")
        self.installer.install_nodejs()
        self.installer.install_npm_packages()

        # Configuration finale
        Logger.header("CONFIGURATION FINALE", "⚙️")
        self.installer.create_data_directory()

        if not self.skip_tests:
            self.installer.test_configuration()

    def show_summary(self) -> None:
        """Affiche le résumé de l'installation."""
        Logger.header("INSTALLATION TERMINÉE", "🎉")

        print()
        Logger.success("Environnement Python (.venv) créé")
        Logger.success("Dépendances du projet installées")
        Logger.success(f"Node.js v{NODE_VERSION} installé via nodeenv")
        print()

        Logger.header("INSTRUCTIONS", "📖")
        print()
        # Afficher uniquement les commandes pertinentes pour activer le .venv
        activate_lines, _ = get_venv_instructions()
        for ln in activate_lines:
            print("  " + ln)
        print()

    # Montrer comment lancer le programme depuis l'environnement activé
    # (the actual lines are printed inside show_summary)


# Note: helper _wrap_block removed (unused) to reduce lint noise


def get_venv_instructions() -> Tuple[List[str], str]:
    """Retourne une paire (activation_lines, deactivate_cmd) adaptée à la plateforme."""
    if platform.system() == "Windows":
        activate_lines = [
            "PowerShell (Windows):",
            "  .\\.venv\\Scripts\\Activate.ps1",
            "CMD (Windows):",
            "  .\\.venv\\Scripts\\activate.bat",
        ]
        deactivate = "deactivate"
    else:
        activate_lines = [
            "Bash (Linux/macOS/WSL):",
            "  source .venv/bin/activate",
        ]
        deactivate = "deactivate"
    return activate_lines, deactivate


def running_in_project_venv(current_executable: Optional[str], install_dir: Path) -> bool:
    """Return True if the given current_executable path points inside install_dir/.venv.

    Accepts a path string or Path; callers should pass Path(sys.executable).
    """
    try:
        if current_executable is None:
            return False
        current = Path(str(current_executable)).resolve()
        venv_path = (install_dir / ".venv").resolve()
        # Compute membership explicitly so coverage tools register execution
        inside = (
            (venv_path in current.parents)
            or (current == (venv_path / "Scripts" / "python.exe"))  # pragma: no cover - redundant when parents includes venv_path
            or (current == (venv_path / "bin" / "python"))  # pragma: no cover - redundant when parents includes venv_path
        )
        return inside
    except Exception:
        return False  # pragma: no cover - defensive fallback for pathological Path.resolve failures
def core_main(args: argparse.Namespace, install_dir: Path, running_in_project_venv_fn) -> None:
    """Logique principale de l'installateur (testable).

    Lève `CLIError` pour signaler des terminaisons voulues au wrapper CLI.
    """
    # Title demandé par l'utilisateur (emoji fourni séparément pour éviter la duplication)
    Logger.header("INSTALLATION ALEXA ADVANCED CONTROL", "🚀")

    # Early detection: running inside project venv and requested uninstall
    if running_in_project_venv_fn() and args.uninstall:
        print()
        Logger.error("Le script a été lancé depuis le .venv du projet.")
        Logger.info("Pour quitter le .venv et pouvoir désinstaller, tapez:")
        if platform.system() == "Windows":
            Logger.info("  PowerShell: deactivate")
            Logger.info("  CMD: deactivate")
        else:
            Logger.info("  Bash / Zsh: deactivate")

        Logger.info("Ensuite relancez la désinstallation depuis votre shell utilisateur:")
        Logger.info("  python scripts/install.py --uninstall")
        # Stopper immédiatement pour éviter tout dommage à l'environnement actif.
        raise CLIError(2)

    # Main flow
    try:
        try:
            manager = InstallationManager(
                install_dir, args.force, args.skip_tests, dry_run=args.dry_run, non_interactive=args.yes
            )
        except TypeError:
            manager = InstallationManager(install_dir, args.force, args.skip_tests, dry_run=args.dry_run)

        # If running within the project venv, block dangerous operations
        if running_in_project_venv_fn():
            if args.uninstall or not args.dry_run:
                print()
                Logger.error("Le script est exécuté depuis le .venv du projet.")

                if platform.system() == "Windows":
                    Logger.info(
                        "Vous êtes dans l'environnement virtuel du projet (.venv). Pour sortir:"
                    )
                    Logger.info("  PowerShell: deactivate")
                    Logger.info("  CMD: deactivate")
                    Logger.info(
                        "Ensuite relancez la commande depuis votre shell utilisateur, par exemple:"
                    )
                    if args.uninstall:
                        Logger.info("  python scripts/install.py --uninstall")
                    else:
                        Logger.info("  python scripts/install.py")
                else:
                    Logger.info(
                        "Vous êtes dans l'environnement virtuel du projet (.venv). Pour sortir:"
                    )
                    Logger.info("  Bash / Zsh: deactivate")
                    Logger.info(
                        "Ensuite relancez la commande depuis votre shell utilisateur, par exemple:"
                    )
                    if args.uninstall:
                        Logger.info("  python3 scripts/install.py --uninstall")
                    else:
                        Logger.info("  python3 scripts/install.py")

                # Block the operation
                raise CLIError(2)

        if args.uninstall:
            Logger.header("DÉSINSTALLATION", "🗑️")
            if manager.check_existing_installation():
                manager.cleanup_existing_installation()
                Logger.success("Désinstallation terminée")
            else:
                Logger.info("Aucune installation trouvée")
            return

        # Vérifications système
        manager.run_system_checks()

        # Installation
        manager.run_installation()

        # Résumé
        manager.show_summary()

    except CLIError:
        # Propagate CLIError as-is; wrapper will handle exit code
        raise
    except KeyboardInterrupt:
        print()
        Logger.error("Installation interrompue par l'utilisateur")
        raise CLIError(1)
    except Exception as e:
        print()
        Logger.error(f"Erreur lors de l'installation: {e}")
        Logger.info("Consultez les logs ci-dessus pour plus de détails")
        raise CLIError(1)


def main():
    """Wrapper CLI: parse args and call core_main; on CLIError map to sys.exit."""
    parser = argparse.ArgumentParser(
        description="Installation automatique d'Alexa Advanced Control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python scripts/install.py                          # Installation normale
  python scripts/install.py --force                  # Force la réinstallation (supprime l'existant)
  python scripts/install.py --skip-tests             # Saute les tests finaux
  python scripts/install.py --dry                    # Simulation (dry-run)
    python scripts/install.py --uninstall              # Désinstallation interactive
  python scripts/install.py --uninstall --force      # Désinstallation sans confirmation
    """,
    )

    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force la réinstallation (supprime l'installation existante)",
    )

    parser.add_argument(
        "--skip-tests", action="store_true", help="Saute les tests de configuration finale"
    )

    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Désinstalle complètement (supprime .venv et nodeenv)",
    )

    parser.add_argument(
        "--dry-run",
        "--dry",
        action="store_true",
        help="Simule les actions sans exécuter (affiche les commandes qui seraient lancées)",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Assume yes for interactive prompts (non-interactive mode)",
    )

    args = parser.parse_args()

    args = parser.parse_args()

    # Détermination du répertoire d'installation
    script_dir = Path(__file__).parent
    install_dir = script_dir.parent

    # Using the top-level helper so tests can import and call it directly
    def _running_in_project_venv() -> bool:
        return running_in_project_venv(sys.executable, install_dir)

    try:
        core_main(args, install_dir, _running_in_project_venv)
    except CLIError as ce:
        # The core already printed context messages; exit with the code
        sys.exit(ce.code)
    except KeyboardInterrupt:  # pragma: no cover - handled in core_main and left for extra safety
        Logger.error("Installation interrompue par l'utilisateur")
        sys.exit(1)


if __name__ == "__main__":
    main()
