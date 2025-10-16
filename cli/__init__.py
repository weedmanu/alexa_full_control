"""
Module CLI pour Alexa Voice Control.

Exporte les fonctions principales pour créer le parser et le contexte.
"""

from cli.command_parser import create_parser
from cli.context import create_context

__all__ = ["create_parser", "create_context"]
