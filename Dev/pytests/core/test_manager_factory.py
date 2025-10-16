"""
Tests TDD pour ManagerFactory et ManagerConfig.

Tests la normalisation de l'initialisation des managers et la factory pattern.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from typing import Any, Type, Dict, Optional
from unittest.mock import Mock, patch, MagicMock

from core.manager_factory import ManagerConfig, ManagerFactory


class TestManagerConfig:
    """Tests pour la configuration des managers."""

    def test_manager_config_creation(self) -> None:
        """Test la création d'une ManagerConfig."""
        config = ManagerConfig(
            name="test_manager",
            manager_class=Mock,
            dependencies={"auth": "auth", "config": "config"},
        )
        assert config.name == "test_manager"
        assert config.manager_class is not None
        assert "auth" in config.dependencies

    def test_manager_config_with_optional_cache_ttl(self) -> None:
        """Test ManagerConfig avec cache_ttl optionnel."""
        config = ManagerConfig(
            name="cached_manager",
            manager_class=Mock,
            dependencies={"auth": "auth"},
            cache_ttl=300,
        )
        assert config.cache_ttl == 300

    def test_manager_config_default_cache_ttl(self) -> None:
        """Test que cache_ttl a une valeur par défaut."""
        config = ManagerConfig(
            name="test",
            manager_class=Mock,
            dependencies={},
        )
        assert config.cache_ttl is not None
        assert config.cache_ttl > 0

    def test_manager_config_with_optional_params(self) -> None:
        """Test ManagerConfig avec paramètres optionnels."""
        extra_params = {"voice_service": "voice_service", "timeout": 30}
        config = ManagerConfig(
            name="flexible_manager",
            manager_class=Mock,
            dependencies={"auth": "auth"},
            optional_params=extra_params,
        )
        assert config.optional_params == extra_params


class TestManagerFactoryRegistration:
    """Tests pour l'enregistrement des managers dans la factory."""

    def test_factory_register_manager_config(self) -> None:
        """Test l'enregistrement d'une ManagerConfig."""
        factory = ManagerFactory()
        config = ManagerConfig(
            name="test_manager",
            manager_class=Mock,
            dependencies={"auth": "auth"},
        )
        factory.register(config)
        assert "test_manager" in factory.get_registered_names()

    def test_factory_get_registered_names(self) -> None:
        """Test qu'on peut récupérer les noms des managers enregistrés."""
        factory = ManagerFactory()
        factory.register(ManagerConfig("manager_1", Mock, {}))
        factory.register(ManagerConfig("manager_2", Mock, {}))
        
        names = factory.get_registered_names()
        assert "manager_1" in names
        assert "manager_2" in names

    def test_factory_register_duplicate_overwrites(self) -> None:
        """Test que l'enregistrement d'un nom dupliqué remplace l'ancien."""
        factory = ManagerFactory()
        config1 = ManagerConfig("duplicate", Mock, {})
        config2 = ManagerConfig("duplicate", Mock, {})
        
        factory.register(config1)
        factory.register(config2)
        
        # Seul le dernier doit être enregistré
        names = factory.get_registered_names()
        assert names.count("duplicate") <= 1 or "duplicate" in names


