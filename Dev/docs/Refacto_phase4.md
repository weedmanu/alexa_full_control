# Phase 4: PROFESSIONAL REFACTORING PROMPT - Event Bus & Observability

**Project**: Alexa Voice Control CLI  
**Objective**: Phase 4 - Centralized Event System & Audit Trail  
**Methodology**: TDD + Event-Driven Architecture  
**Depends On**: Phase 1-3 COMPLETE  
**Duration**: 1-2 sprints (8-12 days)

---

## 📋 EXECUTIVE BRIEF

### Context
Current implementation lacks observability:
- No audit trail of operations
- Difficult to debug user actions
- No correlation IDs linking related operations
- Logging scattered, hard to aggregate
- No centralized event system
- No visibility into system behavior

### Goal
Implement event-driven architecture with:
- Centralized EventBus for all system events
- Correlation IDs for request tracing
- Structured logging with event metadata
- Audit trail of all operations
- Optional integration with external monitoring

### Success Criteria
- ✅ EventBus service created and integrated
- ✅ 50+ critical events defined and emitted
- ✅ Correlation IDs on all requests
- ✅ Structured logging with metadata
- ✅ All 88+ existing tests pass
- ✅ 30+ new event tests
- ✅ No performance degradation
- ✅ Production-ready error tracking

---

## 🎯 PHASE 4 DETAILED BREAKDOWN

### 4.1 Event System Design (2-3 days)

**Objective**: Define event architecture

**Design Document** (`docs/design_event_system.md`):

```markdown
# Event System Design

## Architecture

### Core Concepts

**Event**: Immutable record of something that happened
- Type: string identifier (api.call.started)
- Timestamp: when it happened
- Correlation ID: links related events
- Data: event-specific payload

**EventBus**: Central dispatcher for events
- Subscribe to event types
- Emit events
- No direct coupling between event sources/handlers

**Handlers**: Processes that react to events
- Logger handler: write to logs
- Metrics handler: collect statistics
- External handler: send to monitoring service

### Event Hierarchy

```
system.startup
system.shutdown
system.error

command.execution.started
command.execution.completed
command.execution.failed

api.call.started
api.call.completed
api.call.failed
api.rate_limited
api.circuit_breaker_opened

auth.session.created
auth.session.expired
auth.authentication_failed

cache.hit
cache.miss
cache.invalidated

scenario.execution.started
scenario.execution.completed
scenario.execution.failed
```

### Event Example

```python
Event(
    event_type="api.call.completed",
    timestamp=datetime.now(timezone.utc),
    correlation_id="550e8400-e29b-41d4-a716-446655440000",
    data={
        "endpoint": "/api/devices",
        "method": "GET",
        "status_code": 200,
        "duration_ms": 250,
        "cache_hit": False,
    }
)
```

### Benefits

1. **Tracing**: Follow complete request flow via correlation_id
2. **Debugging**: Reconstruct what happened and when
3. **Monitoring**: Collect metrics from events
4. **Audit**: Comply with regulations
5. **Analytics**: Understand usage patterns
```

**Deliverables**:
- `docs/design_event_system.md`
- Event taxonomy diagram
- Integration patterns document

---

### 4.2 Define Event Types (1-2 days)

**File**: `core/events/event_types.py`

