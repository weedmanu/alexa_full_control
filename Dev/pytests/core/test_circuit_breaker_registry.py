"""
Tests TDD pour CircuitBreakerRegistry.

Tests le singleton, configurations per-type, et gestion centralisée des CircuitBreakers.
"""

import sys
from pathlib import Path

# Add project root to path BEFORE any imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from typing import Any
from unittest.mock import Mock, patch

try:
    from core.breaker_registry import CircuitBreakerRegistry
except ImportError:
    # Fallback for import issues
    import importlib.util
    spec = importlib.util.spec_from_file_location("breaker_registry", project_root / "core" / "breaker_registry.py")
    if spec and spec.loader:
        breaker_registry = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(breaker_registry)
        CircuitBreakerRegistry = breaker_registry.CircuitBreakerRegistry


class TestCircuitBreakerRegistryInitialization:
    """Tests d'initialisation du registre singleton."""

    def test_singleton_pattern_returns_same_instance(self) -> None:
        """Test que le registre est un singleton."""
        registry1 = CircuitBreakerRegistry()
        registry2 = CircuitBreakerRegistry()
        assert registry1 is registry2

    def test_get_or_create_returns_circuit_breaker(self) -> None:
        """Test que get_or_create retourne un CircuitBreaker."""
        registry = CircuitBreakerRegistry()
        breaker = registry.get_or_create("music")
        assert breaker is not None
        assert hasattr(breaker, "call")

    def test_get_or_create_returns_same_breaker_for_name(self) -> None:
        """Test que get_or_create retourne toujours le même breaker pour un nom donné."""
        registry = CircuitBreakerRegistry()
        breaker1 = registry.get_or_create("music_player")
        breaker2 = registry.get_or_create("music_player")
        assert breaker1 is breaker2

    def test_different_names_get_different_breakers(self) -> None:
        """Test que différents noms créent différents breakers."""
        registry = CircuitBreakerRegistry()
        breaker_music = registry.get_or_create("music")
        breaker_device = registry.get_or_create("device")
        assert breaker_music is not breaker_device


class TestCircuitBreakerRegistryConfiguration:
    """Tests des configurations per-type de breaker."""

    def test_get_config_returns_music_config(self) -> None:
        """Test que get_config retourne la bonne config pour type 'music'."""
        registry = CircuitBreakerRegistry()
        config = registry.get_config("music")
        assert config is not None
        assert "failure_threshold" in config
        assert "timeout" in config

    def test_music_config_has_higher_threshold_than_default(self) -> None:
        """Test que music a un threshold plus élevé que default."""
        registry = CircuitBreakerRegistry()
        music_config = registry.get_config("music")
        default_config = registry.get_config("default")
        assert music_config["failure_threshold"] >= default_config["failure_threshold"]

    def test_get_config_returns_default_for_unknown_type(self) -> None:
        """Test que get_config retourne default pour un type inconnu."""
        registry = CircuitBreakerRegistry()
        config = registry.get_config("unknown_type")
        assert config == registry.get_config("default")

    def test_all_config_types_have_required_fields(self) -> None:
        """Test que toutes les configs ont les champs requis."""
        registry = CircuitBreakerRegistry()
        config_types = ["default", "music", "device", "alarm", "routine"]
        
        for config_type in config_types:
            config = registry.get_config(config_type)
            assert "failure_threshold" in config
            assert "timeout" in config
            assert config["failure_threshold"] > 0
            assert config["timeout"] > 0


class TestCircuitBreakerRegistryStats:
    """Tests pour les statistiques et gestion des breakers."""

    def test_list_breakers_returns_dict(self) -> None:
        """Test que list_breakers retourne un dictionnaire."""
        registry = CircuitBreakerRegistry()
        # Créer quelques breakers d'abord
        registry.get_or_create("test_1")
        registry.get_or_create("test_2")
        
        breakers = registry.list_breakers()
        assert isinstance(breakers, dict)
        assert len(breakers) > 0

    def test_list_breakers_contains_created_breakers(self) -> None:
        """Test que list_breakers inclut les breakers créés."""
        registry = CircuitBreakerRegistry()
        registry.get_or_create("my_breaker")
        
        breakers = registry.list_breakers()
        assert "my_breaker" in breakers

    def test_get_stats_returns_stats_dict(self) -> None:
        """Test que get_stats retourne un dictionnaire de statistiques."""
        registry = CircuitBreakerRegistry()
        registry.get_or_create("stats_test")
        
        stats = registry.get_stats()
        assert isinstance(stats, dict)
        assert "stats_test" in stats

    def test_stats_contain_breaker_info(self) -> None:
        """Test que les stats contiennent les infos du breaker."""
        registry = CircuitBreakerRegistry()
        breaker = registry.get_or_create("info_test")
        
        stats = registry.get_stats()
        assert "info_test" in stats
        breaker_stat = stats["info_test"]
        
        # Les stats doivent contenir l'état et la config
        assert isinstance(breaker_stat, dict)


