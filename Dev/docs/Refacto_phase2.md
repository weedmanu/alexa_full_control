# Phase 2: PROFESSIONAL REFACTORING PROMPT - Configuration Externalization

**Project**: Alexa Voice Control CLI  
**Objective**: Phase 2 - Centralize Configuration  
**Methodology**: TDD + Configuration as Code  
**Depends On**: Phase 1 (AlexaAPIService) COMPLETE  
**Duration**: 1-2 sprints (10 days)

---

## 📋 EXECUTIVE BRIEF

### Context
Current configuration is dispersed throughout code:
- Hardcoded domains in `alexa_auth.py` (amazon.fr default)
- Endpoints hardcoded in endpoint strings
- Timeouts, retries missing or scattered
- Multi-region support absent
- Environment-specific configs impossible
- Makes deployment and testing difficult

### Goal
Create centralized configuration system using Pydantic Settings + YAML files, enabling:
- Single source for all tunable parameters
- Easy environment switching (dev/staging/prod)
- Multi-region support (US/EU/DE)
- No code changes for configuration updates

### Success Criteria
- ✅ All config loaded from YAML files
- ✅ Environment variable override support
- ✅ Pydantic-Settings for type validation
- ✅ Config documentation auto-generated
- ✅ All existing tests pass (88/88 + new ones)
- ✅ Configuration accessible everywhere (singleton pattern)
- ✅ No hardcodes in code (audit script confirms)
- ✅ Dev/staging/prod configs provided
- ✅ Zero tech debt from Phase 1 carried over

---

## 🎯 PHASE 2 DETAILED BREAKDOWN

### 2.1 Requirements & Dependencies Analysis (1-2 days)

**Objective**: Understand what needs to be configurable

**Tasks**:

```bash
# Task 2.1.1: Audit current hardcodes
grep -r "amazon\.fr\|amazon\.com\|amazon\.de\|timeout\|retry" \
  --include="*.py" services/ core/ alexa_auth/ | tee config_audit.txt

# Task 2.1.2: Extract all tunable parameters
# Look for:
# - Domain/region settings
# - API timeouts
# - Retry counts/delays
# - Circuit breaker thresholds
# - Cache TTLs
# - Logging levels
# - Feature flags

# Task 2.1.3: Create requirements document
cat > docs/config_requirements.md << 'EOF'
# Configuration Requirements

## API Configuration
- amazon_domain: str (default: amazon.fr)
- api_base_url: str (constructed from domain)
- request_timeout: int (seconds)
- max_retries: int
- retry_delay: float (seconds)

## Circuit Breaker
- failure_threshold: int
- recovery_timeout: int

## Cache
- default_ttl: int
- compression_enabled: bool

## Authentication
- cache_dir: str
- session_file: str

## Logging
- level: str (DEBUG, INFO, WARNING)
- format: str
- output_file: str

## Multi-region Mapping
- regions: dict[str, dict] (us, eu, de, etc)
EOF
```

**Deliverables**:
- `config_audit.txt` - All current hardcodes
- `docs/config_requirements.md` - What to configure
- `requirements_update.txt` - New pip packages needed

**New Dependencies** (add to requirements.txt):
```
pydantic-settings>=2.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
```

**Definition of Done**:
- [ ] All hardcodes identified
- [ ] Requirements documented
- [ ] New packages listed
- [ ] Approved by team lead

---

### 2.2 Design Configuration System (2-3 days)

**Objective**: Architecture before implementation

**Design Document** (`docs/design_config_system.md`):

```markdown
# Configuration System Design

## Architecture

### Structure
- `config/base.yaml` - Default/base configuration
- `config/amazon_domains.yaml` - Multi-region endpoint mappings
- `config/dev.yaml` - Development overrides
- `config/staging.yaml` - Staging overrides
- `config/prod.yaml` - Production overrides
- `.env` - Local environment variables (git-ignored)

### Loading Strategy
1. Load base.yaml (base defaults)
2. Load environment-specific override (dev/staging/prod)
3. Override with environment variables if present
4. Validate with Pydantic-Settings

### Config Classes (Pydantic Models)

```python
class APIConfig(BaseSettings):
    """API configuration"""
    amazon_domain: str
    request_timeout: int = 10
    max_retries: int = 3
    retry_delay: float = 0.5

class CircuitBreakerConfig(BaseSettings):
    """Circuit breaker resilience"""
    failure_threshold: int = 5
    recovery_timeout: int = 60