```python
"""
Central registry of all event types in the system.

Events are immutable records of things that happened.
Every event has type, timestamp, correlation_id, and data.
"""

from enum import Enum


class EventType(str, Enum):
    """All event types in the system"""
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    
    # Command execution
    COMMAND_STARTED = "command.started"
    COMMAND_COMPLETED = "command.completed"
    COMMAND_FAILED = "command.failed"
    
    # API calls
    API_CALL_STARTED = "api.call.started"
    API_CALL_COMPLETED = "api.call.completed"
    API_CALL_FAILED = "api.call.failed"
    API_RATE_LIMITED = "api.rate_limited"
    API_CIRCUIT_BREAKER_OPENED = "api.circuit_breaker_opened"
    
    # Authentication
    AUTH_SESSION_CREATED = "auth.session.created"
    AUTH_SESSION_EXPIRED = "auth.session.expired"
    AUTH_FAILED = "auth.failed"
    
    # Cache
    CACHE_HIT = "cache.hit"
    CACHE_MISS = "cache.miss"
    CACHE_INVALIDATED = "cache.invalidated"
    
    # Business operations
    SCENARIO_STARTED = "scenario.started"
    SCENARIO_COMPLETED = "scenario.completed"
    SCENARIO_FAILED = "scenario.failed"
    
    DEVICE_DISCOVERED = "device.discovered"
    DEVICE_REMOVED = "device.removed"
    
    MUSIC_PLAYBACK_STARTED = "music.playback_started"
    MUSIC_PLAYBACK_STOPPED = "music.playback_stopped"


class EventSeverity(str, Enum):
    """Event severity levels"""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

---

### 4.3 Implement Event Model - TDD (2-3 days)

#### 4.3.1 Write Tests

**File**: `Dev/pytests/core/events/test_event_bus.py`

```python
"""Tests for event system"""

import pytest
import uuid
from datetime import datetime, timezone
from core.events.event_bus import Event, EventBus
from core.events.event_types import EventType


class TestEventCreation:
    """Test Event model"""
    
    def test_event_has_type(self):
        """Event should have type"""
        event = Event(
            event_type=EventType.API_CALL_COMPLETED,
            data={"status": 200}
        )
        assert event.event_type == EventType.API_CALL_COMPLETED
    
    def test_event_has_timestamp(self):
        """Event should have timestamp"""
        event = Event(
            event_type=EventType.API_CALL_COMPLETED,
            data={}
        )
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)
    
    def test_event_generates_correlation_id(self):
        """Event should have correlation ID"""
        event = Event(
            event_type=EventType.API_CALL_COMPLETED,
            data={}
        )
        assert event.correlation_id is not None
        assert len(event.correlation_id) > 0
    
    def test_event_accepts_correlation_id(self):
        """Event should accept provided correlation ID"""
        correlation_id = str(uuid.uuid4())
        event = Event(
            event_type=EventType.API_CALL_COMPLETED,
            data={},
            correlation_id=correlation_id,
        )
        assert event.correlation_id == correlation_id
    
    def test_event_is_immutable(self):
        """Event should be immutable"""
        event = Event(
            event_type=EventType.API_CALL_COMPLETED,
            data={}
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            event.event_type = EventType.CACHE_HIT


class TestEventBus:
    """Test EventBus functionality"""
    
    def test_event_bus_emits_events(self):
        """EventBus should emit events"""
        bus = EventBus()
        
        event = Event(
            event_type=EventType.API_CALL_COMPLETED,
            data={}
        )
        
        # Should not raise
        bus.emit(event)
    
    def test_event_bus_subscriptions(self):
        """EventBus should handle subscriptions"""
        bus = EventBus()
        events_received = []
        
        def handler(event):
            events_received.append(event)
        
        bus.subscribe(EventType.API_CALL_COMPLETED, handler)
        
        event = Event(
            event_type=EventType.API_CALL_COMPLETED,
            data={}
        )
        bus.emit(event)
        
        assert len(events_received) == 1
        assert events_received[0] == event
    
    def test_event_bus_filters_subscriptions(self):
        """EventBus should only send matching events"""
        bus = EventBus()
        events_received = []
        
        def handler(event):
            events_received.append(event)
        
        bus.subscribe(EventType.API_CALL_COMPLETED, handler)
        
        # Emit different event
        event = Event(
            event_type=EventType.CACHE_HIT,
            data={}
        )
        bus.emit(event)
        
        assert len(events_received) == 0


class TestCorrelationID:
    """Test correlation ID tracking"""
    
    def test_correlation_id_propagates(self):
        """Correlation ID should propagate through related events"""
        correlation_id = str(uuid.uuid4())
        
        event1 = Event(
            event_type=EventType.API_CALL_STARTED,
            data={},
            correlation_id=correlation_id,
        )
        
        event2 = Event(
            event_type=EventType.API_CALL_COMPLETED,
            data={},
            correlation_id=correlation_id,
        )
        
        assert event1.correlation_id == event2.correlation_id
```

#### 4.3.2 Implement Event System

**File**: `core/events/event_bus.py`

```python
"""
Centralized event bus for system-wide event handling.

Enables decoupled communication between components through
typed events with correlation IDs for request tracing.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from threading import RLock

from loguru import logger

from core.events.event_types import EventType, EventSeverity


@dataclass(frozen=True)
class Event:
    """Immutable event record"""
    
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    correlation_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    severity: EventSeverity = field(default=EventSeverity.INFO)
    source: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for logging"""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "severity": self.severity.value,
            "data": self.data,
            "source": self.source,
        }


