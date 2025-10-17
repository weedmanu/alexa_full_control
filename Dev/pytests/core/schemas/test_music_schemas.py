"""
Music Schema Tests - Phase 3.5 (TDD)

Tests for music-related DTOs (Data Transfer Objects).
Covers: playback control, music status, playlists, tracks, library operations.

Test Coverage:
- Music playback status responses
- Track and playlist data models
- Play music requests with queue/shuffle options
- Music search responses
- Music library management
- Queue management
- Music source/provider handling (Amazon Music, TuneIn, etc)

Tests are written BEFORE implementation (Test-Driven Development).
Implementation: core/schemas/music_schemas.py
"""

import pytest
from typing import List, Optional
from pydantic import ValidationError
from datetime import datetime


class TestPlayMusicRequest:
    """Test PlayMusicRequest for music playback commands."""

    def test_play_music_request_with_trackid(self):
        """Should play music by track ID."""
        from core.schemas.music_schemas import PlayMusicRequest
        
        request = PlayMusicRequest(
            trackId="TRACK123",
            deviceSerialNumber="ABC123"
        )
        
        assert request.track_id == "TRACK123"
        assert request.device_serial_number == "ABC123"

    def test_play_music_request_with_queue_token(self):
        """Should play music from queue using queueToken."""
        from core.schemas.music_schemas import PlayMusicRequest
        
        request = PlayMusicRequest(
            queueToken="QUEUE_TOKEN_ABC",
            deviceSerialNumber="ABC123"
        )
        
        assert request.queue_token == "QUEUE_TOKEN_ABC"

    def test_play_music_request_requires_device_serial(self):
        """deviceSerialNumber is required."""
        from core.schemas.music_schemas import PlayMusicRequest
        
        with pytest.raises(ValidationError):
            PlayMusicRequest(trackId="TRACK123")

    def test_play_music_request_requires_either_track_or_queue(self):
        """Must provide either trackId or queueToken."""
        from core.schemas.music_schemas import PlayMusicRequest
        
        # Neither trackId nor queueToken provided
        # This raises ValueError from __init__, not ValidationError
        with pytest.raises(ValueError):
            PlayMusicRequest(deviceSerialNumber="ABC123")

    def test_play_music_request_with_shuffle_mode(self):
        """Should support shuffleMode parameter."""
        from core.schemas.music_schemas import PlayMusicRequest
        
        request = PlayMusicRequest(
            trackId="TRACK123",
            deviceSerialNumber="ABC123",
            shuffleMode="on"
        )
        
        assert request.shuffle_mode == "on"

    def test_play_music_request_with_repeat_mode(self):
        """Should support repeatMode parameter."""
        from core.schemas.music_schemas import PlayMusicRequest
        
        request = PlayMusicRequest(
            trackId="TRACK123",
            deviceSerialNumber="ABC123",
            repeatMode="one"
        )
        
        assert request.repeat_mode == "one"

    def test_play_music_request_immutable(self):
        """PlayMusicRequest should be immutable (frozen=True)."""
        from core.schemas.music_schemas import PlayMusicRequest
        
        request = PlayMusicRequest(
            trackId="TRACK123",
            deviceSerialNumber="ABC123"
        )
        
        # RequestDTO is frozen - should not allow modification
        with pytest.raises(Exception):  # FrozenInstanceError
            request.track_id = "DIFFERENT_TRACK"


class TestTrackDTO:
    """Test TrackDTO for individual track data."""

    def test_track_from_amazon_api_response(self):
        """Should parse track from Amazon Music API response."""
        from core.schemas.music_schemas import TrackDTO
        
        api_data = {
            "trackId": "TRACK123",
            "title": "Song Title",
            "artist": "Artist Name",
            "album": "Album Name",
            "duration": 180,
            "artUrl": "https://example.com/art.jpg"
        }
        
        track = TrackDTO(**api_data)
        
        assert track.track_id == "TRACK123"
        assert track.title == "Song Title"
        assert track.artist == "Artist Name"
        assert track.duration == 180

    def test_track_requires_title(self):
        """Title is required field."""
        from core.schemas.music_schemas import TrackDTO
        
        with pytest.raises(ValidationError):
            TrackDTO(trackId="TRACK123", artist="Artist")

    def test_track_requires_artist(self):
        """Artist is required field."""
        from core.schemas.music_schemas import TrackDTO
        
        with pytest.raises(ValidationError):
            TrackDTO(trackId="TRACK123", title="Song")

    def test_track_optional_fields(self):
        """Album, duration, artUrl should be optional."""
        from core.schemas.music_schemas import TrackDTO
        
        track = TrackDTO(
            trackId="TRACK123",
            title="Song",
            artist="Artist"
        )
        
        assert track.album is None
        assert track.duration is None
        assert track.art_url is None

    def test_track_with_all_fields(self):
        """Should handle all track fields."""
        from core.schemas.music_schemas import TrackDTO
        
        track = TrackDTO(
            trackId="TRACK123",
            title="Song",
            artist="Artist",
            album="Album",
            duration=240,
            artUrl="https://example.com/art.jpg"
        )
        
        assert track.track_id == "TRACK123"
        assert track.album == "Album"
        assert track.duration == 240
        assert track.art_url == "https://example.com/art.jpg"