class Settings(BaseSettings):
    """Root configuration"""
    api: APIConfig
    circuit_breaker: CircuitBreakerConfig
    cache: CacheConfig
    logging: LoggingConfig
    regions: Dict[str, Dict[str, str]]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### Usage Pattern

```python
# Load once at startup
from utils.config import get_config

config = get_config()  # Singleton

# Use everywhere
timeout = config.api.request_timeout
domain = config.get_region("eu").get("domain")
```

### Priority Order (highest to lowest)
1. Environment variables (CLI override)
2. .env file (local development)
3. config/{ENVIRONMENT}.yaml (environment-specific)
4. config/base.yaml (defaults)

### Environment Detection
```python
ENVIRONMENT = os.getenv("ALEXA_ENV", "dev")
# Loads: base.yaml + {ENVIRONMENT}.yaml
```
```

**Deliverables**:
- `docs/design_config_system.md`
- Architecture diagram (ASCII)
- Pydantic model structure diagram

---

### 2.3 Create Configuration Files (1-2 days)

**File**: `config/base.yaml`
```yaml
# Base configuration - defaults used everywhere
api:
  request_timeout: 10
  max_retries: 3
  retry_delay: 0.5
  amazon_domain: "amazon.fr"

circuit_breaker:
  failure_threshold: 5
  recovery_timeout: 60

cache:
  enabled: true
  compression: true
  default_ttl: 3600
  directory: "data/cache"

logging:
  level: "INFO"
  format: "json"
  file: "logs/alexa.log"

auth:
  cache_dir: "data/auth"
  session_file: "session.cache"
```

**File**: `config/amazon_domains.yaml`
```yaml
# Multi-region endpoint mappings
regions:
  us:
    domain: "amazon.com"
    api_endpoint: "https://alexa.amazon.com"
    auth_endpoint: "https://login.amazon.com"
    
  eu:
    domain: "amazon.eu"
    api_endpoint: "https://alexa.amazon.eu"
    auth_endpoint: "https://login.amazon.eu"
    
  de:
    domain: "amazon.de"
    api_endpoint: "https://alexa.amazon.de"
    auth_endpoint: "https://login.amazon.de"
    
  uk:
    domain: "amazon.co.uk"
    api_endpoint: "https://alexa.amazon.co.uk"
    auth_endpoint: "https://login.amazon.co.uk"
    
  fr:
    domain: "amazon.fr"
    api_endpoint: "https://alexa.amazon.fr"
    auth_endpoint: "https://login.amazon.fr"
```

**File**: `config/dev.yaml`
```yaml
# Development overrides
api:
  request_timeout: 20  # More lenient in dev
  max_retries: 5

logging:
  level: "DEBUG"
  file: "logs/alexa_dev.log"

cache:
  compression: false  # Easier to inspect in dev
```

**File**: `config/staging.yaml`
```yaml
# Staging overrides
api:
  request_timeout: 15

logging:
  level: "INFO"

cache:
  default_ttl: 1800  # Shorter TTL for testing
```

**File**: `config/prod.yaml`
```yaml
# Production overrides
api:
  request_timeout: 10
  max_retries: 2  # Fail fast in production

logging:
  level: "WARNING"  # Less verbose

circuit_breaker:
  recovery_timeout: 120  # Longer recovery
```

**File**: `.env.example` (commit this, not .env)
```bash
# Environment Configuration
ALEXA_ENV=dev
ALEXA_DOMAIN=amazon.fr
ALEXA_API_TIMEOUT=10
ALEXA_LOG_LEVEL=DEBUG

# Optional: Override specific settings
# ALEXA_API_REQUEST_TIMEOUT=15
```

---

### 2.4 Implement Configuration Loader - TDD (2-3 days)

#### 2.4.1 Write Tests First

**File**: `Dev/pytests/utils/test_config_loader.py`

```python
"""Tests for configuration loading system"""

import os
import pytest
from pathlib import Path
from utils.config import get_config, ConfigManager


class TestConfigInitialization:
    """Test configuration system initialization"""
    
    def test_config_loads_base_yaml(self):
        """Config should load base.yaml"""
        config = get_config()
        assert config is not None
        assert hasattr(config, 'api')
        assert hasattr(config, 'circuit_breaker')
    
    def test_config_is_singleton(self):
        """Config should be singleton - same instance"""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2
    
    def test_config_has_required_sections(self):
        """Config must have all required top-level sections"""
        config = get_config()
        required = ['api', 'circuit_breaker', 'cache', 'logging', 'auth']
        for section in required:
            assert hasattr(config, section)


