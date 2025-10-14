"""
State Machine pour la gestion robuste des états de connexion Alexa.

Cette machine à états garantit des transitions sûres et prévisibles
entre les différents états de connexion et d'authentification.
"""

import threading
from enum import Enum, auto
from typing import Callable, Dict, List

# Utiliser logger standard si loguru n'est pas disponible
try:
    from utils.logger import get_logger
    logger = get_logger("state_machine")
except ImportError:
    try:
        from loguru import logger
    except ImportError:
        import logging

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)  # type: ignore


class ConnectionState(Enum):
    """États possibles de la connexion Alexa."""

    DISCONNECTED = auto()  # Pas de connexion
    AUTHENTICATING = auto()  # En cours d'authentification
    AUTHENTICATED = auto()  # Authentifié, prêt à communiquer
    REFRESHING_TOKEN = auto()  # En cours de rafraîchissement du token
    ERROR = auto()  # État d'erreur
    RATE_LIMITED = auto()  # Rate limit atteint
    CIRCUIT_OPEN = auto()  # Circuit breaker ouvert


class StateTransitionError(Exception):
    """Erreur levée lors d'une transition d'état invalide."""


class AlexaStateMachine:
    """
    Machine à états thread-safe pour gérer la connexion Alexa.

    Garantit que les transitions d'état sont valides et atomiques,
    évitant les race conditions et les états incohérents.
    """

    # Transitions valides : état actuel -> états possibles
    VALID_TRANSITIONS: Dict[ConnectionState, List[ConnectionState]] = {
        ConnectionState.DISCONNECTED: [
            ConnectionState.AUTHENTICATING,
            ConnectionState.ERROR,
        ],
        ConnectionState.AUTHENTICATING: [
            ConnectionState.AUTHENTICATED,
            ConnectionState.ERROR,
            ConnectionState.REFRESHING_TOKEN,
            ConnectionState.RATE_LIMITED,
        ],
        ConnectionState.AUTHENTICATED: [
            ConnectionState.DISCONNECTED,
            ConnectionState.ERROR,
            ConnectionState.REFRESHING_TOKEN,
            ConnectionState.RATE_LIMITED,
            ConnectionState.CIRCUIT_OPEN,
        ],
        ConnectionState.REFRESHING_TOKEN: [
            ConnectionState.AUTHENTICATED,
            ConnectionState.ERROR,
            ConnectionState.RATE_LIMITED,
        ],
        ConnectionState.ERROR: [
            ConnectionState.DISCONNECTED,
            ConnectionState.AUTHENTICATING,
            ConnectionState.REFRESHING_TOKEN,
        ],
        ConnectionState.RATE_LIMITED: [
            ConnectionState.AUTHENTICATED,
            ConnectionState.ERROR,
            ConnectionState.DISCONNECTED,
        ],
        ConnectionState.CIRCUIT_OPEN: [
            ConnectionState.DISCONNECTED,
            ConnectionState.AUTHENTICATING,
            ConnectionState.ERROR,
        ],
    }

    def __init__(self, initial_state: ConnectionState = ConnectionState.DISCONNECTED):
        """
        Initialise la machine à états.

        Args:
            initial_state: État initial (par défaut DISCONNECTED)
        """
        self._state = initial_state
        self._lock = threading.RLock()  # Lock réentrant pour éviter les deadlocks
        self._state_history: List[ConnectionState] = [initial_state]
        self._callbacks: Dict[ConnectionState, List[Callable[[], None]]] = {}

        logger.info("Initialisation de la State Machine")
        logger.success(f"State Machine initialisée: {initial_state.name}")

    @property
    def state(self) -> ConnectionState:
        """Retourne l'état actuel (thread-safe)."""
        with self._lock:
            return self._state

    @property
    def is_connected(self) -> bool:
        """Vérifie si la connexion est établie."""
        return self.state == ConnectionState.AUTHENTICATED

    @property
    def can_execute_commands(self) -> bool:
        """Vérifie si on peut exécuter des commandes."""
        return self.state == ConnectionState.AUTHENTICATED

    @property
    def is_error_state(self) -> bool:
        """Vérifie si on est dans un état d'erreur."""
        return self.state in [
            ConnectionState.ERROR,
            ConnectionState.RATE_LIMITED,
            ConnectionState.CIRCUIT_OPEN,
        ]

    def transition_to(self, new_state: ConnectionState) -> bool:
        """
        Effectue une transition vers un nouvel état (thread-safe).

        Args:
            new_state: Nouvel état cible

        Returns:
            True si la transition a réussi, False sinon

        Raises:
            StateTransitionError: Si la transition n'est pas valide
        """
        with self._lock:
            current = self._state

            # Vérifier si la transition est valide
            if new_state not in self.VALID_TRANSITIONS.get(current, []):
                error_msg = f"Transition invalide: {current.name} → {new_state.name}"
                logger.error(f"❌ {error_msg}")
                raise StateTransitionError(error_msg)

            # Effectuer la transition
            logger.info(f"🔄 Transition: {current.name} → {new_state.name}")
            self._state = new_state
            self._state_history.append(new_state)

            # Limiter l'historique à 100 états
            if len(self._state_history) > 100:
                self._state_history = self._state_history[-100:]

            # Exécuter les callbacks
            self._execute_callbacks(new_state)

            return True

    def register_callback(self, state: ConnectionState, callback: Callable[[], None]) -> None:
        """
        Enregistre un callback à exécuter lors de l'entrée dans un état.

        Args:
            state: État qui déclenchera le callback
            callback: Fonction à appeler (sans arguments)
        """
        with self._lock:
            if state not in self._callbacks:
                self._callbacks[state] = []
            self._callbacks[state].append(callback)
            logger.debug(f"📌 Callback enregistré pour l'état {state.name}")

    def _execute_callbacks(self, state: ConnectionState) -> None:
        """Exécute tous les callbacks pour un état donné."""
        callbacks = self._callbacks.get(state, [])
        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"❌ Erreur dans callback pour {state.name}: {e}")

    def get_history(self, limit: int = 10) -> List[ConnectionState]:
        """
        Retourne l'historique des états.

        Args:
            limit: Nombre maximum d'états à retourner

        Returns:
            Liste des derniers états (du plus ancien au plus récent)
        """
        with self._lock:
            return self._state_history[-limit:]

    def reset(self) -> None:
        """Réinitialise la machine à l'état DISCONNECTED."""
        with self._lock:
            logger.warning("🔄 Réinitialisation de la State Machine")
            self._state = ConnectionState.DISCONNECTED
            self._state_history.append(ConnectionState.DISCONNECTED)

    def set_initial_state(self, new_state: ConnectionState) -> None:
        """
        Définit l'état initial sans validation des transitions.

        ⚠️ À utiliser uniquement lors de l'initialisation avec des credentials existants.
        Bypasse les transitions normales pour restaurer un état connu.

        Args:
            new_state: État initial à définir (typiquement AUTHENTICATED si cookies valides)
        """
        with self._lock:
            logger.debug(f"🔧 Initialisation état: {self._state.name} → {new_state.name}")
            self._state = new_state
            self._state_history.append(new_state)
            self._execute_callbacks(new_state)

    def connect(self) -> None:
        """Démarre le processus de connexion (transition vers AUTHENTICATING)."""
        self.transition_to(ConnectionState.AUTHENTICATING)

    def disconnect(self) -> None:
        """Se déconnecte (transition vers DISCONNECTED)."""
        self.transition_to(ConnectionState.DISCONNECTED)

    def on_connected(self) -> None:
        """Confirme la connexion réussie (transition vers AUTHENTICATED)."""
        self.transition_to(ConnectionState.AUTHENTICATED)

    def error(self) -> None:
        """Signale une erreur (transition vers ERROR)."""
        self.transition_to(ConnectionState.ERROR)

    def refresh_token(self) -> None:
        """Démarre le rafraîchissement du token (transition vers REFRESHING_TOKEN)."""
        self.transition_to(ConnectionState.REFRESHING_TOKEN)
