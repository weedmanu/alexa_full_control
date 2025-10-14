"""
Module CLI principal pour les tests.

Ce module expose la fonction main() depuis le fichier racine 'alexa'
pour permettre aux tests de l'importer facilement.
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importer la fonction main depuis le fichier racine
try:
    import alexa

    main = alexa.main
except ImportError:
    # Fallback si l'import échoue
    def main():
        print("❌ Erreur: Module CLI principal non trouvé")
        return 1


__all__ = ["main"]