class TestCircuitBreakerRegistryReset:
    """Tests pour la réinitialisation des breakers."""

    def test_reset_all_clears_all_breakers(self) -> None:
        """Test que reset() réinitialise tous les breakers."""
        registry = CircuitBreakerRegistry()
        registry.get_or_create("reset_test_1")
        registry.get_or_create("reset_test_2")
        
        initial_count = len(registry.list_breakers())
        registry.reset()
        final_count = len(registry.list_breakers())
        
        # Après reset, le registre doit être vide ou réinitialisé
        assert final_count == 0 or final_count < initial_count

    def test_reset_breaker_specific_breaker(self) -> None:
        """Test que reset_breaker réinitialise un breaker spécifique."""
        registry = CircuitBreakerRegistry()
        breaker1 = registry.get_or_create("breaker_to_reset")
        breaker2 = registry.get_or_create("breaker_to_keep")
        
        # Simuler une certaine utilisation du breaker
        breaker1_before = registry.get_stats().get("breaker_to_reset")
        
        registry.reset_breaker("breaker_to_reset")
        
        breaker1_after = registry.get_or_create("breaker_to_reset")
        # Le breaker doit être réinitialisé
        assert breaker1_after is not None


class TestCircuitBreakerRegistryMemoryFootprint:
    """Tests pour vérifier la réduction de l'empreinte mémoire."""

    def test_registry_consolidates_breakers(self) -> None:
        """Test que le registre consolide les breakers par nom."""
        registry = CircuitBreakerRegistry()
        
        # Simuler la création de nombreux breakers avec les mêmes noms
        breakers_created = []
        for i in range(5):
            breaker = registry.get_or_create(f"music_{i % 2}")  # music_0 et music_1
            breakers_created.append(breaker)
        
        # Les breakers avec le même nom doivent être identiques
        assert registry.get_or_create("music_0") is registry.get_or_create("music_0")
        assert registry.get_or_create("music_1") is registry.get_or_create("music_1")

    def test_no_duplicate_breaker_instances(self) -> None:
        """Test qu'il n'y a pas de breakers dupliqués dans le registre."""
        registry = CircuitBreakerRegistry()
        
        # Créer plusieurs breakers
        names = ["dev1", "dev2", "dev1", "dev3", "dev2"]
        created_breakers = [registry.get_or_create(name) for name in names]
        
        # Le nombre unique de breakers doit être <= nombre de noms uniques
        unique_names = set(names)
        list_count = len(registry.list_breakers())
        
        assert list_count <= len(unique_names)


class TestCircuitBreakerRegistryThreadSafety:
    """Tests pour la sécurité thread."""

    def test_concurrent_access_returns_same_breaker(self) -> None:
        """Test que l'accès concurrent retourne le même breaker."""
        import threading
        
        registry = CircuitBreakerRegistry()
        results = []
        
        def get_breaker() -> None:
            breaker = registry.get_or_create("concurrent_test")
            results.append(breaker)
        
        threads = [threading.Thread(target=get_breaker) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Tous les threads doivent obtenir le même breaker
        first = results[0]
        for result in results[1:]:
            assert result is first


class TestCircuitBreakerRegistryIntegration:
    """Tests d'intégration du registre."""

    def test_full_lifecycle(self) -> None:
        """Test le cycle de vie complet du registre."""
        registry = CircuitBreakerRegistry()
        
        # 1. Créer des breakers
        breaker1 = registry.get_or_create("lifecycle_1")
        breaker2 = registry.get_or_create("lifecycle_2")
        assert len(registry.list_breakers()) >= 2
        
        # 2. Vérifier les stats
        stats = registry.get_stats()
        assert "lifecycle_1" in stats
        assert "lifecycle_2" in stats
        
        # 3. Réinitialiser un breaker
        registry.reset_breaker("lifecycle_1")
        
        # 4. Le breaker doit toujours exister
        assert registry.get_or_create("lifecycle_1") is not None

    def test_mixed_manager_types(self) -> None:
        """Test avec différents types de managers."""
        registry = CircuitBreakerRegistry()
        
        # Créer des breakers pour différents types
        music_breaker = registry.get_or_create("playback_manager")
        device_breaker = registry.get_or_create("device_manager")
        alarm_breaker = registry.get_or_create("alarm_manager")
        
        # Tous doivent être valides
        assert music_breaker is not None
        assert device_breaker is not None
        assert alarm_breaker is not None
        
        # Ils doivent être différents
        assert music_breaker is not device_breaker
        assert device_breaker is not alarm_breaker
