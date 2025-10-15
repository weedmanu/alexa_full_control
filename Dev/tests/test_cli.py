
import unittest
from unittest.mock import MagicMock, patch, call
import sys
from pathlib import Path
import importlib.util

# This import should work because pytest adds the root to the path
from cli.commands import AuthCommand, MusicCommand

class TestAlexaMain(unittest.TestCase):

    def setUp(self):
        # Dynamically import the 'alexa' script as a module
        alexa_path = Path(__file__).parent.parent.parent.absolute() / 'alexa'
        if not alexa_path.exists():
            raise FileNotFoundError(f"Could not find 'alexa' script at {alexa_path}")
        from importlib.machinery import SourceFileLoader
        self.alexa = SourceFileLoader("alexa", str(alexa_path)).load_module()
        # Add to sys.modules so patch can find it by string 'alexa.create_parser'
        sys.modules['alexa'] = self.alexa

    def tearDown(self):
        # Clean up the module from sys.modules to isolate tests
        if 'alexa' in sys.modules:
            del sys.modules['alexa']

    def test_main_flow_success(self):
        with patch('alexa.create_parser') as mock_create_parser, \
             patch('alexa.register_all_commands'), \
             patch('alexa.create_context') as mock_create_context, \
             patch('alexa.setup_logging') as mock_setup_logging, \
             patch('alexa_auth.alexa_auth.AlexaAuth.load_cookies', return_value=False):

            # Mock the parser and its arguments
            mock_parser = MagicMock()
            mock_args = MagicMock()
            mock_args.category, mock_args.action = 'device', 'list'
            mock_args.verbose, mock_args.debug, mock_args.config = False, False, None
            mock_parser.parse_args.return_value = mock_args
            mock_create_parser.return_value = mock_parser

            # Mock the command class and its execution
            mock_command_class = MagicMock()
            mock_command_instance = MagicMock()
            mock_command_instance.execute.return_value = True
            mock_command_class.return_value = mock_command_instance
            mock_parser.get_command_class.return_value = mock_command_class

            # Mock the context
            mock_context = MagicMock()
            mock_create_context.return_value = mock_context

            with patch.object(sys, 'argv', ['alexa', 'device', 'list']):
                result = self.alexa.main()

            self.assertEqual(result, 0)
            mock_setup_logging.assert_called_with(verbose=False, debug=False)
            mock_create_context.assert_called_with(config_file=None)
            mock_command_instance.execute.assert_called_with(mock_args)
            mock_context.cleanup.assert_called_once()

    def test_main_keyboard_interrupt(self):
        with patch('alexa.create_parser', side_effect=KeyboardInterrupt), \
             patch('alexa.logger') as mock_logger, \
             patch.object(sys, 'argv', ['alexa', 'device', 'list']):
            result = self.alexa.main()
        self.assertEqual(result, 130)
        mock_logger.warning.assert_called_with("Interruption par Ctrl+C")

    def test_main_unhandled_exception(self):
        with patch('alexa.create_parser', side_effect=Exception("Test error")), \
             patch('alexa.logger') as mock_logger, \
             patch.object(sys, 'argv', ['alexa', 'device', 'list']):
            result = self.alexa.main()
        self.assertEqual(result, 1)
        mock_logger.exception.assert_called_with("Erreur non gérée dans main()")

    def test_setup_logging(self):
        with patch('alexa.setup_loguru_logger') as mock_setup:
            self.alexa.setup_logging(verbose=True)
            mock_setup.assert_called_with(log_file=None, level='INFO', ensure_utf8=True)

            self.alexa.setup_logging(debug=True)
            mock_setup.assert_called_with(log_file=Path('logs') / 'alexa_cli.log', level='DEBUG', ensure_utf8=True)

    def test_register_all_commands(self):
        mock_parser = MagicMock()
        self.alexa.register_all_commands(mock_parser)

        # Check if a few key commands were registered
        self.assertIn(call('auth', AuthCommand), mock_parser.register_command.call_args_list)
        self.assertIn(call('music', MusicCommand), mock_parser.register_command.call_args_list)
        self.assertGreater(mock_parser.register_command.call_count, 5)

    def test_main_with_h_argument_after_action(self):
        with patch('sys.argv', ['alexa', 'device', 'list', '-h']), \
             patch('alexa.create_parser') as mock_create_parser, \
             patch('sys.exit') as mock_exit:

            mock_parser = MagicMock()
            mock_create_parser.return_value = mock_parser

            self.alexa.main()

            # Check that parse_args was called with the modified arguments for help
            mock_parser.parse_args.assert_called_with()
            self.assertEqual(sys.argv, ['alexa', 'device', '-h'])
            mock_exit.assert_called_with(0)

if __name__ == '__main__':
    unittest.main()