class TestAPIConfiguration:
    """Test API configuration"""
    
    def test_api_timeout_defaults_to_10(self):
        """API timeout should default to 10 seconds"""
        config = get_config()
        assert config.api.request_timeout == 10
    
    def test_api_domain_configurable(self):
        """API domain should be configurable"""
        config = get_config()
        assert config.api.amazon_domain in ['amazon.fr', 'amazon.com']
    
    def test_api_retries_configurable(self):
        """Retry count should be configurable"""
        config = get_config()
        assert config.api.max_retries > 0


class TestEnvironmentOverrides:
    """Test environment variable overrides"""
    
    def test_env_var_overrides_yaml(self, monkeypatch):
        """Environment variables should override YAML"""
        monkeypatch.setenv('ALEXA_API_REQUEST_TIMEOUT', '20')
        
        # Reload config
        config = ConfigManager.reload()
        
        assert config.api.request_timeout == 20
    
    def test_alexa_env_switches_config_file(self, monkeypatch):
        """ALEXA_ENV variable should switch config file"""
        monkeypatch.setenv('ALEXA_ENV', 'staging')
        config = ConfigManager.reload()
        
        # Staging has different defaults
        # (depends on actual staging.yaml)
        assert config is not None


class TestMultiRegionSupport:
    """Test multi-region configuration"""
    
    def test_regions_loaded(self):
        """All regions should be loaded"""
        config = get_config()
        assert len(config.regions) >= 3
        assert 'us' in config.regions
        assert 'eu' in config.regions
        assert 'de' in config.regions
    
    def test_get_region_returns_config(self):
        """get_region should return region config"""
        config = get_config()
        us_config = config.get_region('us')
        
        assert us_config is not None
        assert 'domain' in us_config
        assert 'api_endpoint' in us_config
    
    def test_invalid_region_raises_error(self):
        """Invalid region should raise KeyError"""
        config = get_config()
        
        with pytest.raises(KeyError):
            config.get_region('invalid_region')


class TestCacheConfiguration:
    """Test cache configuration"""
    
    def test_cache_ttl_configurable(self):
        """Cache TTL should be configurable"""
        config = get_config()
        assert config.cache.default_ttl > 0
    
    def test_cache_compression_configurable(self):
        """Cache compression should be toggleable"""
        config = get_config()
        assert isinstance(config.cache.compression, bool)


class TestValidation:
    """Test configuration validation"""
    
    def test_invalid_timeout_raises_error(self, monkeypatch):
        """Negative timeout should fail validation"""
        monkeypatch.setenv('ALEXA_API_REQUEST_TIMEOUT', '-5')
        
        with pytest.raises(Exception):  # Pydantic ValidationError
            ConfigManager.reload()
    
    def test_invalid_retry_count_raises_error(self, monkeypatch):
        """Negative retry count should fail validation"""
        monkeypatch.setenv('ALEXA_API_MAX_RETRIES', '-1')
        
        with pytest.raises(Exception):
            ConfigManager.reload()


class TestConfigDocumentation:
    """Test auto-generated documentation"""
    
    def test_config_has_descriptions(self):
        """Each config field should have description"""
        config = get_config()
        # Pydantic auto-generates from docstrings
        schema = config.__class__.model_json_schema()
        assert 'properties' in schema
        assert len(schema['properties']) > 0
