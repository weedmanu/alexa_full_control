
import unittest
from unittest.mock import MagicMock, patch, call
import logging
from pathlib import Path
from datetime import datetime

from utils.logger import (
    setup_loguru_logger,
    get_log_level_from_verbosity,
    get_loguru_level_from_verbosity,
    InstallLogger,
    SharedIcons
)

class TestLogger(unittest.TestCase):

    @patch('utils.logger.logger')
    def test_setup_loguru_logger(self, mock_loguru_logger):
        setup_loguru_logger(level="DEBUG", enable_stderr=True)

        # Check that remove was called
        mock_loguru_logger.remove.assert_called_once()

        # Check that add was called for stdout and stderr
        self.assertIn(call(unittest.mock.ANY, format=unittest.mock.ANY, level="DEBUG", colorize=True, backtrace=True, diagnose=True), mock_loguru_logger.add.call_args_list)
        self.assertIn(call(unittest.mock.ANY, format=unittest.mock.ANY, level="ERROR", colorize=True, backtrace=True, diagnose=True), mock_loguru_logger.add.call_args_list)

    def test_get_log_level_from_verbosity(self):
        self.assertEqual(get_log_level_from_verbosity(0), logging.WARNING)
        self.assertEqual(get_log_level_from_verbosity(1), logging.INFO)
        self.assertEqual(get_log_level_from_verbosity(2), logging.DEBUG)

    def test_get_loguru_level_from_verbosity(self):
        self.assertEqual(get_loguru_level_from_verbosity(0), "WARNING")
        self.assertEqual(get_loguru_level_from_verbosity(1), "INFO")
        self.assertEqual(get_loguru_level_from_verbosity(2), "DEBUG")

    @patch('utils.logger.LOGURU_AVAILABLE', True)
    @patch('utils.logger.logger')
    def test_install_logger_with_loguru(self, mock_loguru_logger):
        logger = InstallLogger()
        logger.header("Test Header")
        mock_loguru_logger.opt.assert_called_with(depth=1)
        mock_loguru_logger.opt.return_value.log.assert_called_with("INSTALL", "🔧 Test Header")

    @patch('utils.logger.LOGURU_AVAILABLE', False)
    @patch('scripts.install.Logger')
    def test_install_logger_fallback(self, mock_fallback_logger):
        logger = InstallLogger()
        logger.header("Test Header")
        mock_fallback_logger.header.assert_called_with("Test Header", "🔧")

    def test_shared_icons_getters(self):
        all_icons = SharedIcons.get_all_icons()
        icon_map = SharedIcons.get_icon_map()
        self.assertIn("✅", all_icons)
        self.assertEqual(icon_map['success'], "✅")

    @patch('utils.logger.LOGURU_AVAILABLE', False)
    def test_setup_loguru_logger_not_available(self):
        # Should not raise an exception
        setup_loguru_logger()

    @patch('utils.logger.logger')
    @patch('utils.logger.Path.mkdir')
    def test_setup_loguru_logger_with_file(self, mock_mkdir, mock_loguru_logger):
        setup_loguru_logger(log_file=Path("test.log"))

        # Check that add was called for the file
        mock_loguru_logger.add.assert_any_call(
            Path("test.log"),
            format=unittest.mock.ANY,
            level="DEBUG",
            rotation="10 MB",
            retention="1 week",
            compression="gz",
            backtrace=True,
            diagnose=True,
            encoding="utf-8",
        )

    @patch('utils.logger.sys.stdout.reconfigure', side_effect=Exception)
    @patch('io.TextIOWrapper')
    def test_ensure_utf8_stdout_exception(self, mock_text_io_wrapper, mock_reconfigure):
        from utils.logger import _ensure_utf8_stdout
        # Should not raise an exception
        _ensure_utf8_stdout()

    def test_install_logger_fallback_methods(self):
        with patch('utils.logger.LOGURU_AVAILABLE', False), \
             patch('scripts.install.Logger') as mock_fallback_logger:

            logger = InstallLogger()

            logger.step("Test Step")
            mock_fallback_logger.step.assert_called_with("Test Step", "⚡")

            logger.progress("Test Progress")
            mock_fallback_logger.progress.assert_called_with("Test Progress")

            logger.success("Test Success")
            mock_fallback_logger.success.assert_called_with("Test Success", "✅")

            logger.error("Test Error")
            mock_fallback_logger.error.assert_called_with("Test Error", "❌")

            logger.warning("Test Warning")
            mock_fallback_logger.warning.assert_called_with("Test Warning", "⚠️")

            logger.info("Test Info")
            mock_fallback_logger.info.assert_called_with("Test Info", "ℹ️")

    @patch('utils.logger.LOGURU_AVAILABLE', False)
    def test_install_logger_fallback_debug(self):
        with patch('builtins.print') as mock_print:
            logger = InstallLogger()
            logger.debug("Test Debug")
            mock_print.assert_called_with("🐞 DEBUG: Test Debug")

    def test_get_format_record(self):
        from utils.logger import _get_format_record
        format_record = _get_format_record()

        mock_record = {
            "level": MagicMock(name="INFO", no=20),
            "extra": {},
            "message": "Test message",
            "name": "test_module",
            "function": "test_func",
            "line": 123,
            "time": datetime.now(),
            "exception": None
        }

        # Test non-error, non-debug level (no location)
        result = format_record(mock_record)
        self.assertNotIn("test_module", result)

        # Test error level (with location)
        mock_record['level'].name = "ERROR"
        # We need to re-call the format_record function to get the updated format string
        result = format_record(mock_record)
        self.assertIn("<cyan>{name}</cyan>", result)

    @patch('utils.logger.logging.getLogger')
    def test_deprecated_setup_logger(self, mock_get_logger):
        from utils.logger import setup_logger
        setup_logger("test_logger")
        mock_get_logger.assert_called_with("test_logger")

    @patch('utils.logger.get_install_logger')
    def test_log_system_info(self, mock_get_install_logger):
        from utils.logger import log_system_info
        mock_logger = MagicMock()
        mock_get_install_logger.return_value = mock_logger
        log_system_info(mock_logger)
        self.assertGreater(mock_logger.debug.call_count, 2)

if __name__ == '__main__':
    unittest.main()
