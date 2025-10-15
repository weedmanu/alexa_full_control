
import unittest
import os
from unittest.mock import MagicMock, patch, mock_open, call
from datetime import datetime, timedelta
import json
from pathlib import Path
import time
import threading

from core.activity_manager import ActivityManager
from core.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerError
from core.state_machine import AlexaStateMachine, ConnectionState, StateTransitionError

class TestActivityManager(unittest.TestCase):

    def setUp(self):
        self.auth = MagicMock()
        # Ensure legacy .session exists for managers that may wrap auth into http_client
        self.auth.session = MagicMock()
        # Provide a typed http_client mock for tests (allows setting .get/.post/.put/.delete)
        self.http_client = MagicMock()
        self.http_client.csrf = getattr(self.auth, "csrf", None)
        self.config = MagicMock()
        self.state_machine = MagicMock()
        self.activity_manager = ActivityManager(self.auth, self.config, self.state_machine)
        # Ensure the ActivityManager uses the typed http_client mock for API calls
        self.activity_manager.http_client = self.http_client

    def test_initialization(self):
        self.assertIsNotNone(self.activity_manager)
        self.assertEqual(self.activity_manager.auth, self.auth)
        self.assertEqual(self.activity_manager.config, self.config)
        self.assertEqual(self.activity_manager.state_machine, self.state_machine)

    @patch('core.activity_manager.ActivityManager.get_privacy_csrf')
    @patch('core.activity_manager.ActivityManager._fetch_privacy_api_records')
    @patch('core.activity_manager.ActivityManager._save_activities_to_cache')
    def test_get_customer_history_records_from_api(self, mock_save_cache, mock_fetch_api, mock_get_csrf):
        mock_get_csrf.return_value = 'test_csrf'
        mock_fetch_api.return_value = [{'id': 1}]

        records = self.activity_manager.get_customer_history_records()

        self.assertEqual(len(records), 1)
        mock_fetch_api.assert_called_once()
        mock_save_cache.assert_called_once_with([{'id': 1}])

    @patch('core.activity_manager.ActivityManager.get_privacy_csrf', return_value=None)
    @patch('core.activity_manager.ActivityManager._get_activities_from_cache')
    def test_get_customer_history_records_from_cache(self, mock_get_cache, mock_get_csrf):
        mock_get_cache.return_value = [{'id': 2}]

        records = self.activity_manager.get_customer_history_records()

        self.assertEqual(len(records), 1)
        mock_get_cache.assert_called_once()

    @patch('core.activity_manager.datetime')
    def test_fetch_privacy_api_records(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 1, 1)
        self.http_client.post.return_value.json.return_value = {'customerHistoryRecords': [{'id': 1}]}

        records = self.activity_manager._fetch_privacy_api_records(10, None, 'test_csrf')

        self.assertEqual(len(records), 1)
        self.http_client.post.assert_called_once()

    def test_save_activities_to_cache(self):
        with patch('core.activity_manager.ActivityManager._save_to_local_cache') as mock_save:
            self.activity_manager._save_activities_to_cache([{'id': 1}])
            mock_save.assert_called_once()

    @patch('core.activity_manager.ActivityManager._load_from_local_cache')
    def test_get_activities_from_cache(self, mock_load):
        mock_load.return_value = {'records': [{'id': 1, 'timestamp': datetime.now().timestamp()}]}
        records = self.activity_manager._get_activities_from_cache(10, None)
        self.assertEqual(len(records), 1)

    def test_get_mock_activities(self):
        records = self.activity_manager._get_mock_activities(2)
        self.assertEqual(len(records), 2)

    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.mkdir')
    def test_save_to_local_cache(self, mock_mkdir, mock_write_text):
        self.activity_manager._save_to_local_cache('test_key', {'data': 'test_data'})
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_write_text.assert_called_once()

    @patch('pathlib.Path.read_text', return_value='{"records": []}')
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_from_local_cache(self, mock_exists, mock_read_text):
        data = self.activity_manager._load_from_local_cache('test_key')
        self.assertEqual(data, {"records": []})

    def test_get_privacy_csrf_from_auth(self):
        self.auth.csrf = 'test_csrf'
        csrf = self.activity_manager.get_privacy_csrf()
        self.assertEqual(csrf, 'test_csrf')

    @patch('core.activity_manager.ActivityManager._extract_csrf_from_html', return_value='html_csrf')
    def test_get_privacy_csrf_from_html(self, mock_extract):
        self.auth.csrf = None
        self.http_client.get.return_value.text = '<html></html>'

        csrf = self.activity_manager.get_privacy_csrf()

        self.assertEqual(csrf, 'html_csrf')

    def test_extract_csrf_from_html(self):
        html = '<html><input name="csrf" value="test_token" /></html>'
        token = self.activity_manager._extract_csrf_from_html(html)
        self.assertEqual(token, 'test_token')

    @patch('core.activity_manager.ActivityManager.get_customer_history_records')
    @patch('core.activity_manager.ActivityManager._convert_privacy_record_to_activity')
    def test_get_activities(self, mock_convert, mock_get_records):
        mock_get_records.return_value = [{'id': 1}]
        mock_convert.return_value = {'converted': True}

        activities = self.activity_manager.get_activities()

        self.assertEqual(len(activities), 1)
        self.assertTrue(activities[0]['converted'])

    def test_convert_privacy_record_to_activity(self):
        record = {
            "recordKey": "key",
            "timestamp": datetime.now().timestamp() * 1000,
            "device": {"serialNumber": "123", "deviceName": "Echo"},
            "voiceHistoryRecordItems": [
                {"recordItemType": "CUSTOMER_TRANSCRIPT", "transcriptText": "Hello"},
                {"recordItemType": "ALEXA_RESPONSE", "transcriptText": "Hi"}
            ]
        }
        activity = self.activity_manager._convert_privacy_record_to_activity(record)
        self.assertEqual(activity['utterance'], 'Hello')
        self.assertEqual(activity['alexaResponse'], 'Hi')

    @patch('builtins.open', new_callable=mock_open, read_data='{"devices": [{"serialNumber": "123", "accountName": "My Echo"}]}')
    @patch('pathlib.Path.exists', return_value=True)
    def test_get_device_info_from_cache(self, mock_exists, mock_file):
        info = self.activity_manager._get_device_info_from_cache("123")
        self.assertEqual(info['accountName'], 'My Echo')

    @patch('core.activity_manager.ActivityManager.get_activities')
    def test_get_activity(self, mock_get_activities):
        mock_get_activities.return_value = [{'id': '123'}]
        activity = self.activity_manager.get_activity('123')
        self.assertIsNotNone(activity)

    def test_delete_activity(self):
        self.assertFalse(self.activity_manager.delete_activity('123'))

    def test_delete_activities_range(self):
        self.assertFalse(self.activity_manager.delete_activities_range(datetime.now()))

    @patch('core.activity_manager.ActivityManager.get_activities')
    def test_get_last_device(self, mock_get_activities):
        mock_get_activities.return_value = [{'deviceName': 'Echo'}]
        device = self.activity_manager.get_last_device()
        self.assertEqual(device, 'Echo')

    @patch('core.activity_manager.ActivityManager.get_activities')
    def test_get_last_command(self, mock_get_activities):
        mock_get_activities.return_value = [{'type': 'voice', 'utterance': 'command'}]
        command = self.activity_manager.get_last_command()
        self.assertEqual(command, 'command')

    @patch('core.activity_manager.ActivityManager.get_activities')
    def test_get_voice_history(self, mock_get_activities):
        self.activity_manager.get_voice_history(days=7)
        mock_get_activities.assert_called_once()

    @patch('core.activity_manager.ActivityManager.delete_activities_range')
    def test_delete_voice_history(self, mock_delete_range):
        self.activity_manager.delete_voice_history(days=7)
        mock_delete_range.assert_called_once()

    @patch('core.activity_manager.ActivityManager.get_activities')
    def test_get_last_interaction(self, mock_get_activities):
        mock_get_activities.return_value = [{'id': '1'}]
        interaction = self.activity_manager.get_last_interaction()
        self.assertIsNotNone(interaction)

    @patch('core.activity_manager.ActivityManager._load_from_local_cache')
    @patch('core.activity_manager.ActivityManager._save_to_local_cache')
    def test_add_mock_activity(self, mock_save, mock_load):
        mock_load.return_value = {"records": []}
        result = self.activity_manager.add_mock_activity("test utterance", "test response")
        self.assertTrue(result)
        mock_save.assert_called_once()

    @patch('core.activity_manager.ActivityManager.get_activities')
    def test_get_last_response(self, mock_get_activities):
        mock_get_activities.return_value = [{'type': 'voice', 'alexaResponse': 'response'}]
        response = self.activity_manager.get_last_response()
        self.assertEqual(response, 'response')

    def test_get_customer_history_records_cannot_execute(self):
        self.state_machine.can_execute_commands = False
        records = self.activity_manager.get_customer_history_records()
        self.assertEqual(records, [])

    @patch('core.activity_manager.ActivityManager.get_privacy_csrf', side_effect=Exception('API Error'))
    @patch('core.activity_manager.ActivityManager._get_activities_from_cache')
    def test_get_customer_history_records_api_fails(self, mock_get_cache, mock_get_csrf):
        mock_get_cache.return_value = [{'id': 'from_cache'}]
        records = self.activity_manager.get_customer_history_records()
        self.assertEqual(records, [{'id': 'from_cache'}])
        mock_get_cache.assert_called_once()

    def test_fetch_privacy_api_records_with_limit(self):
        self.http_client.post.return_value.json.return_value = {'customerHistoryRecords': [{'id': 1}, {'id': 2}]}
        records = self.activity_manager._fetch_privacy_api_records(1, None, 'test_csrf')
        self.assertEqual(len(records), 1)

    @patch('core.activity_manager.ActivityManager._save_to_local_cache', side_effect=IOError)
    def test_save_activities_to_cache_exception(self, mock_save):
        self.activity_manager._save_activities_to_cache([{'id': 1}])
        mock_save.assert_called_once()

    @patch('core.activity_manager.ActivityManager._load_from_local_cache', return_value=None)
    @patch('core.activity_manager.ActivityManager._get_mock_activities')
    def test_get_activities_from_cache_empty(self, mock_get_mock, mock_load):
        self.activity_manager._get_activities_from_cache(10, None)
        mock_get_mock.assert_called_once()

    @patch('core.activity_manager.ActivityManager._load_from_local_cache')
    def test_get_activities_from_cache_with_start_time(self, mock_load):
        now = datetime.now()
        records = [
            {'id': 1, 'timestamp': (now - timedelta(minutes=10)).timestamp()},
            {'id': 2, 'timestamp': (now + timedelta(minutes=10)).timestamp()}
        ]
        mock_load.return_value = {'records': records}

        filtered_records = self.activity_manager._get_activities_from_cache(10, now.timestamp() * 1000)
        self.assertEqual(len(filtered_records), 1)
        self.assertEqual(filtered_records[0]['id'], 2)

    @patch('core.activity_manager.ActivityManager._load_from_local_cache', side_effect=IOError)
    @patch('core.activity_manager.ActivityManager._get_mock_activities')
    def test_get_activities_from_cache_exception(self, mock_get_mock, mock_load):
        self.activity_manager._get_activities_from_cache(10, None)
        mock_get_mock.assert_called_once()

    def test_get_privacy_csrf_cannot_execute(self):
        self.state_machine.can_execute_commands = False
        csrf = self.activity_manager.get_privacy_csrf()
        self.assertIsNone(csrf)

    @patch('requests.get', side_effect=Exception('Request failed'))
    def test_get_privacy_csrf_html_request_fails(self, mock_get):
        self.auth.csrf = None
        # Use http_client mock for migrated tests
        self.http_client.get.side_effect = Exception("Request failed")
        csrf = self.activity_manager.get_privacy_csrf()
        self.assertIsNone(csrf)

    def test_extract_csrf_from_html_all_patterns(self):
        test_cases = {
            "token1": '<html><body><input name="csrf" value="token1"/></body></html>',
            "token2": '<html><body><meta name="csrf" content="token2"/></body></html>',
            "token3": "<html><body><script>var appConfig = {csrf: 'token3'};</script></body></html>",
            "token4": "<html><body><script>var appConfig = {'anti-csrftoken-a2z': 'token4'};</script></body></html>",
            "token5": "<html><body><script>var appConfig = {csrfToken: 'token5'};</script></body></html>",
            "token6": "<html><body><script>var appConfig = {_csrf: 'token6'};</script></body></html>",
        }

        for expected_token, html in test_cases.items():
            with self.subTest(f"Testing for {expected_token}"):
                extracted_token = self.activity_manager._extract_csrf_from_html(html)
                self.assertEqual(extracted_token, expected_token)

    def test_get_activities_cannot_execute(self):
        self.state_machine.can_execute_commands = False
        activities = self.activity_manager.get_activities()
        self.assertEqual(activities, [])

    @patch('core.activity_manager.ActivityManager.get_customer_history_records', return_value=[])
    def test_get_activities_no_records(self, mock_get_records):
        activities = self.activity_manager.get_activities()
        self.assertEqual(activities, [])

    def test_convert_privacy_record_to_activity_malformed(self):
        activity = self.activity_manager._convert_privacy_record_to_activity({})
        self.assertIsNotNone(activity)
        self.assertEqual(activity['activityStatus'], 'UNKNOWN')

    def test_convert_privacy_record_to_activity_exception(self):
        record = {"device": "not_a_dict"}
        activity = self.activity_manager._convert_privacy_record_to_activity(record)
        self.assertIsNone(activity)

    @patch('builtins.open', side_effect=IOError)
    @patch('pathlib.Path.exists', return_value=True)
    def test_get_device_info_from_cache_exception(self, mock_exists, mock_open):
        info = self.activity_manager._get_device_info_from_cache("123")
        self.assertIsNone(info)