class TestPlaylistDTO:
    """Test PlaylistDTO for playlist data."""

    def test_playlist_from_amazon_api_response(self):
        """Should parse playlist from Amazon API response."""
        from core.schemas.music_schemas import PlaylistDTO
        
        api_data = {
            "playlistId": "PLAYLIST123",
            "title": "My Playlist",
            "trackCount": 25,
            "artUrl": "https://example.com/playlist.jpg"
        }
        
        playlist = PlaylistDTO(**api_data)
        
        assert playlist.playlist_id == "PLAYLIST123"
        assert playlist.title == "My Playlist"
        assert playlist.track_count == 25

    def test_playlist_requires_title(self):
        """Title is required."""
        from core.schemas.music_schemas import PlaylistDTO
        
        with pytest.raises(ValidationError):
            PlaylistDTO(playlistId="PLAYLIST123")

    def test_playlist_track_count_non_negative(self):
        """Track count should be >= 0."""
        from core.schemas.music_schemas import PlaylistDTO
        
        playlist = PlaylistDTO(
            playlistId="PLAYLIST123",
            title="Empty Playlist",
            trackCount=0
        )
        
        assert playlist.track_count == 0


class TestMusicStatusResponse:
    """Test MusicStatusResponse for current playback status."""

    def test_music_status_from_amazon_api(self):
        """Should parse current music status from API."""
        from core.schemas.music_schemas import MusicStatusResponse
        
        api_data = {
            "currentTrack": {
                "trackId": "TRACK123",
                "title": "Now Playing",
                "artist": "Artist"
            },
            "isPlaying": True,
            "progress": 45,
            "duration": 180,
            "volume": 50
        }
        
        status = MusicStatusResponse(**api_data)
        
        assert status.current_track.track_id == "TRACK123"
        assert status.is_playing is True
        assert status.progress == 45
        assert status.volume == 50

    def test_music_status_stopped(self):
        """Should represent stopped/idle music state."""
        from core.schemas.music_schemas import MusicStatusResponse
        
        status = MusicStatusResponse(
            isPlaying=False,
            volume=0
        )
        
        assert status.is_playing is False
        assert status.current_track is None

    def test_music_status_volume_range(self):
        """Volume should be 0-100."""
        from core.schemas.music_schemas import MusicStatusResponse
        
        # Valid volumes
        for vol in [0, 50, 100]:
            status = MusicStatusResponse(isPlaying=False, volume=vol)
            assert status.volume == vol

    def test_music_status_with_queue_info(self):
        """Should include queue information."""
        from core.schemas.music_schemas import MusicStatusResponse
        
        status = MusicStatusResponse(
            isPlaying=True,
            volume=50,
            queueLength=10,
            queueIndex=3
        )
        
        assert status.queue_length == 10
        assert status.queue_index == 3

    def test_music_status_immutable(self):
        """MusicStatusResponse should be immutable."""
        from core.schemas.music_schemas import MusicStatusResponse
        
        status = MusicStatusResponse(isPlaying=True, volume=50)
        
        # ResponseDTO is frozen
        with pytest.raises(Exception):  # FrozenInstanceError
            status.is_playing = False


class TestMusicSearchResponse:
    """Test MusicSearchResponse for music search results."""

    def test_search_returns_tracks(self):
        """Should return list of matching tracks."""
        from core.schemas.music_schemas import MusicSearchResponse
        
        response_data = {
            "results": [
                {
                    "trackId": "TRACK1",
                    "title": "Song 1",
                    "artist": "Artist A"
                },
                {
                    "trackId": "TRACK2",
                    "title": "Song 2",
                    "artist": "Artist B"
                }
            ]
        }
        
        response = MusicSearchResponse(**response_data)
        
        assert len(response.results) == 2
        assert response.results[0].track_id == "TRACK1"

    def test_empty_search_results(self):
        """Should handle empty search results."""
        from core.schemas.music_schemas import MusicSearchResponse
        
        response = MusicSearchResponse(results=[])
        
        assert len(response.results) == 0

    def test_search_with_total_count(self):
        """Should include total result count."""
        from core.schemas.music_schemas import MusicSearchResponse
        
        response = MusicSearchResponse(
            results=[],
            totalCount=1000
        )
        
        assert response.total_count == 1000


class TestMusicLibraryResponse:
    """Test MusicLibraryResponse for library info."""

    def test_library_playlists(self):
        """Should return user's playlists."""
        from core.schemas.music_schemas import MusicLibraryResponse
        
        response_data = {
            "playlists": [
                {
                    "playlistId": "PLAYLIST1",
                    "title": "Favorites",
                    "trackCount": 50
                }
            ]
        }
        
        response = MusicLibraryResponse(**response_data)
        
        assert len(response.playlists) == 1
        assert response.playlists[0].title == "Favorites"

    def test_library_artists(self):
        """Should return list of artists in library."""
        from core.schemas.music_schemas import MusicLibraryResponse
        
        response = MusicLibraryResponse(
            artists=["Artist 1", "Artist 2"]
        )
        
        assert len(response.artists) == 2