```

**Run Tests (should fail)**:
```bash
cd alexa_full_control
pytest Dev/pytests/utils/test_config_loader.py -v
# Expected: ALL FAIL (red)
```

#### 2.4.2 Implement to Make Tests Pass

**File**: `utils/config.py`

```python
"""
Centralized configuration management using Pydantic Settings.

Single source of truth for all tunable application parameters.
Supports environment variable overrides and multi-region setup.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from loguru import logger


class APISettings(BaseSettings):
    """API communication settings"""
    
    request_timeout: int = Field(
        default=10,
        description="HTTP request timeout in seconds",
        ge=1,
        le=120,
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts",
        ge=0,
        le=10,
    )
    retry_delay: float = Field(
        default=0.5,
        description="Delay between retries in seconds",
        ge=0.1,
        le=10.0,
    )
    amazon_domain: str = Field(
        default="amazon.fr",
        description="Default Amazon domain",
    )
    
    class Config:
        env_prefix = "ALEXA_API_"


class CircuitBreakerSettings(BaseSettings):
    """Circuit breaker resilience settings"""
    
    failure_threshold: int = Field(
        default=5,
        description="Failures before opening circuit",
        ge=1,
        le=50,
    )
    recovery_timeout: int = Field(
        default=60,
        description="Seconds to wait before half-open",
        ge=10,
        le=600,
    )
    
    class Config:
        env_prefix = "ALEXA_CB_"


class CacheSettings(BaseSettings):
    """Cache configuration"""
    
    enabled: bool = Field(
        default=True,
        description="Enable caching",
    )
    compression: bool = Field(
        default=True,
        description="Enable gzip compression",
    )
    default_ttl: int = Field(
        default=3600,
        description="Default TTL in seconds",
        ge=60,
        le=86400,
    )
    directory: str = Field(
        default="data/cache",
        description="Cache directory",
    )
    
    class Config:
        env_prefix = "ALEXA_CACHE_"


class LoggingSettings(BaseSettings):
    """Logging configuration"""
    
    level: str = Field(
        default="INFO",
        description="Log level (DEBUG, INFO, WARNING, ERROR)",
        regex="^(DEBUG|INFO|WARNING|ERROR)$",
    )
    format: str = Field(
        default="json",
        description="Log format (json or text)",
    )
    file: str = Field(
        default="logs/alexa.log",
        description="Log file path",
    )
    
    class Config:
        env_prefix = "ALEXA_LOG_"


class AuthSettings(BaseSettings):
    """Authentication settings"""
    
    cache_dir: str = Field(
        default="data/auth",
        description="Auth cache directory",
    )
    session_file: str = Field(
        default="session.cache",
        description="Session cache filename",
    )
    
    class Config:
        env_prefix = "ALEXA_AUTH_"


class Settings(BaseSettings):
    """Root configuration"""
    
    api: APISettings = Field(default_factory=APISettings)
    circuit_breaker: CircuitBreakerSettings = Field(
        default_factory=CircuitBreakerSettings
    )
    cache: CacheSettings = Field(default_factory=CacheSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    regions: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Multi-region endpoint mappings",
    )
    
    def get_region(self, region_code: str) -> Dict[str, str]:
        """
        Get region configuration by code.
        
        Args:
            region_code: Region identifier (us, eu, de, etc)
            
        Returns:
            Region configuration dict
            
        Raises:
            KeyError: If region not found
        """
        if region_code not in self.regions:
            raise KeyError(
                f"Region '{region_code}' not found. "
                f"Available: {list(self.regions.keys())}"
            )
        return self.regions[region_code]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class ConfigManager:
    """Singleton configuration manager"""
    
    _instance: Optional[Settings] = None
    _config_dir = Path(__file__).parent.parent / "config"
    
    @classmethod
    def load(cls) -> Settings:
        """
        Load configuration (singleton pattern).
        
        Returns:
            Settings instance
        """
        if cls._instance is not None:
            return cls._instance
        
        # Determine environment
        env = os.getenv("ALEXA_ENV", "dev")
        logger.debug(f"Loading configuration for environment: {env}")
        
        # Load base config
        base_path = cls._config_dir / "base.yaml"
        env_path = cls._config_dir / f"{env}.yaml"
        domains_path = cls._config_dir / "amazon_domains.yaml"
        
        if not base_path.exists():
            raise FileNotFoundError(f"Config not found: {base_path}")
        
        # Load YAML files manually (pydantic-settings needs help)
        import yaml
        
        with open(base_path) as f:
            base_config = yaml.safe_load(f)
        
        # Load environment-specific overrides
        if env_path.exists():
            with open(env_path) as f:
                env_config = yaml.safe_load(f) or {}
                base_config.update(env_config)
        
        # Load multi-region configuration
        if domains_path.exists():
            with open(domains_path) as f:
                domains_config = yaml.safe_load(f)
                base_config['regions'] = domains_config.get('regions', {})
        
        # Create Settings instance
        cls._instance = Settings(**base_config)
        
        logger.info(
            f"Configuration loaded for {env}",
            extra={
                "domain": cls._instance.api.amazon_domain,
                "timeout": cls._instance.api.request_timeout,
            }
        )
        
        return cls._instance
    
    @classmethod
    def reload(cls) -> Settings:
        """Reload configuration (for testing)"""
        cls._instance = None
        return cls.load()


def get_config() -> Settings:
    """Get configuration singleton"""
    return ConfigManager.load()
```

**Install Dependencies**:
```bash
pip install pydantic-settings pyyaml python-dotenv
```

**Run Tests**:
```bash
pytest Dev/pytests/utils/test_config_loader.py -v
# Expected: Tests PASS (green)
```

---

### 2.5 Integrate Config Into Services (2-3 days)

#### 2.5.1 Update AlexaAPIService

**File**: `services/alexa_api_service.py` (modifications)

```python
# Add to imports
from utils.config import get_config

class AlexaAPIService:
    """Centralized API service using configuration"""
    
    def __init__(self, auth: AlexaAuth, cache: CacheService):
        self._auth = auth
        self._cache = cache
        self._config = get_config()
        
        # Initialize circuit breaker with config
        self._circuit_breaker = CircuitBreaker(
            fail_max=self._config.circuit_breaker.failure_threshold,
            reset_timeout=self._config.circuit_breaker.recovery_timeout,
        )
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Use config for timeout"""
        try:
            url = f"https://alexa.{self._config.api.amazon_domain}/api/devices"
            response = self._circuit_breaker.call(
                self._auth.get,
                url,
                timeout=self._config.api.request_timeout,  # From config!
            )
            # ... rest of implementation
