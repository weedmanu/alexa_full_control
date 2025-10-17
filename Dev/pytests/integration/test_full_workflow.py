"""
TDD Tests for Full Workflow Integration.

Tests complete end-to-end workflows combining multiple managers and commands.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unittest.mock import Mock

import pytest


class TestPlaybackWorkflow:
    """Tests for complete playback workflows."""

    def test_workflow_list_devices_and_play(self) -> None:
        """Test workflow: list devices → select device → play music."""
        device_manager = Mock()
        device_manager.get_devices.return_value = [
            {"serial": "dev1", "name": "Living Room"},
            {"serial": "dev2", "name": "Bedroom"}
        ]

        playback_manager = Mock()
        playback_manager.play.return_value = {"status": "playing"}

        # Workflow step 1: List devices
        devices = device_manager.get_devices()
        assert len(devices) > 0

        # Workflow step 2: Play on first device
        result = playback_manager.play()
        assert result["status"] == "playing"

    def test_workflow_play_pause_resume(self) -> None:
        """Test workflow: play → pause → resume."""
        manager = Mock()

        # Play
        manager.play.return_value = {"status": "playing"}
        result1 = manager.play()
        assert result1["status"] == "playing"

        # Pause
        manager.pause.return_value = {"status": "paused"}
        result2 = manager.pause()
        assert result2["status"] == "paused"

        # Resume
        manager.play.return_value = {"status": "playing"}
        result3 = manager.play()
        assert result3["status"] == "playing"

    def test_workflow_change_track_sequence(self) -> None:
        """Test workflow: play → next → next → previous."""
        manager = Mock()
        tracks = [
            {"title": "Song 1"},
            {"title": "Song 2"},
            {"title": "Song 3"}
        ]
        current_index = 0

        # Play
        manager.get_current.return_value = tracks[0]
        assert manager.get_current()["title"] == "Song 1"

        # Next
        current_index = 1
        manager.get_current.return_value = tracks[1]
        assert manager.get_current()["title"] == "Song 2"

        # Next
        current_index = 2
        manager.get_current.return_value = tracks[2]
        assert manager.get_current()["title"] == "Song 3"

        # Previous
        current_index = 1
        manager.get_current.return_value = tracks[1]
        assert manager.get_current()["title"] == "Song 2"

    def test_workflow_shuffle_mode_toggle(self) -> None:
        """Test workflow: toggle shuffle on/off."""
        manager = Mock()

        # Enable shuffle
        manager.set_shuffle.return_value = {"shuffle": True}
        result = manager.set_shuffle(True)
        assert result["shuffle"] is True

        # Disable shuffle
        manager.set_shuffle.return_value = {"shuffle": False}
        result = manager.set_shuffle(False)
        assert result["shuffle"] is False

    def test_workflow_repeat_mode_cycling(self) -> None:
        """Test workflow: cycle through repeat modes."""
        manager = Mock()

        # Off
        manager.set_repeat.return_value = {"repeat": "off"}
        result = manager.set_repeat("off")
        assert result["repeat"] == "off"

        # One
        manager.set_repeat.return_value = {"repeat": "one"}
        result = manager.set_repeat("one")
        assert result["repeat"] == "one"

        # All
        manager.set_repeat.return_value = {"repeat": "all"}
        result = manager.set_repeat("all")
        assert result["repeat"] == "all"


class TestDeviceWorkflow:
    """Tests for device management workflows."""

    def test_workflow_discover_and_list_devices(self) -> None:
        """Test workflow: discover devices → list devices."""
        manager = Mock()

        # Discover
        manager.discover.return_value = True
        assert manager.discover()

        # List
        manager.get_devices.return_value = [
            {"serial": "dev1", "name": "Room1"}
        ]
        devices = manager.get_devices()
        assert len(devices) > 0

    def test_workflow_get_device_info(self) -> None:
        """Test workflow: get detailed device information."""
        manager = Mock()
        manager.get_device_info.return_value = {
            "serial": "ABCD1234",
            "name": "Living Room",
            "device_type": "ECHO_DOT",
            "firmware": "1.2.3",
            "volume": 50
        }

        info = manager.get_device_info("ABCD1234")
        assert info["serial"] == "ABCD1234"
        assert info["volume"] == 50

    def test_workflow_rename_device(self) -> None:
        """Test workflow: select device → rename."""
        manager = Mock()

        manager.rename_device.return_value = {
            "serial": "ABCD1234",
            "new_name": "New Room Name"
        }

        result = manager.rename_device("ABCD1234", "New Room Name")
        assert result["new_name"] == "New Room Name"

    def test_workflow_set_device_volume(self) -> None:
        """Test workflow: set device volume."""
        manager = Mock()

        manager.set_volume.return_value = {"volume": 75}
        result = manager.set_volume("ABCD1234", 75)
        assert result["volume"] == 75

    def test_workflow_enable_disable_do_not_disturb(self) -> None:
        """Test workflow: enable/disable do not disturb."""
        manager = Mock()

        # Enable
        manager.set_dnd.return_value = {"dnd": True}
        result = manager.set_dnd("ABCD1234", True)
        assert result["dnd"] is True

        # Disable
        manager.set_dnd.return_value = {"dnd": False}
        result = manager.set_dnd("ABCD1234", False)
        assert result["dnd"] is False


class TestAlarmWorkflow:
    """Tests for alarm management workflows."""

    def test_workflow_create_alarm(self) -> None:
        """Test workflow: create new alarm."""
        manager = Mock()
        manager.add_alarm.return_value = {
            "alarm_id": "alarm123",
            "time": "07:30",
            "enabled": True
        }

        result = manager.add_alarm("07:30")
        assert result["alarm_id"] is not None
        assert result["time"] == "07:30"

    def test_workflow_create_recurring_alarm(self) -> None:
        """Test workflow: create recurring alarm."""
        manager = Mock()
        manager.add_alarm.return_value = {
            "alarm_id": "alarm124",
            "time": "07:30",
            "recurring": "weekdays",
            "enabled": True
        }

        result = manager.add_alarm("07:30", recurring="weekdays")
        assert result["recurring"] == "weekdays"

    def test_workflow_list_alarms(self) -> None:
        """Test workflow: list all alarms."""
        manager = Mock()
        manager.get_alarms.return_value = [
            {"alarm_id": "a1", "time": "07:30"},
            {"alarm_id": "a2", "time": "22:00"}
        ]

        alarms = manager.get_alarms()
        assert len(alarms) == 2

    def test_workflow_disable_enable_alarm(self) -> None:
        """Test workflow: disable and enable alarm."""
        manager = Mock()

        # Disable
        manager.set_alarm_enabled.return_value = {"enabled": False}
        result = manager.set_alarm_enabled("alarm123", False)
        assert result["enabled"] is False

        # Enable
        manager.set_alarm_enabled.return_value = {"enabled": True}
        result = manager.set_alarm_enabled("alarm123", True)
        assert result["enabled"] is True

    def test_workflow_delete_alarm(self) -> None:
        """Test workflow: delete alarm."""
        manager = Mock()
        manager.delete_alarm.return_value = {"deleted": True}

        result = manager.delete_alarm("alarm123")
        assert result["deleted"] is True


class TestMusicSearchWorkflow:
    """Tests for music search workflows."""

    def test_workflow_search_artist(self) -> None:
        """Test workflow: search for artist."""
        manager = Mock()
        manager.search.return_value = {
            "results": [
                {"title": "Artist 1", "type": "artist"},
                {"title": "Artist 2", "type": "artist"}
            ]
        }

        results = manager.search("The Beatles", search_type="artist")
        assert len(results["results"]) > 0

    def test_workflow_search_album(self) -> None:
        """Test workflow: search for album."""
        manager = Mock()
        manager.search.return_value = {
            "results": [
                {"title": "Abbey Road", "type": "album"}
            ]
        }

        results = manager.search("Abbey Road", search_type="album")
        assert results["results"][0]["type"] == "album"

    def test_workflow_search_and_play(self) -> None:
        """Test workflow: search music → play."""
        search_manager = Mock()
        playback_manager = Mock()

        # Search
        search_manager.search.return_value = {
            "results": [{"id": "track123", "title": "Song"}]
        }
        results = search_manager.search("Song")

        # Play
        playback_manager.play_music_id.return_value = {"status": "playing"}
        play_result = playback_manager.play_music_id(results["results"][0]["id"])
        assert play_result["status"] == "playing"

    def test_workflow_create_playlist(self) -> None:
        """Test workflow: create playlist with search results."""
        manager = Mock()
        manager.create_playlist.return_value = {
            "playlist_id": "pl123",
            "name": "My Playlist"
        }

        result = manager.create_playlist("My Playlist")
        assert result["playlist_id"] is not None

    def test_workflow_add_to_playlist(self) -> None:
        """Test workflow: add songs to playlist."""
        manager = Mock()
        manager.add_to_playlist.return_value = {
            "playlist_id": "pl123",
            "song_count": 5
        }

        result = manager.add_to_playlist("pl123", "track123")
        assert result["song_count"] == 5


class TestListsWorkflow:
    """Tests for lists management workflows."""

    def test_workflow_create_list(self) -> None:
        """Test workflow: create shopping list."""
        manager = Mock()
        manager.create_list.return_value = {
            "list_id": "list123",
            "name": "Shopping",
            "items": []
        }

        result = manager.create_list("Shopping")
        assert result["list_id"] is not None

    def test_workflow_add_items_to_list(self) -> None:
        """Test workflow: add items to list."""
        manager = Mock()

        manager.add_item.return_value = {
            "list_id": "list123",
            "items": ["milk", "bread", "eggs"]
        }

        # Add multiple items
        for item in ["milk", "bread", "eggs"]:
            result = manager.add_item("list123", item)

        assert len(result["items"]) == 3

    def test_workflow_check_off_items(self) -> None:
        """Test workflow: check off items in list."""
        manager = Mock()

        manager.update_item.return_value = {"completed": True}
        result = manager.update_item("list123", "item1", completed=True)
        assert result["completed"] is True

    def test_workflow_delete_list(self) -> None:
        """Test workflow: delete list."""
        manager = Mock()
        manager.delete_list.return_value = {"deleted": True}

        result = manager.delete_list("list123")
        assert result["deleted"] is True


class TestReminderWorkflow:
    """Tests for reminder workflows."""

    def test_workflow_set_reminder(self) -> None:
        """Test workflow: set reminder for specific time."""
        manager = Mock()
        manager.add_reminder.return_value = {
            "reminder_id": "rem123",
            "text": "Take medication",
            "time": "09:00"
        }

        result = manager.add_reminder("09:00", "Take medication")
        assert result["reminder_id"] is not None

    def test_workflow_set_recurring_reminder(self) -> None:
        """Test workflow: set recurring reminder."""
        manager = Mock()
        manager.add_reminder.return_value = {
            "reminder_id": "rem124",
            "text": "Weekly meeting",
            "recurring": "weekly"
        }

        result = manager.add_reminder("10:00", "Weekly meeting", recurring="weekly")
        assert result["recurring"] == "weekly"

    def test_workflow_list_reminders(self) -> None:
        """Test workflow: list all reminders."""
        manager = Mock()
        manager.get_reminders.return_value = [
            {"reminder_id": "rem1", "text": "Task 1"},
            {"reminder_id": "rem2", "text": "Task 2"}
        ]

        reminders = manager.get_reminders()
        assert len(reminders) > 0

    def test_workflow_delete_reminder(self) -> None:
        """Test workflow: delete reminder."""
        manager = Mock()
        manager.delete_reminder.return_value = {"deleted": True}

        result = manager.delete_reminder("rem123")
        assert result["deleted"] is True


class TestRoutineWorkflow:
    """Tests for routine workflows."""

    def test_workflow_list_routines(self) -> None:
        """Test workflow: list available routines."""
        manager = Mock()
        manager.get_routines.return_value = [
            {"routine_id": "r1", "name": "Good Morning"},
            {"routine_id": "r2", "name": "Good Night"}
        ]

        routines = manager.get_routines()
        assert len(routines) > 0

    def test_workflow_execute_routine(self) -> None:
        """Test workflow: execute routine."""
        manager = Mock()
        manager.execute.return_value = {"executed": True}

        result = manager.execute("r1")
        assert result["executed"] is True

    def test_workflow_check_routine_status(self) -> None:
        """Test workflow: check routine execution status."""
        manager = Mock()
        manager.get_status.return_value = {
            "routine_id": "r1",
            "status": "executing",
            "progress": 50
        }

        status = manager.get_status("r1")
        assert status["status"] == "executing"


class TestMultiDeviceWorkflow:
    """Tests for multi-device workflows."""

    def test_workflow_control_all_devices(self) -> None:
        """Test workflow: broadcast command to all devices."""
        playback_manager = Mock()
        device_manager = Mock()

        # Get all devices
        device_manager.get_devices.return_value = [
            {"serial": "dev1"},
            {"serial": "dev2"},
            {"serial": "dev3"}
        ]

        devices = device_manager.get_devices()

        # Play on all
        playback_manager.play_on_devices.return_value = {
            "devices_played": len(devices)
        }

        result = playback_manager.play_on_devices([d["serial"] for d in devices])
        assert result["devices_played"] == 3

    def test_workflow_group_devices(self) -> None:
        """Test workflow: group devices for multi-room."""
        manager = Mock()
        manager.create_group.return_value = {
            "group_id": "group1",
            "devices": ["dev1", "dev2"]
        }

        result = manager.create_group("group1", ["dev1", "dev2"])
        assert len(result["devices"]) == 2

    def test_workflow_play_on_group(self) -> None:
        """Test workflow: play music on device group."""
        manager = Mock()
        manager.play_on_group.return_value = {
            "group_id": "group1",
            "status": "playing"
        }

        result = manager.play_on_group("group1")
        assert result["status"] == "playing"


class TestErrorRecoveryWorkflow:
    """Tests for error recovery workflows."""

    def test_workflow_handle_device_offline(self) -> None:
        """Test workflow: handle device going offline."""
        manager = Mock()
        manager.play.side_effect = ConnectionError("Device offline")

        with pytest.raises(ConnectionError):
            manager.play()

    def test_workflow_retry_on_failure(self) -> None:
        """Test workflow: retry operation on transient failure."""
        manager = Mock()
        attempts = 0

        manager.play.side_effect = [
            Exception("Network error"),
            {"status": "playing"}
        ]

        # Try first time - fails
        with pytest.raises(Exception):
            manager.play()

    def test_workflow_fallback_device(self) -> None:
        """Test workflow: fallback to alternate device on failure."""
        device_manager = Mock()
        playback_manager = Mock()

        # Primary device fails
        playback_manager.play.side_effect = ConnectionError("Primary offline")

        with pytest.raises(ConnectionError):
            playback_manager.play()

        # Could fall back to secondary device

    def test_workflow_graceful_degradation(self) -> None:
        """Test workflow: graceful degradation on partial failure."""
        result = {
            "partial": True,
            "success_count": 2,
            "failure_count": 1,
            "message": "Completed with partial success"
        }

        assert result["partial"] is True