class TestCircuitBreaker(unittest.TestCase):

    def setUp(self):
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=1)

    def test_initial_state(self):
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
        self.assertEqual(self.breaker.failure_count, 0)
        self.assertFalse(self.breaker.is_open)

    def test_successful_call(self):
        result = self.breaker.call(lambda: "success")
        self.assertEqual(result, "success")
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
        self.assertEqual(self.breaker.failure_count, 0)

    def test_failures_below_threshold(self):
        with self.assertRaises(ValueError):
            self.breaker.call(lambda: exec("raise ValueError('failure')"))
        self.assertEqual(self.breaker.failure_count, 1)
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)

    def test_failures_reaching_threshold(self):
        for _ in range(3):
            with self.assertRaises(ValueError):
                self.breaker.call(lambda: exec("raise ValueError('failure')"))

        self.assertEqual(self.breaker.failure_count, 3)
        self.assertEqual(self.breaker.state, CircuitState.OPEN)
        self.assertTrue(self.breaker.is_open)

    def test_call_when_open(self):
        for _ in range(3):
            with self.assertRaises(ValueError):
                self.breaker.call(lambda: exec("raise ValueError('failure')"))

        with self.assertRaises(CircuitBreakerError):
            self.breaker.call(lambda: "should not run")

    def test_transition_to_half_open(self):
        for _ in range(3):
            with self.assertRaises(ValueError):
                self.breaker.call(lambda: exec("raise ValueError('failure')"))

        time.sleep(1.1)

        with self.assertRaises(ValueError):
             self.breaker.call(lambda: exec("raise ValueError('failure')"))
        self.assertEqual(self.breaker.state, CircuitState.OPEN)

        self.breaker.reset()
        for _ in range(3):
            with self.assertRaises(ValueError):
                self.breaker.call(lambda: exec("raise ValueError('failure')"))

        time.sleep(1.1)

        self.breaker.call(lambda: "success")
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)

    def test_half_open_call_succeeds(self):
        for _ in range(3):
            with self.assertRaises(ValueError):
                self.breaker.call(lambda: exec("raise ValueError('failure')"))
        time.sleep(1.1)

        result = self.breaker.call(lambda: "success")
        self.assertEqual(result, "success")
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
        self.assertEqual(self.breaker.failure_count, 0)

    def test_half_open_call_fails(self):
        for _ in range(3):
            with self.assertRaises(ValueError):
                self.breaker.call(lambda: exec("raise ValueError('failure')"))
        time.sleep(1.1)

        with self.assertRaises(ValueError):
            self.breaker.call(lambda: exec("raise ValueError('failure')"))

        self.assertEqual(self.breaker.state, CircuitState.OPEN)
        self.assertEqual(self.breaker.failure_count, 4)

    def test_reset(self):
        for _ in range(3):
            with self.assertRaises(ValueError):
                self.breaker.call(lambda: exec("raise ValueError('failure')"))

        self.breaker.reset()

        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
        self.assertEqual(self.breaker.failure_count, 0)

    def test_protected_decorator(self):

        @self.breaker.protected
        def my_func(should_fail=False):
            if should_fail:
                raise ValueError("failure")
            return "success"

        self.assertEqual(my_func(), "success")

        for _ in range(3):
            with self.assertRaises(ValueError):
                my_func(should_fail=True)

        with self.assertRaises(CircuitBreakerError):
            my_func()

    def test_thread_safety(self):

        @self.breaker.protected
        def flaky_func():
            import random
            if random.random() < 0.8:
                raise ValueError("random failure")
            return "success"

        def worker():
            for _ in range(10):
                try:
                    flaky_func()
                except (ValueError, CircuitBreakerError):
                    pass
                time.sleep(0.05)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertIn(self.breaker.state, [CircuitState.CLOSED, CircuitState.OPEN, CircuitState.HALF_OPEN])