class EventBus:
    """
    Centralized event dispatcher.
    
    Thread-safe singleton that manages event subscriptions
    and emissions across the application.
    """
    
    _instance: Optional["EventBus"] = None
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._lock = RLock()
        self._event_history: List[Event] = []
        self._max_history = 1000
    
    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[Event], None],
    ) -> None:
        """
        Subscribe to events of specific type.
        
        Args:
            event_type: Type of events to listen for
            handler: Callable that processes events
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)
            logger.debug(f"Subscribed to {event_type.value}")
    
    def emit(self, event: Event) -> None:
        """
        Emit event to all subscribers.
        
        Args:
            event: Event to emit
        """
        with self._lock:
            # Store in history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            # Log event
            logger.bind(
                correlation_id=event.correlation_id,
                event_type=event.event_type.value,
            ).log(
                event.severity.value.upper(),
                f"Event: {event.event_type.value}",
                extra=event.data,
            )
            
            # Dispatch to handlers
            if event.event_type in self._subscribers:
                for handler in self._subscribers[event.event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        logger.error(
                            f"Error in event handler: {e}",
                            extra={"event_type": event.event_type.value},
                        )
    
    def get_history(
        self,
        correlation_id: Optional[str] = None,
    ) -> List[Event]:
        """
        Retrieve event history.
        
        Args:
            correlation_id: Filter by correlation ID
            
        Returns:
            List of events
        """
        with self._lock:
            if correlation_id:
                return [
                    e for e in self._event_history
                    if e.correlation_id == correlation_id
                ]
            return list(self._event_history)
    
    @classmethod
    def get_instance(cls) -> "EventBus":
        """Get EventBus singleton"""
        if cls._instance is None:
            cls._instance = EventBus()
        return cls._instance
```

**Run Tests**:
```bash
pytest Dev/pytests/core/events/test_event_bus.py -v
# Expected: Tests PASS
```

---

### 4.4 Integrate Events Into AlexaAPIService (2-3 days)

**File**: `services/alexa_api_service.py` (modifications)

```python
from core.events.event_bus import Event, EventBus
from core.events.event_types import EventType, EventSeverity

class AlexaAPIService:
    """API service with event emission"""
    
    def __init__(self, auth, cache):
        self._auth = auth
        self._cache = cache
        self._event_bus = EventBus.get_instance()
    
    def get_devices(self) -> GetDevicesResponse:
        """Get devices with event tracking"""
        correlation_id = str(uuid.uuid4())
        
        # Emit: API call started
        self._event_bus.emit(Event(
            event_type=EventType.API_CALL_STARTED,
            data={
                "endpoint": "/api/devices",
                "method": "GET",
            },
            correlation_id=correlation_id,
        ))
        
        try:
            start_time = time.time()
            url = f"https://alexa.{self._config.api.amazon_domain}/api/devices"
            
            response = self._circuit_breaker.call(
                self._auth.get,
                url,
                timeout=self._config.api.request_timeout,
            )
            
            duration_ms = (time.time() - start_time) * 1000
            data = response.json()
            devices_response = GetDevicesResponse(**data)
            
            # Emit: API call completed
            self._event_bus.emit(Event(
                event_type=EventType.API_CALL_COMPLETED,
                data={
                    "endpoint": "/api/devices",
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "device_count": len(devices_response.devices),
                },
                correlation_id=correlation_id,
                severity=EventSeverity.INFO,
            ))
            
            return devices_response
            
        except Exception as e:
            # Emit: API call failed
            self._event_bus.emit(Event(
                event_type=EventType.API_CALL_FAILED,
                data={
                    "endpoint": "/api/devices",
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                correlation_id=correlation_id,
                severity=EventSeverity.ERROR,
            ))
            raise
```

---

### 4.5 Add Event Handlers (1-2 days)

**File**: `services/event_handlers.py`

```python
"""Built-in event handlers"""

from loguru import logger
from core.events.event_bus import Event, EventBus
from core.events.event_types import EventType


class LoggingEventHandler:
    """Handler that logs all events"""
    
    @staticmethod
    def setup():
        """Register logging handlers"""
        bus = EventBus.get_instance()
        
        # Log all API failures
        bus.subscribe(EventType.API_CALL_FAILED, LoggingEventHandler.log_api_failure)
        
        # Log auth failures
        bus.subscribe(EventType.AUTH_FAILED, LoggingEventHandler.log_auth_failure)
    
    @staticmethod
    def log_api_failure(event: Event):
        """Log API failures with context"""
        logger.error(
            "API call failed",
            extra={
                "correlation_id": event.correlation_id,
                "endpoint": event.data.get("endpoint"),
                "error": event.data.get("error"),
            }
        )
    
    @staticmethod
    def log_auth_failure(event: Event):
        """Log authentication failures"""
        logger.error(
            "Authentication failed",
            extra={
                "correlation_id": event.correlation_id,
                "reason": event.data.get("reason"),
            }
        )


class MetricsEventHandler:
    """Handler that collects metrics"""
    
    stats = {
        "api_calls_total": 0,
        "api_calls_failed": 0,
        "cache_hits": 0,
        "cache_misses": 0,
    }
    
    @staticmethod
    def setup():
        """Register metrics handlers"""
        bus = EventBus.get_instance()
        
        bus.subscribe(EventType.API_CALL_COMPLETED, MetricsEventHandler.count_api_call)
        bus.subscribe(EventType.API_CALL_FAILED, MetricsEventHandler.count_api_failure)
        bus.subscribe(EventType.CACHE_HIT, MetricsEventHandler.count_cache_hit)
        bus.subscribe(EventType.CACHE_MISS, MetricsEventHandler.count_cache_miss)
    
    @staticmethod
    def count_api_call(event: Event):
        MetricsEventHandler.stats["api_calls_total"] += 1
    
    @staticmethod
    def count_api_failure(event: Event):
        MetricsEventHandler.stats["api_calls_failed"] += 1
    
    @staticmethod
    def count_cache_hit(event: Event):
        MetricsEventHandler.stats["cache_hits"] += 1
    
    @staticmethod
    def count_cache_miss(event: Event):
        MetricsEventHandler.stats["cache_misses"] += 1
    
    @staticmethod
    def get_stats():
        return MetricsEventHandler.stats
```

---

### 4.6 Update Main Entry Point (1 day)

**File**: `alexa.py` (modifications)

```python
def main() -> int:
    """Main entry point"""
    try:
        # Initialize event bus and handlers
        from services.event_handlers import LoggingEventHandler, MetricsEventHandler
        
        LoggingEventHandler.setup()
        MetricsEventHandler.setup()
        
        # Emit: System startup
        event_bus = EventBus.get_instance()
        event_bus.emit(Event(
            event_type=EventType.SYSTEM_STARTUP,
            data={"version": "2.0.0"},
        ))
        
        # ... rest of main
        
        # On shutdown
        event_bus.emit(Event(
            event_type=EventType.SYSTEM_SHUTDOWN,
            data={},
        ))
        
    except Exception as e:
        event_bus.emit(Event(
            event_type=EventType.SYSTEM_ERROR,
            data={"error": str(e)},
            severity=EventSeverity.CRITICAL,
        ))
        raise
```

---

### 4.7 Documentation & Examples (1 day)

**File**: `docs/EVENT_SYSTEM.md`

```markdown
# Event System

## Overview

All significant operations in the system emit typed events. Events enable:
- Request tracing via correlation IDs
- Audit trail of operations
- Performance monitoring
- Integration with external systems

## Event Flow Example

```
User runs: alexa music play -d "Salon" -s "Soleil Bleu"

1. COMMAND_STARTED event
   - correlation_id: abc-123
   - data: {command: "music", action: "play"}

2. API_CALL_STARTED event
   - correlation_id: abc-123
   - data: {endpoint: "/api/devices"}

3. API_CALL_COMPLETED event
   - correlation_id: abc-123
   - data: {status: 200, duration_ms: 150}

4. API_CALL_STARTED event
   - correlation_id: abc-123
   - data: {endpoint: "/api/music"}

5. API_CALL_COMPLETED event
   - correlation_id: abc-123
   - data: {status: 200, duration_ms: 200}

6. COMMAND_COMPLETED event
   - correlation_id: abc-123
   - data: {result: "success"}
```

## Using Events in Code

```python
from core.events.event_bus import Event, EventBus
from core.events.event_types import EventType, EventSeverity

bus = EventBus.get_instance()

# Emit event
bus.emit(Event(
    event_type=EventType.API_CALL_COMPLETED,
    data={
        "endpoint": "/api/music",
        "status": 200,
    },
    severity=EventSeverity.INFO,
))

# Subscribe to events
def handle_api_failure(event):
    print(f"API failed: {event.data['error']}")

bus.subscribe(EventType.API_CALL_FAILED, handle_api_failure)
```

## Tracing Requests

All related events share same correlation_id:

```bash
# View all events for specific correlation_id
python -c "
from core.events.event_bus import EventBus
bus = EventBus.get_instance()
events = bus.get_history('abc-123')
for e in events:
    print(f'{e.event_type}: {e.data}')
"
```
```

---

### 4.8 Code Review Checklist - Phase 4

```
CHECKLIST: Phase 4 - Event Bus & Observability

Event System:
- [ ] EventType enum complete (50+ events)
- [ ] Event model immutable
- [ ] EventBus singleton pattern
- [ ] Thread-safe event emission
- [ ] Event history maintained

Integration:
- [ ] AlexaAPIService emits events
- [ ] All major operations emit events
- [ ] Correlation IDs propagated
- [ ] Handlers registered on startup
- [ ] No performance impact

Handlers:
- [ ] LoggingEventHandler working
- [ ] MetricsEventHandler collecting
- [ ] Error handling in handlers
- [ ] No lost events

Testing:
- [ ] EventBus tested (30+ tests)
- [ ] All 88+ existing tests pass
- [ ] Event emission verified
- [ ] Correlation ID tested
- [ ] Handler subscription tested

Documentation:
- [ ] EVENT_SYSTEM.md complete
- [ ] Examples provided
- [ ] Integration guide provided
- [ ] Troubleshooting guide

Quality:
- [ ] Type hints: 100%
- [ ] Coverage: >95%
- [ ] No performance regression
- [ ] Thread-safety verified
```

---

## Definition of Done (Phase 4)

Code:
- [ ] EventBus implemented and tested
- [ ] 50+ event types defined
- [ ] All services emit events
- [ ] Correlation IDs on all requests
- [ ] All 88+ existing tests passing
- [ ] 30+ new event tests

Documentation:
- [ ] EVENT_SYSTEM.md complete
- [ ] Integration examples provided
- [ ] Troubleshooting guide

Quality:
- [ ] Type safety: 100%
- [ ] Test coverage: >95%
- [ ] No performance impact
- [ ] Thread-safe implementation

---

## Timeline

Week 1:
- [ ] Days 1-2: Design (4.1-4.2)
- [ ] Days 3-4: Implement event system (4.3)
- [ ] Days 5-7: Integrate (4.4-4.5)

Week 2:
- [ ] Days 8-9: Add handlers (4.5)
- [ ] Days 10-11: Documentation (4.7)
- [ ] Day 12: Code review (4.8)