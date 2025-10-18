"""
Package des commandes Alexa.

Ce package organise toutes les fonctionnalités Alexa par domaine :
- Chaque domaine a son propre sous-package avec sa commande CLI et son manager
- Les classes de base sont dans le sous-package 'base'
- L'organisation permet une maintenance et une évolution plus faciles

Domaines disponibles :
- alarms : Gestion des alarmes
- reminders : Gestion des rappels
- timers : Gestion des minuteurs
- music : Contrôle musical (library, playback, radio)
- activity : Historique d'activité
- calendar : Gestion du calendrier
- dnd : Mode Ne Pas Déranger
- lists : Gestion des listes
- multiroom : Groupes multi-pièces
- routines : Routines automatisées
- scenario : Scénarios personnalisés
- smart_home : Contrôle appareils connectés
"""

# Imports des commandes pour compatibilité avec l'ancien système
from .alarms import AlarmCommand
from .reminders import ReminderCommand
from .timers import CountdownCommand
from .music import LibraryCommand, PlaybackCommand, RadioCommand
from .activity import ActivityCommand
from .calendar import CalendarCommand
from .dnd import DNDCommand
from .lists import ListsCommand
from .multiroom import MultiroomCommand
from .routines import RoutineCommand
from .scenario import ScenarioCommand
from .smart_home import SmartHomeCommand
from .auth import AuthCommand
from .device import DeviceCommand
from .cache import CacheCommand
from .favorite import FavoriteCommand
from .announcement import AnnouncementCommand

# Imports des managers pour compatibilité
from .alarms import AlarmManager
from .reminders import ReminderManager
from .timers import TimerManager
from .music import LibraryManager, PlaybackManager, TuneInManager
from .activity import ActivityManager
from .calendar import CalendarManager
from .dnd import DNDManager
from .lists import ListsManager
from .multiroom import MultiRoomManager
from .routines import RoutineManager
from .scenario import ScenarioManager
from .smart_home import LightController, ThermostatController, SmartDeviceController

__all__ = [
    # Commandes
    "AlarmCommand",
    "ReminderCommand",
    "CountdownCommand",
    "LibraryCommand",
    "PlaybackCommand",
    "RadioCommand",
    "ActivityCommand",
    "CalendarCommand",
    "DNDCommand",
    "ListsCommand",
    "MultiroomCommand",
    "RoutineCommand",
    "ScenarioCommand",
    "SmartHomeCommand",
    "AuthCommand",
    "DeviceCommand",
    "CacheCommand",
    "FavoriteCommand",
    "AnnouncementCommand",

    # Managers
    "AlarmManager",
    "ReminderManager",
    "TimerManager",
    "LibraryManager",
    "PlaybackManager",
    "TuneInManager",
    "ActivityManager",
    "CalendarManager",
    "DNDManager",
    "ListsManager",
    "MultiRoomManager",
    "RoutineManager",
    "ScenarioManager",
    "LightController",
    "ThermostatController",
    "SmartDeviceController",
]



