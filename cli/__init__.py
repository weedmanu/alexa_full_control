"""
Module CLI pour Alexa Voice Control.

Ce package contient toute l'architecture de la CLI modulaire avec sous-commandes.

Modules:
    - command_parser: Parser principal avec argparse subparsers
    - base_command: Classe de base abstraite pour toutes les commandes
    - context: Contexte partagé (auth, config, state_machine, managers)
    - commands: Package contenant toutes les commandes spécifiques

Architecture:
    python alexa_voice_control.py <CATEGORY> <ACTION> [OPTIONS]

Auteur: M@nu
Date: 7 octobre 2025
"""

from cli.base_command import BaseCommand, CommandError
from cli.command_parser import CommandParser, create_parser
from cli.context import Context, create_context

__all__ = [
    "BaseCommand",
    "CommandError",
    "CommandParser",
    "create_parser",
    "Context",
    "create_context",
]
