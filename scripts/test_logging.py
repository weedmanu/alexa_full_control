#!/usr/bin/env python3
"""
Script de test pour le système de logging Loguru.

Teste tous les niveaux de log et affiche des exemples.
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils.logger import setup_loguru_logger
    from loguru import logger

    LOGURU_AVAILABLE = True
except ImportError:
    print("⚠️  Loguru non disponible. Installation: pip install loguru")
    sys.exit(1)


def test_basic_logging():
    """Test des niveaux de log de base."""
    print("\n" + "=" * 80)
    print("TEST 1: Niveaux de log de base")
    print("=" * 80 + "\n")

    # Configuration
    setup_loguru_logger(level="DEBUG")

    # Tests des différents niveaux
    logger.debug("Message de débogage - détails techniques")
    logger.info("Message d'information - étape normale")
    logger.success("Message de succès - opération réussie")
    logger.warning("Message d'avertissement - attention requise")
    logger.error("Message d'erreur - problème détecté")

    print()


def test_with_context():
    """Test avec informations de contexte."""
    print("\n" + "=" * 80)
    print("TEST 2: Messages avec contexte")
    print("=" * 80 + "\n")

    logger.info("Initialisation de la configuration")
    logger.debug("Langue: fr_FR")
    logger.debug("Domaine Amazon: amazon.fr")
    logger.debug("Timeout API: 30s")

    logger.success("Configuration initialisée")

    print()


def test_module_simulation():
    """Simule les logs de différents modules."""
    print("\n" + "=" * 80)
    print("TEST 3: Simulation de modules")
    print("=" * 80 + "\n")

    # Simuler core.config
    logger.bind(module="core.config").info("✅ Configuration initialisée")
    logger.bind(module="core.config").debug("📋 Configuration:")
    logger.bind(module="core.config").debug("  - Langue: fr_FR")

    # Simuler core.state_machine
    logger.bind(module="core.state_machine").info("🔧 State Machine initialisée: DISCONNECTED")

    # Simuler core.circuit_breaker
    logger.bind(module="core.circuit_breaker").info(
        "🔧 Circuit Breaker initialisé: threshold=3, timeout=30.0s"
    )

    # Simuler services.cache_service
    logger.bind(module="services.cache_service").debug("Metadata chargé: 2 entrée(s)")
    logger.bind(module="services.cache_service").info(
        "💾 Cache saved (compressed): devices (TTL: 3600s, 16137→3446 bytes, -78.6%)"
    )

    # Simuler services.sync_service
    logger.bind(module="services.sync_service").success("✅ 8 appareils Alexa synchronisés")
    logger.bind(module="services.sync_service").success(
        "🎉 Synchronisation appareils terminée: 8 éléments en 0.8s"
    )

    print()


def test_installation_flow():
    """Simule un flux d'installation complet."""
    print("\n" + "=" * 80)
    print("TEST 4: Flux d'installation simulé")
    print("=" * 80 + "\n")

    logger.info("🚀 INSTALLATION ALEXA ADVANCED CONTROL")
    logger.info("")

    logger.info("🔍 VÉRIFICATIONS SYSTÈME")
    logger.info("Vérification de Python")
    logger.success("Python 3.11.0 détecté")

    logger.info("Vérification de pip")
    logger.success("pip disponible (pip 25.2)")

    logger.info("Vérification de l'espace disque")
    logger.success("125.3 GB disponibles")

    logger.info("")
    logger.info("🐍 ENVIRONNEMENT PYTHON")
    logger.info("Création de l'environnement virtuel")
    logger.success("Environnement virtuel créé")

    logger.info("Mise à jour de pip")
    logger.success("pip mis à jour")

    logger.info("")
    logger.info("📦 DÉPENDANCES PYTHON")
    logger.info("Installation depuis requirements.txt")
    logger.success("Packages Python installés")

    logger.info("")
    logger.info("🟢 ENVIRONNEMENT NODE.JS")
    logger.info("Installation de Node.js v20.17.0")
    logger.success("Node.js v20.17.0 installé")

    logger.info("Installation des packages npm")
    logger.success("alexa-cookie2 installé")
    logger.success("yargs installé")

    logger.info("")
    logger.info("⚙️ CONFIGURATION FINALE")
    logger.info("Création du dossier data")
    logger.success("Dossier data créé")

    logger.info("Test de la configuration")
    logger.success("Test Python réussi (Python 3.11.0)")
    logger.success("Test Node.js réussi")

    logger.info("")
    logger.success("🎉 INSTALLATION TERMINÉE")

    print()


def test_error_handling():
    """Test de la gestion des erreurs."""
    print("\n" + "=" * 80)
    print("TEST 5: Gestion des erreurs")
    print("=" * 80 + "\n")

    try:
        logger.info("Tentative d'opération risquée...")
        # Simuler une erreur
        raise ValueError("Exemple d'erreur pour le test")
    except Exception as e:
        logger.error(f"Erreur détectée: {e}")
        logger.warning("L'opération sera réessayée")

    print()


def test_with_file_logging():
    """Test avec sauvegarde dans un fichier."""
    print("\n" + "=" * 80)
    print("TEST 6: Logging vers fichier")
    print("=" * 80 + "\n")

    log_file = project_root / "logs" / "test_install.log"

    # Reconfigurer avec fichier
    setup_loguru_logger(log_file=log_file, level="DEBUG")

    logger.info(f"Logs également sauvegardés dans: {log_file}")
    logger.debug("Ce message sera dans le fichier en mode DEBUG")
    logger.success("Logging vers fichier testé avec succès")

    print()


def main():
    """Exécute tous les tests."""
    print("\n" + "=" * 80)
    print("🧪 TEST DU SYSTÈME DE LOGGING LOGURU")
    print("=" * 80)

    test_basic_logging()
    test_with_context()
    test_module_simulation()
    test_installation_flow()
    test_error_handling()
    test_with_file_logging()

    print("\n" + "=" * 80)
    print("✅ TOUS LES TESTS TERMINÉS")
    print("=" * 80 + "\n")

    print("📝 Notes:")
    print("  - Les émojis doivent s'afficher correctement")
    print("  - Les couleurs doivent être visibles (si terminal compatible)")
    print("  - Le format doit être: YYYY-MM-DD HH:mm:ss | emoji LEVEL | module:function:line | message")
    print()


if __name__ == "__main__":
    main()
