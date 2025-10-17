"""AlexaAPIService for Phase 1."""
from __future__ import annotations
import time, logging
from typing import Any, Dict, Optional, List, Type, TypeVar

from pydantic import ValidationError

# Phase 3.6: DTO imports for type-safe API responses
try:
    from core.schemas.device_schemas import GetDevicesResponse, Device
    from core.schemas.communication_schemas import (
        SpeakCommandRequest,
        AnnounceCommandRequest,
        CommunicationResponse,
    )
    from core.schemas.music_schemas import MusicStatusResponse, PlayMusicResponse
    from core.schemas.base import ResponseDTO
    HAS_SCHEMAS = True
except ImportError:
    HAS_SCHEMAS = False

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=ResponseDTO)

class AlexaAPIError(Exception):
    pass

class ApiError(AlexaAPIError):
    def __init__(self, status: int, body: Any = None, endpoint: str | None = None):
        super().__init__(f"API error {status} for {endpoint}: {body}")
        self.status = status
        self.body = body
        self.endpoint = endpoint

class NetworkError(AlexaAPIError):
    pass

class CircuitOpen(AlexaAPIError):
    pass

class AlexaAPIService:
    ENDPOINTS: Dict[str, str] = {"get_devices": "/api/devices-v2/device", "speak": "/api/speak"}
    
    def __init__(self, *args: Any, session: Any = None, cache_service: Any = None, breaker_registry: Any = None, **kwargs: Any) -> None:
        self._breaker_failures: Dict[str, int] = {}
        if args:
            auth = args[0] if len(args) > 0 else None
            cache = args[1] if len(args) > 1 else None
            self._auth = auth
            self._cache = cache
            class _AuthSessionShim:
                def __init__(self, auth_obj: Any): self._a = auth_obj
                def request(self, method: str, url: str, **kw: Any) -> Any:
                    m = method.lower()
                    if m == "get": return self._a.get(url, **kw)
                    if m == "post": return self._a.post(url, **kw)
                    if m == "put": return self._a.put(url, **kw)
                    if m == "delete": return self._a.delete(url, **kw)
                    raise ValueError(f"Unsupported: {method}")
            self._session = _AuthSessionShim(self._auth)
            return
        self._session = session or __import__("requests").Session()
        self._cache = cache_service
        self._auth = None
    
    def _resolve_path(self, key_or_path: str) -> str:
        if key_or_path.startswith("http"): return key_or_path
        if key_or_path in self.ENDPOINTS: return self.ENDPOINTS[key_or_path]
        if key_or_path.startswith("/"): return key_or_path
        return "/" + key_or_path
    
    def _check_breaker(self, endpoint: str) -> None:
        if self._breaker_failures.get(endpoint, 0) >= 2:
            raise CircuitOpen(f"Circuit open for {endpoint}")
    
    def _record_failure(self, endpoint: str) -> None:
        self._breaker_failures[endpoint] = self._breaker_failures.get(endpoint, 0) + 1
    
    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        endpoint = path
        self._check_breaker(endpoint)
        url = self._resolve_path(path)
        try:
            start = time.time()
            resp = self._session.request(method, url, **kwargs)
            duration = time.time() - start
            logger.debug("Request %s %s -> %s (%.3fs)", method, url, getattr(resp, "status_code", None), duration)
        except Exception as exc:
            logger.exception("Network error for %s %s", method, url)
            self._record_failure(endpoint)
            raise NetworkError(exc)
        status = getattr(resp, "status_code", None)
        try:
            body = resp.json() if hasattr(resp, "json") else None
        except Exception:
            body = getattr(resp, "text", None)
        if status is not None and status >= 400:
            self._record_failure(endpoint)
            raise ApiError(status, body=body, endpoint=endpoint)
        return body
    
    def get(self, path: str, cache_key: Optional[str] = None, **kwargs: Any) -> Any:
        """Perform GET request with optional cache fallback."""
        try:
            return self._request("GET", path, **kwargs)
        except NetworkError:
            if cache_key and self._cache:
                try:
                    cached = self._cache.get(cache_key, ignore_ttl=True)
                    if cached is not None:
                        logger.info("Cached: %s", cache_key)
                        return cached
                except Exception:
                    pass
            raise
    
    def post(self, path: str, json: Any = None, **kwargs: Any) -> Any:
        """Perform POST request."""
        return self._request("POST", path, json=json, **kwargs)
    
    # Phase 3.6: DTO parsing helper methods
    def _parse_dto(self, data: Dict[str, Any], dto_class: Type[T]) -> T:
        """Parse response data into a typed DTO.
        
        Args:
            data: Raw response dict from API
            dto_class: Target DTO class to parse into
            
        Returns:
            Parsed DTO instance
            
        Raises:
            ApiError: If validation fails
        """
        if not HAS_SCHEMAS:
            logger.warning("DTOs not available, returning raw data")
            return data
        
        try:
            return dto_class(**data)
        except ValidationError as e:
            logger.error("DTO validation error: %s", e)
            raise ApiError(
                status=400,
                body={'error': str(e), 'errorCode': 'VALIDATION_ERROR'},
                endpoint='parse_response'
            ) from e
    
    def get_devices(self, use_cache_fallback: bool = True) -> List[Dict[str, Any]]:
        """Get list of devices from Alexa API.
        
        Args:
            use_cache_fallback: Whether to fall back to cache on network error
            
        Returns:
            List of device dicts or GetDevicesResponse DTO if schemas available
        """
        if not hasattr(self, "_auth") or self._auth is None:
            res = self.get("devices")
            if isinstance(res, dict):
                return res.get("devices", [])
            return res
        
        cache_key = "devices_list"
        try:
            path = self.ENDPOINTS.get("get_devices", "/devices")
            domain = getattr(self._auth, "amazon_domain", "amazon.fr")
            url = f"https://alexa.{domain}{path}"
            resp = self._auth.get(url, timeout=10)
            data = resp.json()
            devices = data.get("devices", [])
            
            # Phase 3.6: Parse with DTO if available
            if HAS_SCHEMAS:
                try:
                    return self._parse_dto({"devices": devices}, GetDevicesResponse).devices
                except ApiError as e:
                    logger.warning("DTO parsing failed, returning raw devices: %s", e)
                    return devices
            
            return devices
        except Exception as exc:
            if use_cache_fallback and hasattr(self, "_cache") and self._cache:
                try:
                    cached = self._cache.get(cache_key, ignore_ttl=True)
                    if cached:
                        return cached.get("devices", [])
                except Exception:
                    pass
            from core.exceptions import APIError as CoreAPIError
            raise CoreAPIError(f"Failed: {exc}") from exc
    
    def send_speak_command(self, device_serial: str, text: str) -> CommunicationResponse:
        """Send speak command to device.
        
        Args:
            device_serial: Device serial number
            text: Text to speak
            
        Returns:
            CommunicationResponse with command status
        """
        try:
            # Create request DTO
            request = SpeakCommandRequest(
                device_serial=device_serial,
                text_to_speak=text
            )
            
            # Make API call
            if not hasattr(self, "_auth") or self._auth is None:
                path = self.ENDPOINTS.get("speak", "/speak")
                response_data = self.post(
                    path,
                    json=request.model_dump(by_alias=True),
                    timeout=10
                )
            else:
                path = self.ENDPOINTS.get("speak", "/speak")
                domain = getattr(self._auth, "amazon_domain", "amazon.fr")
                url = f"https://alexa.{domain}{path}"
                resp = self._auth.post(url, data=request.model_dump(by_alias=True), timeout=10)
                response_data = resp.json() if hasattr(resp, "json") else {"success": True}
            
            # Parse response DTO
            if not response_data:
                response_data = {"success": True}
            return self._parse_dto(response_data, CommunicationResponse)
            
        except Exception as exc:
            logger.error("speak_command failed: %s", exc)
            # Return error response DTO
            return CommunicationResponse(
                success=False,
                status="failed",
                error_message=str(exc)
            )
    
    def send_announce_command(self, device_serial: str, message: str, title: Optional[str] = None) -> CommunicationResponse:
        """Send announce command to device.
        
        Args:
            device_serial: Device serial number
            message: Message to announce
            title: Optional announcement title
            
        Returns:
            CommunicationResponse with command status
        """
        try:
            # Create request DTO
            request = AnnounceCommandRequest(
                device_serial=device_serial,
                message=message,
                title=title
            )
            
            # Make API call
            if not hasattr(self, "_auth") or self._auth is None:
                path = self.ENDPOINTS.get("announce", "/announce")
                response_data = self.post(
                    path,
                    json=request.model_dump(by_alias=True),
                    timeout=10
                )
            else:
                path = self.ENDPOINTS.get("announce", "/announce")
                domain = getattr(self._auth, "amazon_domain", "amazon.fr")
                url = f"https://alexa.{domain}{path}"
                resp = self._auth.post(url, data=request.model_dump(by_alias=True), timeout=10)
                response_data = resp.json() if hasattr(resp, "json") else {"success": True}
            
            # Parse response DTO
            if not response_data:
                response_data = {"success": True}
            return self._parse_dto(response_data, CommunicationResponse)
            
        except Exception as exc:
            logger.error("announce_command failed: %s", exc)
            # Return error response DTO
            return CommunicationResponse(
                success=False,
                status="failed",
                error_message=str(exc)
            )
    
    def get_music_status(self) -> MusicStatusResponse:
        """Get current music playback status.
        
        Returns:
            MusicStatusResponse with playback status
        """
        try:
            # Make API call for music status
            path = self.ENDPOINTS.get("music_status", "/api/np/command")
            response_data = self.get(path, cache_key="music_status")
            
            # Parse response DTO
            if not response_data:
                response_data = {"isPlaying": False, "volume": 0}
            return self._parse_dto(response_data, MusicStatusResponse)
            
        except Exception as exc:
            logger.error("get_music_status failed: %s", exc)
            # Return default status (stopped)
            return MusicStatusResponse(is_playing=False, volume=0)
    
    def play_music(self, track_id: str, device_serial: Optional[str] = None) -> PlayMusicResponse:
        """Play music track.
        
        Args:
            track_id: ID of track to play
            device_serial: Optional device serial number
            
        Returns:
            PlayMusicResponse with play status
        """
        try:
            # Make API call to play track
            path = self.ENDPOINTS.get("play_music", "/api/np/player")
            payload = {"trackId": track_id}
            if device_serial:
                payload["deviceSerialNumber"] = device_serial
            
            response_data = self.post(path, json=payload)
            
            # Parse response DTO
            if not response_data:
                response_data = {"success": True, "isPlaying": True}
            return self._parse_dto(response_data, PlayMusicResponse)
            
        except Exception as exc:
            logger.error("play_music failed: %s", exc)
            # Return error response DTO
            return PlayMusicResponse(success=False, error=str(exc))