class TestQueueResponse:
    """Test QueueResponse for playback queue."""

    def test_queue_tracks(self):
        """Should return queue tracks."""
        from core.schemas.music_schemas import QueueResponse
        
        response_data = {
            "tracks": [
                {
                    "trackId": "TRACK1",
                    "title": "First",
                    "artist": "Artist"
                },
                {
                    "trackId": "TRACK2",
                    "title": "Second",
                    "artist": "Artist"
                }
            ],
            "currentIndex": 0
        }
        
        response = QueueResponse(**response_data)
        
        assert len(response.tracks) == 2
        assert response.current_index == 0

    def test_queue_current_track(self):
        """Should identify current track."""
        from core.schemas.music_schemas import QueueResponse
        
        response = QueueResponse(
            tracks=[
                {"trackId": "TRACK1", "title": "First", "artist": "A"},
                {"trackId": "TRACK2", "title": "Current", "artist": "A"}
            ],
            currentIndex=1
        )
        
        current = response.tracks[response.current_index]
        assert current.track_id == "TRACK2"


class TestPlayMusicResponse:
    """Test PlayMusicResponse for play command result."""

    def test_play_music_success(self):
        """Should confirm music is now playing."""
        from core.schemas.music_schemas import PlayMusicResponse
        
        response = PlayMusicResponse(
            success=True,
            isPlaying=True
        )
        
        assert response.success is True
        assert response.is_playing is True

    def test_play_music_failure(self):
        """Should report play failure with error."""
        from core.schemas.music_schemas import PlayMusicResponse
        
        response = PlayMusicResponse(
            success=False,
            error="Track not found"
        )
        
        assert response.success is False
        assert response.error == "Track not found"


class TestMusicSchemaIntegration:
    """Integration tests for music schemas."""

    def test_search_then_play_workflow(self):
        """Should support search -> play workflow."""
        from core.schemas.music_schemas import (
            MusicSearchResponse, PlayMusicRequest
        )
        
        # Search for music
        search_result = MusicSearchResponse(
            results=[
                {
                    "trackId": "TRACK123",
                    "title": "Song",
                    "artist": "Artist"
                }
            ]
        )
        
        # Get first result and play it
        track = search_result.results[0]
        play_request = PlayMusicRequest(
            trackId=track.track_id,
            deviceSerialNumber="ABC123"
        )
        
        assert play_request.track_id == "TRACK123"

    def test_status_update_workflow(self):
        """Should track music status through playback."""
        from core.schemas.music_schemas import MusicStatusResponse
        
        # Initial status
        status = MusicStatusResponse(
            isPlaying=True,
            volume=50,
            currentTrack={
                "trackId": "TRACK1",
                "title": "Song",
                "artist": "Artist"
            },
            progress=30,
            duration=180
        )
        
        # Verify current playback info
        assert status.current_track is not None
        assert status.progress < status.duration


class TestMusicAliasConversion:
    """Test field name conversions (camelCase ↔ snake_case)."""

    def test_track_field_aliases(self):
        """Track should accept both camelCase and snake_case."""
        from core.schemas.music_schemas import TrackDTO
        
        # Using camelCase (API format)
        track1 = TrackDTO(
            trackId="T1",
            title="Song",
            artist="Artist",
            artUrl="https://example.com/art.jpg"
        )
        
        # Using snake_case (Python format)
        track2 = TrackDTO(
            track_id="T1",
            title="Song",
            artist="Artist",
            art_url="https://example.com/art.jpg"
        )
        
        assert track1.track_id == track2.track_id
        assert track1.art_url == track2.art_url

    def test_response_json_uses_aliases(self):
        """JSON output should use camelCase (API format)."""
        from core.schemas.music_schemas import TrackDTO
        
        track = TrackDTO(
            track_id="TRACK1",
            title="Song",
            artist="Artist"
        )
        
        json_data = track.model_dump(by_alias=True)
        
        # Verify camelCase in JSON
        assert "trackId" in json_data
        assert json_data["trackId"] == "TRACK1"


class TestMusicSchemaValidation:
    """Test validation rules for music schemas."""

    def test_duration_positive(self):
        """Duration should be positive if provided."""
        from core.schemas.music_schemas import TrackDTO
        
        # Valid
        track = TrackDTO(
            trackId="T1",
            title="Song",
            artist="Artist",
            duration=180
        )
        assert track.duration == 180

    def test_volume_bounds(self):
        """Volume should be bounded 0-100."""
        from core.schemas.music_schemas import MusicStatusResponse
        
        # Valid
        status = MusicStatusResponse(isPlaying=False, volume=75)
        assert status.volume == 75

    def test_rejects_unknown_fields(self):
        """Should reject unknown API fields (strict mode)."""
        from core.schemas.music_schemas import TrackDTO
        
        with pytest.raises(ValidationError):
            TrackDTO(
                trackId="T1",
                title="Song",
                artist="Artist",
                unknownField="should fail"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
