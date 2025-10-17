"""
Music-Related Data Transfer Objects (DTOs)

Phase 3.5 - Music Schemas Implementation

Models:
- TrackDTO: Individual track metadata (title, artist, duration, art)
- PlaylistDTO: Playlist information and metadata
- PlayMusicRequest: Request to play a track or queue
- PlayMusicResponse: Response from play command
- MusicStatusResponse: Current playback status
- MusicSearchResponse: Search results for music
- MusicLibraryResponse: User's music library info
- QueueResponse: Current playback queue

API Endpoints:
- GET /api/np/command/queue: Get current queue
- GET /api/np/command: Get current playback status
- POST /api/np/command: Send playback commands (play, pause, next, etc)
- GET /api/music/library: Get user's music library
- GET /api/music/search: Search music library
- POST /api/np/player: Play specific track

Field Mapping (camelCase → snake_case):
- trackId → track_id
- playlistId → playlist_id
- artUrl → art_url
- currentTrack → current_track
- isPlaying → is_playing
- repeatMode → repeat_mode
- shuffleMode → shuffle_mode
- queueLength → queue_length
- queueIndex → queue_index
- queueToken → queue_token
- deviceSerialNumber → device_serial_number
- trackCount → track_count
- totalCount → total_count
- currentIndex → current_index

Example Amazon API Responses:
GET /api/np/command (music status):
{
    "currentTrack": {
        "trackId": "TRACK123",
        "title": "Song Title",
        "artist": "Artist Name"
    },
    "isPlaying": true,
    "progress": 45,
    "duration": 180,
    "volume": 50
}

POST /api/np/player (play track):
{
    "trackId": "TRACK123",
    "deviceSerialNumber": "ABC123",
    "shuffleMode": "off",
    "repeatMode": "none"
}
"""

from typing import List, Optional

from pydantic import Field, field_validator

from core.schemas.base import DomainModel, RequestDTO, ResponseDTO


class TrackDTO(DomainModel):
    """
    Individual track metadata.

    Represents a single music track with its metadata:
    artist, title, duration, album, etc.

    Attributes:
        track_id: Unique track identifier (Spotify URI format or Amazon ID)
        title: Track/song title
        artist: Primary artist name
        album: Album name (optional)
        duration: Track duration in seconds (optional)
        art_url: Album art URL (optional)

    Example:
        >>> track = TrackDTO(
        ...     trackId="spotify:track:123",
        ...     title="Bohemian Rhapsody",
        ...     artist="Queen",
        ...     duration=354
        ... )
        >>> track.title
        'Bohemian Rhapsody'
    """

    # Required fields
    track_id: Optional[str] = Field(None, alias="trackId")
    title: str
    artist: str

    # Optional fields
    album: Optional[str] = None
    duration: Optional[int] = Field(None, ge=0)  # Duration >= 0
    art_url: Optional[str] = Field(None, alias="artUrl")


class PlaylistDTO(DomainModel):
    """
    Playlist metadata and information.

    Represents a music playlist.

    Attributes:
        playlist_id: Unique playlist identifier
        title: Playlist name
        track_count: Number of tracks in playlist
        art_url: Playlist art/cover URL

    Example:
        >>> playlist = PlaylistDTO(
        ...     playlistId="PLabc123",
        ...     title="My Favorites",
        ...     trackCount=42
        ... )
    """

    playlist_id: Optional[str] = Field(None, alias="playlistId")
    title: str
    track_count: int = Field(0, alias="trackCount", ge=0)
    art_url: Optional[str] = Field(None, alias="artUrl")


class PlayMusicRequest(RequestDTO):
    """
    Request to play music on a device.

    Supports playing by track ID, queue token, or other parameters.

    Attributes:
        track_id: Track to play (optional - use with deviceSerialNumber)
        queue_token: Queue to play (optional - alternative to trackId)
        device_serial_number: Target device serial number (required)
        shuffle_mode: "on" or "off" (optional)
        repeat_mode: "off", "all", "one" (optional)

    Example:
        >>> request = PlayMusicRequest(
        ...     trackId="TRACK123",
        ...     deviceSerialNumber="ABC123",
        ...     shuffleMode="off"
        ... )
    """

    track_id: Optional[str] = Field(None, alias="trackId")
    queue_token: Optional[str] = Field(None, alias="queueToken")
    device_serial_number: str = Field(..., alias="deviceSerialNumber", min_length=1)
    shuffle_mode: Optional[str] = Field(None, alias="shuffleMode")
    repeat_mode: Optional[str] = Field(None, alias="repeatMode")

    @field_validator("shuffle_mode", mode="before")
    @classmethod
    def validate_shuffle_mode(cls, v):
        """Shuffle mode should be 'on' or 'off'."""
        if v is not None and v not in ("on", "off"):
            raise ValueError("shuffle_mode must be 'on' or 'off'")
        return v

    @field_validator("repeat_mode", mode="before")
    @classmethod
    def validate_repeat_mode(cls, v):
        """Repeat mode should be 'off', 'all', or 'one'."""
        if v is not None and v not in ("off", "all", "one"):
            raise ValueError("repeat_mode must be 'off', 'all', or 'one'")
        return v

    @field_validator("track_id", "queue_token", mode="before")
    @classmethod
    def require_track_or_queue(cls, v, info):
        """Either track_id or queue_token must be provided."""
        # This will be validated at class level, we'll check in __init__
        return v

    def __init__(self, **data):
        """Ensure either track_id or queue_token is provided."""
        super().__init__(**data)
        if not self.track_id and not self.queue_token:
            raise ValueError("Either trackId or queueToken must be provided")


