"""
Infrastructure partagée des commandes.

Ce module contient les composants d'infrastructure utilisés par toutes les commandes :
- Context : Contexte partagé injecté dans toutes les commandes
- create_context : Factory function pour créer un contexte
"""

from .context import Context, create_context

__all__ = ["Context", "create_context"]