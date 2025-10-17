from core.dnd_manager import DNDManager
from core.music.playback_manager import PlaybackManager
from core.notification_manager import NotificationManager
from core.reminders.reminder_manager import ReminderManager


class FakeAPI:
    pass


class DummyAuth:
    # Minimal object returned/used as http_client by BaseManager
    def __init__(self):
        self.session = None


class DummyConfig:
    def __init__(self):
        self.amazon_domain = "amazon.test"
        self.alexa_domain = "alexa.test"


def test_dnd_manager_accepts_api_service():
    api = FakeAPI()
    dm = DNDManager(auth=DummyAuth(), config=DummyConfig(), api_service=api)
    assert dm._api_service is api


def test_notification_manager_accepts_api_service():
    api = FakeAPI()
    nm = NotificationManager(auth=DummyAuth(), config=DummyConfig(), api_service=api)
    assert nm._api_service is api


def test_reminder_and_playback_accept_api_service():
    api = FakeAPI()
    rm = ReminderManager(auth=DummyAuth(), config=DummyConfig(), api_service=api)
    pm = PlaybackManager(auth=DummyAuth(), config=DummyConfig(), api_service=api)
    assert rm._api_service is api
    assert pm._api_service is api