class PlayMusicResponse(ResponseDTO):
    """
    Response from play music command.

    Indicates whether music playback was initiated successfully.

    Attributes:
        success: Whether play command succeeded
        is_playing: Whether music is now playing
        error: Error message if failed (optional)

    Example:
        >>> response = PlayMusicResponse(
        ...     success=True,
        ...     isPlaying=True
        ... )
    """

    success: bool = True
    is_playing: bool = Field(False, alias="isPlaying")
    error: Optional[str] = None


class MusicStatusResponse(ResponseDTO):
    """
    Current music playback status.

    Returns current playback information including current track,
    playback position, volume, etc.

    Attributes:
        is_playing: Whether music is currently playing
        volume: Current volume level (0-100)
        current_track: Currently playing track (optional)
        progress: Current playback position in seconds
        duration: Total track duration in seconds
        queue_length: Number of tracks in queue
        queue_index: Current position in queue

    Example:
        >>> status = MusicStatusResponse(
        ...     isPlaying=True,
        ...     volume=50,
        ...     currentTrack={"trackId": "T1", "title": "Song", "artist": "Artist"},
        ...     progress=45,
        ...     duration=180
        ... )
    """

    is_playing: bool = Field(False, alias="isPlaying")
    volume: int = Field(0, ge=0, le=100)
    current_track: Optional[TrackDTO] = Field(None, alias="currentTrack")
    progress: int = Field(0, ge=0)
    duration: Optional[int] = Field(None, ge=0)
    queue_length: Optional[int] = Field(None, alias="queueLength", ge=0)
    queue_index: Optional[int] = Field(None, alias="queueIndex", ge=0)


class MusicSearchResponse(ResponseDTO):
    """
    Search results for music query.

    Contains list of tracks/playlists matching search criteria.

    Attributes:
        results: List of matching tracks
        total_count: Total number of results available (may be > len(results))

    Example:
        >>> response = MusicSearchResponse(
        ...     results=[
        ...         {"trackId": "T1", "title": "Song", "artist": "Artist"}
        ...     ],
        ...     totalCount=1000
        ... )
    """

    results: List[TrackDTO] = []
    total_count: Optional[int] = Field(None, alias="totalCount")


class MusicLibraryResponse(ResponseDTO):
    """
    User's music library information.

    Returns playlists, artists, albums from user's library.

    Attributes:
        playlists: User's playlists
        artists: Artists in library
        albums: Albums in library

    Example:
        >>> response = MusicLibraryResponse(
        ...     playlists=[
        ...         {"playlistId": "P1", "title": "Favorites", "trackCount": 50}
        ...     ]
        ... )
    """

    playlists: Optional[List[PlaylistDTO]] = None
    artists: Optional[List[str]] = None
    albums: Optional[List[str]] = None


class QueueResponse(ResponseDTO):
    """
    Current playback queue.

    List of tracks in queue with current playing index.

    Attributes:
        tracks: List of queued tracks
        current_index: Index of currently playing track

    Example:
        >>> response = QueueResponse(
        ...     tracks=[
        ...         {"trackId": "T1", "title": "Song 1", "artist": "Artist"},
        ...         {"trackId": "T2", "title": "Song 2", "artist": "Artist"}
        ...     ],
        ...     currentIndex=0
        ... )
    """

    tracks: List[TrackDTO] = []
    current_index: int = Field(0, alias="currentIndex", ge=0)


__all__ = [
    "TrackDTO",
    "PlaylistDTO",
    "PlayMusicRequest",
    "PlayMusicResponse",
    "MusicStatusResponse",
    "MusicSearchResponse",
    "MusicLibraryResponse",
    "QueueResponse",
]
