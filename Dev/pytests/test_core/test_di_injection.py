from core.di_container import reset_di_container, setup_di_container


class DummyAuth:
    def __init__(self):
        self.session = None
        self.amazon_domain = "amazon.test"


class DummyConfig:
    def __init__(self):
        self.alexa_domain = "alexa.test"
        self.amazon_domain = "amazon.test"


def test_di_injects_alexa_api_service():
    reset_di_container()
    auth = DummyAuth()
    config = DummyConfig()
    container = setup_di_container(auth, config)

    # Create a playback manager via the container - should receive alexa_api_service if available
    playback = container.get_manager("playback_manager")
    # If AlexaAPIService is registered, the manager should have attribute _api_service
    assert hasattr(playback, "_api_service")
