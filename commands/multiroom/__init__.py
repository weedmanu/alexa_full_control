"""
Gestion du multiroom Alexa.

Ce module contient la commande CLI et le manager pour le multiroom.
"""

from .command import MultiroomCommand
from .manager import MultiRoomManager

__all__ = ["MultiroomCommand", "MultiRoomManager"]



