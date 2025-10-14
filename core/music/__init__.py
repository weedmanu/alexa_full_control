"""
Package de gestion avancée de la musique.

Note: LibraryManager utilise VoiceCommandService au lieu d'une bibliothèque locale.
"""

from .library_manager import LibraryManager
from .playback_manager import PlaybackManager
from .tunein_manager import TuneInManager

__all__ = ["LibraryManager", "PlaybackManager", "TuneInManager"]
