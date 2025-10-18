"""
Package des commandes CLI spécifiques.

Ce package contient toutes les implémentations de commandes pour chaque catégorie.

Catégories disponibles:
    - auth: Authentification
    - device: Gestion appareils
    - music: Contrôle musique
    - (timers) : supprimé - actions timers disponibles via `device` (fusion)
    - alarm: Gestion alarmes
    - reminder: Gestion rappels
    - light: Contrôle lumières
    - thermostat: Contrôle thermostats
    - smarthome: Contrôle appareils smart home
    - announcement: Gestion annonces
    - dnd: Mode Ne Pas Déranger
    - activity: Historique activités
    - calendar: Gestion calendrier
    - audio: Paramètres audio
    - settings: Paramètres appareils
    - routine: Routines
    - multiroom: Groupes multi-pièces

Auteur: M@nu
Date: 7 octobre 2025
"""

try:
    from cli.activity import ActivityCommand
except Exception:
    from cli.commands.activity import ActivityCommand

try:
    from cli.alarm import AlarmCommand
except Exception:
    from cli.commands.alarm import AlarmCommand

try:
    from cli.auth import AuthCommand
except Exception:
    from cli.commands.auth import AuthCommand

try:
    from cli.cache import CacheCommand
except Exception:
    from cli.commands.cache import CacheCommand

try:
    from cli.calendar import CalendarCommand
except Exception:
    from cli.commands.calendar import CalendarCommand

try:
    from cli.device import DeviceCommand
except Exception:
    from cli.commands.device import DeviceCommand

try:
    from cli.device_communicate import DeviceCommunicateCommand
except Exception:
    from cli.commands.device_communicate import DeviceCommunicateCommand

try:
    from cli.device_manager import DeviceManagerCommand
except Exception:
    from cli.commands.device_manager import DeviceManagerCommand

try:
    from cli.dnd import DNDCommand
except Exception:
    from cli.commands.dnd import DNDCommand

try:
    from cli.favorite import FavoriteCommand
except Exception:
    from cli.commands.favorite import FavoriteCommand

try:
    from cli.lists import ListsCommand
except Exception:
    from cli.commands.lists import ListsCommand

try:
    from cli.multiroom import MultiroomCommand
except Exception:
    from cli.commands.multiroom import MultiroomCommand

try:
    from cli.music_playback_manager import MusicPlaybackManagerCommand
except Exception:
    from cli.commands.music_playback_manager import MusicPlaybackManagerCommand

try:
    from cli.music_library import LibraryCommands
except Exception:
    from cli.commands.music_library import LibraryCommands

try:
    from cli.music_playback import PlaybackCommands
except Exception:
    from cli.commands.music_playback import PlaybackCommands

try:
    from cli.music_tunein import TuneInCommands
except Exception:
    from cli.commands.music_tunein import TuneInCommands

# Aliases publics pour compatibilité avec l'enregistrement des commandes
MusicLibraryCommand = LibraryCommands
MusicPlaybackCommand = PlaybackCommands
MusicRadioCommand = TuneInCommands
from cli.reminder import ReminderCommand
from cli.routine import RoutineCommand
from cli.scenario import ScenarioCommand
from cli.smarthome import SmartHomeCommand
from cli.timers_manager import TimersManagerCommand
from cli.alarm import AlarmCommand
from cli.reminder import ReminderCommand
from cli.timers_countdown import TimersCommands as CountdownCommand

__all__ = [
    "ActivityCommand",
    "AlarmCommand",
    "ReminderCommand",
    "CountdownCommand",
    "CalendarCommand",
    "DeviceCommand",
    "DeviceManagerCommand",
    "DeviceCommunicateCommand",
    "DNDCommand",
    "FavoriteCommand",
    "ListsCommand",
    "MultiroomCommand",
    "MusicLibraryCommand",
    "MusicPlaybackCommand",
    "MusicRadioCommand",
    "MusicPlaybackManagerCommand",
    "ReminderCommand",
    "RoutineCommand",
    "ScenarioCommand",
    "SmartHomeCommand",
    "AlarmCommand",
    "ReminderCommand",
    "CountdownCommand",
    "TimersManagerCommand",
]
