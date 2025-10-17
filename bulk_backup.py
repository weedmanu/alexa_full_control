#!/usr/bin/env python3
"""
Script de sauvegarde sécurisée avant corrections d'encodage UTF-8.
Crée un commit de sauvegarde avec l'état actuel du code avant les corrections.
Version de test - 17 octobre 2025
"""

import subprocess
import sys
import datetime
from pathlib import Path
from typing import Tuple, Optional

def run_command(command: str, cwd: Optional[str] = None) -> Tuple[bool, str, str]:
    """Exécute une commande et retourne le résultat."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def get_git_status() -> Tuple[bool, Optional[str]]:
    """Vérifie l'état du dépôt git."""
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        print(f"Erreur git status: {stderr}")
        return False, None

    return True, stdout

def create_backup_commit(message_suffix: str = "") -> bool:
    """Crée un commit de sauvegarde."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Vérifier s'il y a des changements
    success, status_output = get_git_status()
    if not success:
        return False

    if status_output is None or not status_output.strip():
        print("Aucun changement à commiter.")
        return True

    # Ajouter tous les fichiers modifiés
    print("Ajout des fichiers modifiés...")
    success, _, stderr = run_command("git add .")
    if not success:
        print(f"Erreur lors de l'ajout des fichiers: {stderr}")
        return False

    # Créer le commit
    commit_message = f"BACKUP: Sauvegarde avant corrections UTF-8 {timestamp}"
    if message_suffix:
        commit_message += f" - {message_suffix}"

    print(f"Création du commit: {commit_message}")
    success, _, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"Erreur lors du commit: {stderr}")
        return False

    print("✅ Commit de sauvegarde créé avec succès!")
    return True

def main():
    """Fonction principale."""
    print("=== Script de sauvegarde avant corrections UTF-8 ===")

    # Vérifier que nous sommes dans un dépôt git
    success, _, stderr = run_command("git rev-parse --git-dir")
    if not success:
        print("Erreur: Ce n'est pas un dépôt git valide.")
        sys.exit(1)

    # Obtenir le répertoire racine du projet
    success, git_root, stderr = run_command("git rev-parse --show-toplevel")
    if not success:
        print(f"Erreur lors de la récupération de la racine git: {stderr}")
        sys.exit(1)

    project_root = Path(git_root)

    # Se positionner dans la racine du projet
    import os
    os.chdir(project_root)

    # Vérifier l'état du dépôt
    print("Vérification de l'état du dépôt...")
    success, status = get_git_status()
    if not success:
        sys.exit(1)

    if status is None or not status.strip():
        print("Aucun changement détecté. Sauvegarde inutile.")
        sys.exit(0)

    print("Fichiers modifiés:")
    for line in status.split('\n'):
        if line.strip():
            print(f"  {line}")

    # Créer automatiquement le commit de sauvegarde
    print("\nCréation automatique du commit de sauvegarde...")
    if create_backup_commit("corrections encodage UTF-8"):
        print("\n✅ Sauvegarde terminée avec succès!")
        print("Vous pouvez maintenant procéder aux corrections d'encodage UTF-8.")
    else:
        print("\n❌ Échec de la sauvegarde!")
        sys.exit(1)

if __name__ == "__main__":
    main()