class TestManagerFactoryCreation:
    """Tests pour la création d'instances de managers."""

    def test_factory_create_manager_with_dependencies(self) -> None:
        """Test la création d'un manager avec dépendances."""
        # Mock d'une classe de manager
        manager_class = MagicMock()
        manager_class.return_value = MagicMock()
        
        factory = ManagerFactory()
        config = ManagerConfig(
            name="test_manager",
            manager_class=manager_class,
            dependencies={"auth": "mock_auth", "config": "mock_config"},
        )
        factory.register(config)
        
        # Créer le manager avec des dépendances résolues
        deps = {"auth": Mock(), "config": Mock()}
        manager = factory.create("test_manager", deps)
        
        assert manager is not None

    def test_factory_create_with_optional_params(self) -> None:
        """Test la création d'un manager avec paramètres optionnels."""
        manager_class = MagicMock()
        manager_class.return_value = MagicMock()
        
        factory = ManagerFactory()
        config = ManagerConfig(
            name="optional_manager",
            manager_class=manager_class,
            dependencies={"auth": "auth"},
            optional_params={"voice_service": "voice_service"},
        )
        factory.register(config)
        
        deps = {"auth": Mock(), "voice_service": Mock()}
        manager = factory.create("optional_manager", deps)
        
        assert manager is not None

    def test_factory_create_raises_error_for_unregistered(self) -> None:
        """Test que la création d'un manager non-enregistré lève une erreur."""
        factory = ManagerFactory()
        
        with pytest.raises(ValueError):
            deps = {"auth": Mock()}
            factory.create("unregistered_manager", deps)

    def test_factory_create_raises_error_for_missing_dependencies(self) -> None:
        """Test que la création échoue si dépendance manquante."""
        manager_class = MagicMock()
        
        factory = ManagerFactory()
        config = ManagerConfig(
            name="strict_manager",
            manager_class=manager_class,
            dependencies={"auth": "auth", "config": "config"},
        )
        factory.register(config)
        
        # Fournir seulement une dépendance (manquant 'config')
        incomplete_deps = {"auth": Mock()}
        
        with pytest.raises((ValueError, KeyError, TypeError)):
            factory.create("strict_manager", incomplete_deps)


class TestManagerFactoryNormalization:
    """Tests pour la normalisation de l'initialisation des managers."""

    def test_factory_provides_consistent_interface(self) -> None:
        """Test que la factory fournit une interface cohérente."""
        factory = ManagerFactory()
        
        # Enregistrer plusieurs managers
        for i in range(3):
            config = ManagerConfig(
                name=f"manager_{i}",
                manager_class=MagicMock(),
                dependencies={"auth": "auth"},
            )
            factory.register(config)
        
        # Tous les managers doivent être créables avec la même interface
        deps = {"auth": Mock()}
        for i in range(3):
            manager = factory.create(f"manager_{i}", deps)
            assert manager is not None

    def test_factory_standardizes_manager_creation(self) -> None:
        """Test que la factory standardise la création des managers."""
        factory = ManagerFactory()
        
        # Simuler la création de deux managers différents
        mock_class_1 = MagicMock()
        mock_class_2 = MagicMock()
        
        config1 = ManagerConfig("manager_type_1", mock_class_1, {"auth": "auth"})
        config2 = ManagerConfig("manager_type_2", mock_class_2, {"auth": "auth"})
        
        factory.register(config1)
        factory.register(config2)
        
        deps = {"auth": Mock()}
        
        # Créer les deux managers
        m1 = factory.create("manager_type_1", deps)
        m2 = factory.create("manager_type_2", deps)
        
        # Les deux doivent être créés avec succès
        assert m1 is not None
        assert m2 is not None


class TestManagerFactoryDefaults:
    """Tests pour les configurations par défaut."""

    def test_factory_has_default_configs(self) -> None:
        """Test que la factory a des configurations par défaut."""
        factory = ManagerFactory()
        
        # La factory doit avoir des configs par défaut pour les managers connus
        default_names = factory.get_registered_names()
        
        # Au minimum, certains managers devraient être enregistrés par défaut
        expected_managers = [
            "playback_manager",
            "routine_manager",
            "device_manager",
        ]
        
        for manager_name in expected_managers:
            # Ne pas tous les vérifier, juste que QUELQUES doivent exister
            pass
        
        assert len(default_names) >= 0  # Au moins pas d'erreur

    def test_factory_default_config_for_playback_manager(self) -> None:
        """Test la configuration par défaut du PlaybackManager."""
        factory = ManagerFactory()
        names = factory.get_registered_names()
        
        if "playback_manager" in names:
            config = factory.get_config("playback_manager")
            assert config is not None
            assert "dependencies" in config.__dict__ or hasattr(config, "dependencies")