```

#### 2.5.2 Update AlexaAuth

**File**: `alexa_auth/alexa_auth.py` (modifications)

```python
class AlexaAuth:
    """Use configuration for defaults"""
    
    def __init__(
        self,
        cache_service: CacheService,
        amazon_domain: Optional[str] = None,
    ):
        config = get_config()
        
        # Use config if domain not provided
        if amazon_domain is None:
            amazon_domain = config.api.amazon_domain
        
        self.amazon_domain = amazon_domain
        # ... rest of init
```

#### 2.5.3 Update Cache Service

**File**: `services/cache_service.py` (modifications)

```python
class CacheService:
    """Use configuration for directory"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        config = get_config()
        
        if cache_dir is None:
            cache_dir = Path(config.cache.directory)
        
        self.cache_dir = cache_dir
        self.use_compression = config.cache.compression
        # ... rest of init
```

#### 2.5.4 Update main entry point

**File**: `alexa.py` (modifications)

```python
def setup_logging(verbose: bool = False, debug: bool = False):
    """Setup logging using config"""
    config = get_config()
    
    # Override with command-line flags if provided
    level = "DEBUG" if debug else ("INFO" if verbose else config.logging.level)
    
    setup_loguru_logger(
        log_file=Path(config.logging.file),
        level=level,
    )
```

**Update Tests**:
```bash
# Update existing tests to use config
pytest Dev/pytests/services/test_alexa_api_service.py -v
# Run all tests
pytest Dev/pytests/ -v
# Expected: All 88+ tests PASS
```

---

### 2.6 Configuration Audit Script (1 day)

**File**: `scripts/audit_config.py`

```python
"""Audit script to verify no hardcodes remain in code"""

import re
import subprocess
from pathlib import Path


def audit_hardcoded_values():
    """Check for remaining hardcodes"""
    
    patterns = {
        "amazon_domain": r"amazon\.(fr|com|de|eu)",
        "api_timeout": r"timeout\s*=\s*\d+",
        "retry_count": r"retry.*=\s*\d+",
        "endpoints": r"https://alexa\.",
    }
    
    excluded_dirs = {"config/", "tests/", "docs/"}
    
    results = {}
    for pattern_name, pattern in patterns.items():
        result = subprocess.run(
            ["grep", "-r", "-n", pattern, ".", "--include=*.py"],
            capture_output=True,
            text=True,
        )
        
        # Filter excluded directories
        lines = [
            l for l in result.stdout.split("\n")
            if not any(exc in l for exc in excluded_dirs)
        ]
        
        results[pattern_name] = lines
    
    # Report
    print("Configuration Audit Report")
    print("=" * 50)
    
    for pattern, lines in results.items():
        if lines:
            print(f"\n{pattern}: {len(lines)} occurrences")
            for line in lines[:5]:  # Show first 5
                print(f"  {line}")
            if len(lines) > 5:
                print(f"  ... and {len(lines) - 5} more")
        else:
            print(f"\n{pattern}: ✓ CLEAN")
    
    return all(not lines for lines in results.values())


if __name__ == "__main__":
    if audit_hardcoded_values():
        print("\n✅ No hardcoded configuration found!")
    else:
        print("\n❌ Hardcoded values still present!")
        exit(1)
```

**Run Audit**:
```bash
python scripts/audit_config.py
# Expected: ✅ No hardcoded configuration found!
```

---

### 2.7 Documentation & Examples (1 day)

**File**: `docs/CONFIGURATION.md`

```markdown
# Configuration Guide

## Overview
Configuration is centralized in YAML files and can be overridden with environment variables.

## Directory Structure
```
config/
├── base.yaml              # Default configuration
├── amazon_domains.yaml    # Multi-region mappings
├── dev.yaml              # Development overrides
├── staging.yaml          # Staging overrides
└── prod.yaml             # Production overrides
```

## Quick Start

### Development (default)
```bash
# No setup needed, uses config/dev.yaml
python -m alexa_cli --help
```

### Production
```bash
export ALEXA_ENV=prod
python -m alexa_cli --help
```

### Custom Region
```bash
export ALEXA_API_AMAZON_DOMAIN=amazon.com
python -m alexa_cli --help
```

## Configuration Reference

### API Settings
- `api.request_timeout` (default: 10s) - HTTP timeout
- `api.max_retries` (default: 3) - Retry attempts
- `api.amazon_domain` (default: amazon.fr) - Amazon region

### Cache Settings
- `cache.compression` (default: true) - Enable gzip
- `cache.default_ttl` (default: 3600) - Cache duration

### Logging
- `logging.level` (default: INFO) - Log level
- `logging.file` (default: logs/alexa.log) - Output file

## Environment Variables

All config can be overridden with env vars:
```bash
export ALEXA_API_REQUEST_TIMEOUT=20
export ALEXA_LOG_LEVEL=DEBUG
export ALEXA_CACHE_COMPRESSION=false
```

## Multi-Region Support

Supported regions: us, eu, de, uk, fr

```bash
# Use EU endpoints
export ALEXA_API_AMAZON_DOMAIN=amazon.eu

# List available regions
python -c "from utils.config import get_config; print(get_config().regions.keys())"
```
```

---

### 2.8 Code Review Checklist - Phase 2

```
CHECKLIST: Phase 2 - Configuration Externalization

Configuration Files:
- [ ] config/base.yaml exists with all defaults
- [ ] config/amazon_domains.yaml has all regions
- [ ] config/dev.yaml, staging.yaml, prod.yaml exist
- [ ] .env.example provided (no secrets!)
- [ ] All configs valid YAML format

Code Implementation:
- [ ] ConfigManager singleton implemented
- [ ] Settings Pydantic models validated
- [ ] get_config() works from anywhere
- [ ] Environment variable override works
- [ ] Multi-region lookup works

Integration:
- [ ] AlexaAPIService uses config
- [ ] AlexaAuth uses config for domain
- [ ] CacheService uses config for directory
- [ ] Logging uses config
- [ ] No hardcodes remain (audit_config.py passes)

Testing:
- [ ] All 88 existing tests pass
- [ ] 20+ new config tests pass
- [ ] Config reload works in tests
- [ ] Environment override tested
- [ ] Invalid config rejected

Documentation:
- [ ] CONFIGURATION.md complete
- [ ] Multi-region usage documented
- [ ] Environment variable list documented
- [ ] Examples provided

Git Quality:
- [ ] Commits describe changes clearly
- [ ] No sensitive data in commits
- [ ] Branch up-to-date with main
- [ ] Ready for code review

Production Readiness:
- [ ] Different configs for dev/staging/prod
- [ ] No hardcoded secrets
- [ ] All timeouts configurable
- [ ] Multi-region tested
```

---

## Definition of Done (Phase 2)

Code:
- [ ] Configuration system implemented (100% coverage)
- [ ] All services updated to use config
- [ ] All 88 existing tests passing
- [ ] 20+ new config tests added

Documentation:
- [ ] CONFIGURATION.md complete
- [ ] Multi-region examples provided
- [ ] Environment variables documented
- [ ] Design decisions recorded

Quality Metrics:
- [ ] Code coverage: >95%
- [ ] Type safety: 100% (mypy passes)
- [ ] Linting: 0 errors
- [ ] Audit: No hardcodes

Testing:
- [ ] Unit tests for ConfigManager
- [ ] Integration tests with services
- [ ] Environment override tested
- [ ] Multi-region tested

Git:
- [ ] Clear commit messages
- [ ] No merge conflicts
- [ ] Ready for production

---

## Execution Timeline

Week 1:
- [ ] Days 1-2: Requirements & analysis (2.1)
- [ ] Days 3-4: Design (2.2)
- [ ] Days 5-7: Implement config files (2.3)

Week 2:
- [ ] Days 8-9: Implement loader (2.4)
- [ ] Days 10-12: Integrate into services (2.