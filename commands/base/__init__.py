"""
Classes de base pour les commandes et managers.

Ce module contient les classes abstraites de base pour toutes les commandes CLI
et tous les managers du syst�me.
"""

from .command import BaseCommand
from .manager import BaseManager
from .persistence_manager import BasePersistenceManager

__all__ = ["BaseCommand", "BaseManager", "BasePersistenceManager"]