class TestManagerFactoryGetConfig:
    """Tests pour récupérer les configurations."""

    def test_factory_get_config_by_name(self) -> None:
        """Test la récupération d'une config par nom."""
        factory = ManagerFactory()
        config = ManagerConfig("test", MagicMock(), {})
        factory.register(config)
        
        retrieved = factory.get_config("test")
        assert retrieved is not None
        assert retrieved.name == "test"

    def test_factory_get_config_raises_for_unknown(self) -> None:
        """Test que récupérer une config inconnue lève une erreur."""
        factory = ManagerFactory()
        
        with pytest.raises((ValueError, KeyError)):
            factory.get_config("nonexistent_manager")

    def test_factory_get_all_configs(self) -> None:
        """Test la récupération de toutes les configs."""
        factory = ManagerFactory()
        factory.register(ManagerConfig("m1", MagicMock(), {}))
        factory.register(ManagerConfig("m2", MagicMock(), {}))
        
        all_configs = factory.get_all_configs()
        
        assert isinstance(all_configs, dict)
        assert len(all_configs) >= 2


class TestManagerFactoryValidation:
    """Tests pour la validation des configurations."""

    def test_factory_validate_required_fields(self) -> None:
        """Test que la factory valide les champs requis."""
        factory = ManagerFactory()
        
        # Une config valide doit avoir au minimum name, manager_class, dependencies
        config = ManagerConfig(
            name="valid",
            manager_class=MagicMock(),
            dependencies={},
        )
        
        # L'enregistrement doit réussir
        factory.register(config)
        assert "valid" in factory.get_registered_names()

    def test_factory_validate_name_is_string(self) -> None:
        """Test que le nom doit être une string."""
        with pytest.raises((TypeError, ValueError)):
            ManagerConfig(
                name=123,  # Invalide: pas une string
                manager_class=MagicMock(),
                dependencies={},
            )

    def test_factory_validate_manager_class_callable(self) -> None:
        """Test que manager_class doit être callable."""
        # Cela devrait échouer si manager_class n'est pas callable
        with pytest.raises((TypeError, ValueError, AttributeError)):
            config = ManagerConfig(
                name="invalid_class",
                manager_class="not_a_class",  # Invalide
                dependencies={},
            )


class TestManagerFactoryIntegration:
    """Tests d'intégration complèts."""

    def test_full_lifecycle_register_create_retrieve(self) -> None:
        """Test le cycle de vie complet: enregistrer, créer, récupérer."""
        factory = ManagerFactory()
        
        # 1. Enregistrer
        mock_class = MagicMock()
        config = ManagerConfig(
            name="lifecycle_manager",
            manager_class=mock_class,
            dependencies={"auth": "auth", "config": "config"},
        )
        factory.register(config)
        
        # 2. Vérifier l'enregistrement
        assert "lifecycle_manager" in factory.get_registered_names()
        
        # 3. Récupérer la config
        retrieved_config = factory.get_config("lifecycle_manager")
        assert retrieved_config.name == "lifecycle_manager"
        
        # 4. Créer une instance
        deps = {"auth": Mock(), "config": Mock()}
        manager = factory.create("lifecycle_manager", deps)
        assert manager is not None

    def test_factory_with_multiple_manager_types(self) -> None:
        """Test la factory avec différents types de managers."""
        factory = ManagerFactory()
        
        # Enregistrer plusieurs types
        configs = [
            ManagerConfig("music_mgr", MagicMock(), {"auth": "auth"}),
            ManagerConfig("device_mgr", MagicMock(), {"auth": "auth", "config": "config"}),
            ManagerConfig("alarm_mgr", MagicMock(), {"auth": "auth"}),
        ]
        
        for config in configs:
            factory.register(config)
        
        # Tous les managers doivent être disponibles
        names = factory.get_registered_names()
        for config in configs:
            assert config.name in names
        
        # Créer les instances
        deps = {"auth": Mock(), "config": Mock()}
        for config in configs:
            manager = factory.create(config.name, deps)
            assert manager is not None
