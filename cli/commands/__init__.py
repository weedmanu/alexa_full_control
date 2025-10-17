"""
Package des commandes CLI spécifiques.

Ce package contient toutes les implémentations de commandes pour chaque catégorie.

Catégories disponibles:
    - auth: Authentification
    - device: Gestion appareils
    - music: Contrôle musique
    - timer: Gestion timers
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

from cli.commands.activity import ActivityCommand
from cli.commands.alarm import AlarmCommand
from cli.commands.auth import AuthCommand
from cli.commands.cache import CacheCommand
from cli.commands.calendar import CalendarCommand
from cli.commands.device import DeviceCommand
from cli.commands.device_manager import DeviceManagerCommand
from cli.commands.device_communicate import DeviceCommunicateCommand
from cli.commands.dnd import DNDCommand
from cli.commands.favorite import FavoriteCommand
from cli.commands.lists import ListsCommand
from cli.commands.multiroom import MultiroomCommand
from cli.commands.music import MusicCommand
from cli.commands.music_playback_manager import MusicPlaybackManagerCommand
from cli.commands.reminder import ReminderCommand
from cli.commands.routine import RoutineCommand
from cli.commands.scenario import ScenarioCommand
from cli.commands.smarthome import SmartHomeCommand
from cli.commands.timers import TimerCommand
from cli.commands.timers_manager import TimersManagerCommand

__all__ = [
    "ActivityCommand",
    "AlarmCommand",
    "AuthCommand",
    "CacheCommand",
    "CalendarCommand",
    "DeviceCommand",
    "DeviceManagerCommand",
    "DeviceCommunicateCommand",
    "DNDCommand",
    "FavoriteCommand",
    "ListsCommand",
    "MultiroomCommand",
    "MusicCommand",
    "MusicPlaybackManagerCommand",
    "ReminderCommand",
    "RoutineCommand",
    "ScenarioCommand",
    "SmartHomeCommand",
    "TimerCommand",
    "TimersManagerCommand",
]
