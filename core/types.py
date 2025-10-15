from typing import Any, Optional, Protocol

import requests


class HTTPClientProtocol(Protocol):
    """Protocol décrivant l'interface attendue d'un client HTTP utilisé par les managers.

    Doit fournir les méthodes HTTP usuelles et un attribut optionnel `csrf`.
    """

    csrf: Optional[str]

    def get(self, url: str, **kwargs: Any) -> requests.Response: ...

    def post(self, url: str, **kwargs: Any) -> requests.Response: ...

    def put(self, url: str, **kwargs: Any) -> requests.Response: ...

    def delete(self, url: str, **kwargs: Any) -> requests.Response: ...