class TestAlexaStateMachine(unittest.TestCase):

    def setUp(self):
        self.sm = AlexaStateMachine()

    def test_initial_state(self):
        self.assertEqual(self.sm.state, ConnectionState.DISCONNECTED)
        self.assertFalse(self.sm.is_connected)
        self.assertFalse(self.sm.can_execute_commands)
        self.assertFalse(self.sm.is_error_state)

    def test_valid_transition(self):
        self.sm.transition_to(ConnectionState.AUTHENTICATING)
        self.assertEqual(self.sm.state, ConnectionState.AUTHENTICATING)

    def test_invalid_transition(self):
        with self.assertRaises(StateTransitionError):
            self.sm.transition_to(ConnectionState.REFRESHING_TOKEN)

    def test_is_connected(self):
        self.sm.transition_to(ConnectionState.AUTHENTICATING)
        self.sm.transition_to(ConnectionState.AUTHENTICATED)
        self.assertTrue(self.sm.is_connected)

    def test_can_execute_commands(self):
        self.sm.transition_to(ConnectionState.AUTHENTICATING)
        self.sm.transition_to(ConnectionState.AUTHENTICATED)
        self.assertTrue(self.sm.can_execute_commands)

    def test_is_error_state(self):
        self.sm.transition_to(ConnectionState.AUTHENTICATING)
        self.sm.transition_to(ConnectionState.ERROR)
        self.assertTrue(self.sm.is_error_state)

    def test_register_and_execute_callback(self):
        callback = MagicMock()
        self.sm.register_callback(ConnectionState.AUTHENTICATING, callback)
        self.sm.transition_to(ConnectionState.AUTHENTICATING)
        callback.assert_called_once()

    def test_get_history(self):
        self.sm.transition_to(ConnectionState.AUTHENTICATING)
        self.sm.transition_to(ConnectionState.AUTHENTICATED)
        history = self.sm.get_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history, [ConnectionState.DISCONNECTED, ConnectionState.AUTHENTICATING, ConnectionState.AUTHENTICATED])

    def test_reset(self):
        self.sm.transition_to(ConnectionState.AUTHENTICATING)
        self.sm.transition_to(ConnectionState.AUTHENTICATED)
        self.sm.reset()
        self.assertEqual(self.sm.state, ConnectionState.DISCONNECTED)

    def test_set_initial_state(self):
        self.sm.set_initial_state(ConnectionState.AUTHENTICATED)
        self.assertEqual(self.sm.state, ConnectionState.AUTHENTICATED)

    def test_convenience_methods(self):
        self.sm.connect()
        self.assertEqual(self.sm.state, ConnectionState.AUTHENTICATING)
        self.sm.on_connected()
        self.assertEqual(self.sm.state, ConnectionState.AUTHENTICATED)
        self.sm.refresh_token()
        self.assertEqual(self.sm.state, ConnectionState.REFRESHING_TOKEN)
        self.sm.error()
        self.assertEqual(self.sm.state, ConnectionState.ERROR)
        self.sm.disconnect()
        self.assertEqual(self.sm.state, ConnectionState.DISCONNECTED)

    def test_thread_safety(self):

        def worker(target_state):
            try:
                self.sm.transition_to(target_state)
            except StateTransitionError:
                pass

        self.sm.set_initial_state(ConnectionState.AUTHENTICATED)

        threads = []
        for state in [ConnectionState.DISCONNECTED, ConnectionState.REFRESHING_TOKEN, ConnectionState.ERROR]:
            thread = threading.Thread(target=worker, args=(state,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertIn(self.sm.state, [ConnectionState.DISCONNECTED, ConnectionState.REFRESHING_TOKEN, ConnectionState.ERROR])

from core.config import Config, ConfigurationError

class TestConfig(unittest.TestCase):

    @patch('core.config.Path.exists', return_value=True)
    @patch('core.config.os.access', return_value=True)
    def setUp(self, mock_access, mock_exists):
        # Patch os.environ to isolate tests from the actual environment
        self.env_patcher = patch.dict(os.environ, {}, clear=True)
        self.mock_env = self.env_patcher.start()
        self.config = Config()

    def tearDown(self):
        self.env_patcher.stop()

    def test_default_values(self):
        self.assertEqual(self.config.language, "fr_FR")
        self.assertEqual(self.config.amazon_domain, "amazon.fr")
        self.assertEqual(self.config.speak_volume, 0)
        self.assertEqual(self.config.normal_volume, 10)

    def test_environment_variables_override_defaults(self):
        self.mock_env['LANGUAGE'] = 'en_US'
        self.mock_env['AMAZON'] = 'amazon.com'
        self.mock_env['SPEAKVOL'] = '50'

        # We need to re-initialize Config to make it read the new env vars
        config = Config()

        self.assertEqual(config.language, 'en_US')
        self.assertEqual(config.amazon_domain, 'amazon.com')
        self.assertEqual(config.speak_volume, 50)

    def test_get_int_env_valid(self):
        self.mock_env['TEST_VAR'] = '42'
        val = self.config._get_int_env('TEST_VAR', 0, min_val=10, max_val=50)
        self.assertEqual(val, 42)

    def test_get_int_env_invalid_int(self):
        self.mock_env['TEST_VAR'] = 'not-a-number'
        with self.assertRaises(ConfigurationError):
            self.config._get_int_env('TEST_VAR', 0)

    def test_get_int_env_out_of_bounds(self):
        self.mock_env['TEST_VAR'] = '100'
        with self.assertRaises(ConfigurationError):
            self.config._get_int_env('TEST_VAR', 0, max_val=50)

        self.mock_env['TEST_VAR'] = '5'
        with self.assertRaises(ConfigurationError):
            self.config._get_int_env('TEST_VAR', 0, min_val=10)

    def test_parse_int_list(self):
        result = self.config._parse_int_list("10 20 30", min_val=0, max_val=100)
        self.assertEqual(result, [10, 20, 30])

        # Test with invalid and out-of-bounds values
        result = self.config._parse_int_list("10 abc 110 20", min_val=0, max_val=100)
        self.assertEqual(result, [10, 20])

    @patch('core.config.Path.exists')
    def test_validate_critical_files_refresh_script_missing(self, mock_exists):
        # The first call to exists is for the token, the second is for the refresh script
        mock_exists.side_effect = [True, False]
        with self.assertRaises(ConfigurationError):
            Config()

    def test_get_temp_dir_non_win32(self):
        with patch('core.config.sys.platform', 'linux'):
            # Re-initialize config to test platform-specific logic
            config = Config()
            self.assertEqual(config.tmp_dir, Path('/tmp'))

    def test_get_api_base_url(self):
        self.mock_env['ALEXA'] = 'alexa.amazon.co.uk'
        config = Config()
        self.assertEqual(config.get_api_base_url(), 'https://alexa.amazon.co.uk')

from core.device_manager import DeviceManager

class TestDeviceManager(unittest.TestCase):

    def setUp(self):
        self.auth = MagicMock()
        # Provide a .session mock for any code that expects requests.Session on auth
        self.auth.session = MagicMock()
        # Provide a typed http_client for tests (migration shim)
        from core.base_manager import create_http_client_from_auth
        self.http_client = create_http_client_from_auth(self.auth)
        self.state_machine = MagicMock()
        self.cache_service = MagicMock()
        self.device_manager = DeviceManager(self.auth, self.state_machine, cache_service=self.cache_service, http_client=self.http_client)
        self.mock_devices = [
            {"accountName": "Echo Dot", "serialNumber": "123", "online": True},
            {"accountName": "Echo Show", "serialNumber": "456", "online": False},
        ]

    def test_initialization(self):
        self.assertIsNotNone(self.device_manager)
        with self.assertRaises(ValueError):
            DeviceManager(None, self.state_machine)
        with self.assertRaises(ValueError):
            DeviceManager(self.auth, None)

    def test_get_devices_from_memory_cache(self):
        self.device_manager._devices_cache = self.mock_devices
        self.device_manager._cache_timestamp = time.time()

        devices = self.device_manager.get_devices()

        self.assertEqual(devices, self.mock_devices)
        self.cache_service.get.assert_not_called()

    def test_get_devices_from_disk_cache(self):
        self.cache_service.get.return_value = {"devices": self.mock_devices}

        devices = self.device_manager.get_devices()

        self.assertEqual(devices, self.mock_devices)
        self.cache_service.get.assert_called_once_with("devices", ignore_ttl=True)

    def test_get_devices_from_api(self):
        self.cache_service.get.return_value = None
        self.http_client.get.return_value.status_code = 200
        self.http_client.get.return_value.json.return_value = {"devices": self.mock_devices}

        devices = self.device_manager.get_devices()

        self.assertEqual(devices, self.mock_devices)
        self.cache_service.set.assert_called_once()

    def test_get_devices_api_fails(self):
        self.cache_service.get.return_value = None
        self.http_client.get.return_value = None

        devices = self.device_manager.get_devices()

        self.assertIsNone(devices)

    def test_find_device_by_name(self):
        self.device_manager.get_devices = MagicMock(return_value=self.mock_devices)

        device = self.device_manager.find_device_by_name("Echo Dot")
        self.assertEqual(device, self.mock_devices[0])

        # Test partial match
        device = self.device_manager.find_device_by_name("Dot")
        self.assertEqual(device, self.mock_devices[0])

        # Test not found
        device = self.device_manager.find_device_by_name("Nonexistent")
        self.assertIsNone(device)

    def test_find_device_by_serial(self):
        self.device_manager.get_devices = MagicMock(return_value=self.mock_devices)

        device = self.device_manager.find_device_by_serial("123")
        self.assertEqual(device, self.mock_devices[0])

        device = self.device_manager.find_device_by_serial("999")
        self.assertIsNone(device)

    def test_get_online_devices(self):
        self.device_manager.get_devices = MagicMock(return_value=self.mock_devices)
        online_devices = self.device_manager.get_online_devices()
        self.assertEqual(len(online_devices), 1)
        self.assertEqual(online_devices[0], self.mock_devices[0])

    def test_invalidate_cache(self):
        self.device_manager._devices_cache = self.mock_devices
        self.device_manager.invalidate_cache()
        self.assertIsNone(self.device_manager._devices_cache)
        self.cache_service.invalidate.assert_called_once_with("devices")

import requests
from core.alarms.alarm_manager import AlarmManager

class TestAlarmManager(unittest.TestCase):

    def setUp(self):
        self.auth = MagicMock()
        # Provide legacy session on auth to keep tests compatible with migration
        self.auth.session = MagicMock()
        # Provide a typed http_client for tests (migration shim)
        from core.base_manager import create_http_client_from_auth
        self.http_client = create_http_client_from_auth(self.auth)
        self.config = MagicMock()
        self.state_machine = MagicMock()
        self.cache_service = MagicMock()
        self.alarm_manager = AlarmManager(self.auth, self.config, self.state_machine, self.cache_service)
        self.mock_alarms = [
            {"id": "1", "deviceSerialNumber": "123", "type": "Alarm"},
            {"id": "2", "deviceSerialNumber": "456", "type": "Alarm"},
        ]

    def test_initialization(self):
        self.assertIsNotNone(self.alarm_manager)

    def test_create_alarm_success(self):
        self.state_machine.can_execute_commands = True
        self.http_client.post.return_value.status_code = 200
        self.http_client.post.return_value.json.return_value = {"id": "new_alarm"}

        result = self.alarm_manager.create_alarm("123", "A_TYPE", "2023-10-27T10:00:00", label="Test", sound="sound1")

        self.assertEqual(result, {"id": "new_alarm"})
        self.http_client.post.assert_called_once()
        self.assertIsNone(self.alarm_manager._alarms_cache)

    def test_create_alarm_fails_connection(self):
        self.state_machine.can_execute_commands = False
        result = self.alarm_manager.create_alarm("123", "A_TYPE", "2023-10-27T10:00:00")
        self.assertIsNone(result)

    def test_create_alarm_api_exception(self):
        self.state_machine.can_execute_commands = True
        self.http_client.post.side_effect = requests.exceptions.RequestException
        result = self.alarm_manager.create_alarm("123", "A_TYPE", "2023-10-27T10:00:00")
        self.assertIsNone(result)

    def test_list_alarms_from_memory_cache(self):
        self.state_machine.can_execute_commands = True
        self.alarm_manager._alarms_cache = self.mock_alarms
        self.alarm_manager._cache_timestamp = time.time()

        alarms = self.alarm_manager.list_alarms()

        self.assertEqual(alarms, self.mock_alarms)
        self.cache_service.get.assert_not_called()

    def test_list_alarms_expired_cache(self):
        self.state_machine.can_execute_commands = True
        self.alarm_manager._alarms_cache = self.mock_alarms
        self.alarm_manager._cache_timestamp = time.time() - 100 # Expired
        self.cache_service.get.return_value = {"alarms": self.mock_alarms}

        self.alarm_manager.list_alarms()
        self.cache_service.get.assert_called_with("alarms")

    def test_list_alarms_from_disk_cache(self):
        self.state_machine.can_execute_commands = True
        self.cache_service.get.return_value = {"alarms": self.mock_alarms}

        alarms = self.alarm_manager.list_alarms()

        self.assertEqual(alarms, self.mock_alarms)
        self.cache_service.get.assert_called_once_with("alarms")

    def test_list_alarms_with_device_serial(self):
        self.state_machine.can_execute_commands = True
        self.alarm_manager._alarms_cache = self.mock_alarms
        self.alarm_manager._cache_timestamp = time.time()

        alarms = self.alarm_manager.list_alarms(device_serial="123")
        self.assertEqual(len(alarms), 1)
        self.assertEqual(alarms[0]['id'], "1")

    def test_refresh_alarms_cache_empty_response(self):
        self.http_client.get.return_value.content = b' '
        alarms = self.alarm_manager._refresh_alarms_cache()
        self.assertEqual(alarms, [])

    def test_refresh_alarms_cache_json_error(self):
        self.http_client.get.return_value.json.side_effect = ValueError
        alarms = self.alarm_manager._refresh_alarms_cache()
        self.assertEqual(alarms, [])

    def test_refresh_alarms_cache_api_error(self):
        self.http_client.get.side_effect = requests.exceptions.RequestException
        alarms = self.alarm_manager._refresh_alarms_cache()
        self.assertEqual(alarms, [])

    def test_delete_alarm_success(self):
        self.state_machine.can_execute_commands = True
        self.http_client.delete.return_value.status_code = 200

        result = self.alarm_manager.delete_alarm("123", "A_TYPE", "alarm_id")

        self.assertTrue(result)
        self.http_client.delete.assert_called_once()
        self.assertIsNone(self.alarm_manager._alarms_cache)

    def test_delete_alarm_fails_connection(self):
        self.state_machine.can_execute_commands = False
        result = self.alarm_manager.delete_alarm("123", "A_TYPE", "alarm_id")
        self.assertFalse(result)

    def test_delete_alarm_api_exception(self):
        self.state_machine.can_execute_commands = True
        self.http_client.delete.side_effect = requests.exceptions.RequestException
        result = self.alarm_manager.delete_alarm("123", "A_TYPE", "alarm_id")
        self.assertFalse(result)

    def test_update_alarm_success(self):
        self.state_machine.can_execute_commands = True
        self.http_client.put.return_value.status_code = 200

        result = self.alarm_manager.update_alarm("123", "A_TYPE", "alarm_id", time="11:00", sound="sound2")

        self.assertTrue(result)
        self.http_client.put.assert_called_once()
        self.assertIsNone(self.alarm_manager._alarms_cache)

    def test_update_alarm_fails_connection(self):
        self.state_machine.can_execute_commands = False
        result = self.alarm_manager.update_alarm("123", "A_TYPE", "alarm_id", time="11:00")
        self.assertFalse(result)

    def test_update_alarm_no_updates(self):
        self.state_machine.can_execute_commands = True
        result = self.alarm_manager.update_alarm("123", "A_TYPE", "alarm_id")
        self.assertFalse(result)

    def test_update_alarm_api_exception(self):
        self.state_machine.can_execute_commands = True
        self.http_client.put.side_effect = requests.exceptions.RequestException
        result = self.alarm_manager.update_alarm("123", "A_TYPE", "alarm_id", time="11:00")
        self.assertFalse(result)

    def test_set_alarm_enabled(self):
        self.state_machine.can_execute_commands = True
        self.http_client.put.return_value.status_code = 200

        result = self.alarm_manager.set_alarm_enabled("123", "A_TYPE", "alarm_id", True)

        self.assertTrue(result)
        self.http_client.put.assert_called_once()
        self.assertIsNone(self.alarm_manager._alarms_cache)

    def test_set_alarm_enabled_fails_connection(self):
        self.state_machine.can_execute_commands = False
        result = self.alarm_manager.set_alarm_enabled("123", "A_TYPE", "alarm_id", True)
        self.assertFalse(result)

    def test_set_alarm_enabled_api_exception(self):
        self.state_machine.can_execute_commands = True
        self.http_client.put.side_effect = requests.exceptions.RequestException
        result = self.alarm_manager.set_alarm_enabled("123", "A_TYPE", "alarm_id", True)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
