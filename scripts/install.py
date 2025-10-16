# Thin compatibility shim for tests expecting `scripts.install`
# Re-export the real install implementation from the `install` package.
from importlib import import_module

_real = import_module('install.install')

# Re-export top-level names from the real module
for _name in dir(_real):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_real, _name)

# Make module attributes available for `from scripts import install` style
__all__ = [n for n in globals().keys() if not n.startswith("_")]
