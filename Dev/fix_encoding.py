#!/usr/bin/env python3
"""
Script de correction automatique des problèmes d'encodage UTF-8.
Corrige les caractères corrompus dans tous les fichiers Python du projet.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Dictionnaire des corrections d'encodage
ENCODING_FIXES = {
    '…': 'à',  # à
    '…': 'â',  # â
    '…': 'ä',  # ä
    '…': 'é',  # é
    '…': 'è',  # è
    '…': 'ê',  # ê
    '…': 'ë',  # ë
    '…': 'ï',  # ï
    '…': 'î',  # î
    '…': 'ô',  # ô
    '…': 'ö',  # ö
    '…': 'ù',  # ù
    '…': 'û',  # û
    '…': 'ü',  # ü
    '…': 'ÿ',  # ÿ
    '…': 'ç',  # ç
    '…': 'À',  # À
    '…': 'Â',  # Â
    '…': 'Ä',  # Ä
    '…': 'É',  # É
    '…': 'È',  # È
    '…': 'Ê',  # Ê
    '…': 'Ë',  # Ë
    '…': 'Ï',  # Ï
    '…': 'Î',  # Î
    '…': 'Ô',  # Ô
    '…': 'Ö',  # Ö
    '…': 'Ù',  # Ù
    '…': 'Û',  # Û
    '…': 'Ü',  # Ü
    '…': 'Ÿ',  # Ÿ
    '…': 'Ç',  # Ç
    '…': 'œ',  # œ
    '…': 'Œ',  # Œ
    '…': 'æ',  # æ
    '…': 'Æ',  # Æ
    '…': "'",  # '
    '…': '"',  # "
    '…': '-',  # –
    '…': '-',  # —
    '…': '…',  # …
    '…': '€',  # €
    '…': '£',  # £
    '…': '°',  # °
    '…': '©',  # ©
    '…': '®',  # ®
    '…': '™',  # ™
    '…': '•',  # •
    '…': '·',  # ·
    '…': '§',  # §
    '…': '¶',  # ¶
    '…': '†',  # †
    '…': '‡',  # ‡
    '…': '‰',  # ‰
    '…': '‹',  # ‹
    '…': '›',  # ›
    '…': '«',  # «
    '…': '»',  # »
    '…': '„',  # „
    '…': '‚',  # ‚
    '…': "'",  # '
    '…': "'",  # '
    '…': '"',  # "
    '…': '"',  # "
    '…': '–',  # –
    '…': '—',  # —
    '…': '…',  # …
}

def find_python_files(root_dir: str, exclude_dirs: List[str] = None) -> List[Path]:
    """Trouve tous les fichiers Python dans le répertoire, en excluant certains dossiers."""
    if exclude_dirs is None:
        exclude_dirs = ['.venv', '__pycache__', '.git', 'node_modules', 'cache', 'nodeenv', 'Dev']

    python_files: List[Path] = []

    for root, dirs, files in os.walk(root_dir):
        # Exclure les dossiers spécifiés
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)

    return python_files

def detect_corrupted_chars(content: str) -> List[Tuple[str, int, int]]:
    """Détecte les caractères corrompus dans le contenu."""
    corrupted = []

    # Chercher tous les caractères non-ASCII qui pourraient être corrompus
    for match in re.finditer(r'[^\x00-\x7F]', content):
        char = match.group()
        pos = match.start()

        # Si c'est un caractère de remplacement (…), c'est probablement corrompu
        if char == '…':
            corrupted.append((char, pos, pos + 1))

    return corrupted

def fix_encoding_issues(content: str) -> Tuple[str, int]:
    """Corrige les problèmes d'encodage dans le contenu."""
    fixed_content = content
    fixes_count = 0

    # Remplacer tous les caractères corrompus connus
    for corrupted_char, replacement in ENCODING_FIXES.items():
        if corrupted_char in fixed_content:
            count = fixed_content.count(corrupted_char)
            fixed_content = fixed_content.replace(corrupted_char, replacement)
            fixes_count += count

    return fixed_content, fixes_count

def process_file(file_path: Path) -> Tuple[bool, int]:
    """Traite un fichier individuel pour corriger les problèmes d'encodage."""
    try:
        # Lire le fichier avec encodage UTF-8
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            original_content = f.read()

        # Détecter les caractères corrompus
        corrupted_chars = detect_corrupted_chars(original_content)

        if not corrupted_chars:
            return True, 0

        # Corriger les problèmes d'encodage
        fixed_content, fixes_count = fix_encoding_issues(original_content)

        if fixes_count > 0:
            # Écrire le contenu corrigé
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            print(f"✅ Corrigé {fixes_count} caractères dans {file_path}")
            return True, fixes_count
        else:
            return True, 0

    except Exception as e:
        print(f"❌ Erreur lors du traitement de {file_path}: {e}")
        return False, 0

def main():
    """Fonction principale."""
    print("=== Script de correction automatique UTF-8 ===")

    # Répertoire racine du projet
    root_dir = Path(__file__).parent

    # Trouver tous les fichiers Python
    print("Recherche des fichiers Python...")
    python_files = find_python_files(str(root_dir))

    print(f"Trouvé {len(python_files)} fichiers Python à analyser.")

    # Traiter chaque fichier
    total_fixes = 0
    processed_files = 0
    error_files = 0

    for file_path in python_files:
        success, fixes = process_file(file_path)
        if success:
            processed_files += 1
            total_fixes += fixes
        else:
            error_files += 1

    # Résumé
    print("\n=== Résumé ===")
    print(f"Fichiers traités: {processed_files}")
    print(f"Fichiers avec erreurs: {error_files}")
    print(f"Total des corrections: {total_fixes}")

    if total_fixes > 0:
        print("\n✅ Corrections terminées avec succès!")
        print("Vous pouvez maintenant tester votre code.")
    else:
        print("\nℹ️  Aucun problème d'encodage détecté.")

    return 0 if error_files == 0 else 1

if __name__ == "__main__":
    exit(main())