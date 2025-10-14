param(
    [string]$action = 'help'
)

switch ($action) {
    'vulture' {
        vulture . --config .vulture.toml
    }
    'tests' {
        python -m pytest --cov=scripts --cov-report=term-missing
    }
    'bench' {
        python -m pytest --benchmark-only
    }
    'profile' {
        pyinstrument -o profile.html python -m pytest tests/pytest_install.py
        Start-Process profile.html
    }
    default {
        Write-Host "Usage: .\scripts\dev_tools.ps1 [vulture|tests|bench|profile]"
    }
}
