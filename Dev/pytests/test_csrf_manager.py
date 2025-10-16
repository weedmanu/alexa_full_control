"""
TDD Tests for CSRFManager - Write tests BEFORE implementation.

Test Coverage:
- Token validation (format, length, characters)
- Token refresh logic (TTL expiration)
- Thread safety
- Error handling
- Safe retrieval (no exceptions)
"""

import threading
import time
import unittest
from unittest.mock import Mock, patch

from core.security.csrf_manager import CSRFManager, SecurityError


class TestCSRFManagerValidation(unittest.TestCase):
    """Test CSRF token validation logic."""

    def setUp(self):
        """Setup mock auth for each test."""
        self.mock_auth = Mock()
        self.mock_auth.csrf = "amzn.valid_token_12345"
        self.mgr = CSRFManager(self.mock_auth)

    def test_valid_amazon_format_token(self):
        """Token starting with 'amzn.' should be valid."""
        token = "amzn.abc123def456"
        self.assertTrue(self.mgr._is_valid_csrf(token))

    def test_valid_long_alphanumeric_token(self):
        """Long alphanumeric token (30+ chars) should be valid."""
        token = "a" * 30  # 30 'a's
        self.assertTrue(self.mgr._is_valid_csrf(token))

    def test_invalid_empty_token(self):
        """Empty token should be invalid."""
        self.assertFalse(self.mgr._is_valid_csrf(""))

    def test_invalid_too_short_token(self):
        """Token < 10 chars should be invalid."""
        token = "abc123"  # 6 chars
        self.assertFalse(self.mgr._is_valid_csrf(token))

    def test_invalid_short_non_amazon_token(self):
        """Short alphanumeric (< 20 chars) not starting with 'amzn.' is invalid."""
        token = "abc123def456"  # 12 chars, not amazon format
        self.assertFalse(self.mgr._is_valid_csrf(token))

    def test_invalid_special_chars_token(self):
        """Token with invalid special chars should be invalid."""
        token = "abc@def!ghi"  # @ and ! are not allowed
        self.assertFalse(self.mgr._is_valid_csrf(token))

    def test_valid_token_with_hyphens(self):
        """Token with hyphens should be valid if long enough."""
        token = "abc-def-ghi-123-456-7890"  # 25 chars with hyphens
        self.assertTrue(self.mgr._is_valid_csrf(token))

    def test_valid_token_with_underscores(self):
        """Token with underscores should be valid if long enough."""
        token = "abc_def_ghi_123_456_7890"  # 25 chars with underscores
        self.assertTrue(self.mgr._is_valid_csrf(token))


class TestCSRFManagerRefresh(unittest.TestCase):
    """Test CSRF token refresh logic."""

    def setUp(self):
        """Setup mock auth for each test."""
        self.mock_auth = Mock()
        self.mock_auth.csrf = "amzn.valid_token_12345"
        self.mgr = CSRFManager(self.mock_auth)

    def test_refresh_valid_token_from_auth(self):
        """Valid token from auth should be cached."""
        token = self.mgr.get_csrf(validate=False)
        self.assertEqual(token, "amzn.valid_token_12345")
        self.assertIsNotNone(self.mgr._csrf_timestamp)

    def test_cache_returns_same_token_within_ttl(self):
        """Cached token should be returned without refresh within TTL."""
        token1 = self.mgr.get_csrf(validate=False)

        # Change auth token
        self.mock_auth.csrf = "amzn.different_token"

        # Should still return cached token (not refreshed)
        token2 = self.mgr.get_csrf(validate=False)
        self.assertEqual(token1, token2)

    def test_refresh_after_ttl_expiration(self):
        """Token should be refreshed after TTL (30 min) expiration."""
        token1 = self.mgr.get_csrf(validate=False)
        original_timestamp = self.mgr._csrf_timestamp

        # Simulate TTL expiration by mocking time
        self.mgr._csrf_timestamp = time.time() - 1801  # Older than 30 min

        # Change auth token
        self.mock_auth.csrf = "amzn.refreshed_token"

        # Should refresh and get new token
        token2 = self.mgr.get_csrf(validate=False)
        self.assertEqual(token2, "amzn.refreshed_token")
        self.assertGreater(self.mgr._csrf_timestamp, original_timestamp)

    def test_invalidate_clears_cache(self):
        """Invalidate should clear cached token."""
        self.mgr.get_csrf(validate=False)
        self.assertIsNotNone(self.mgr._csrf_cache)

        self.mgr.invalidate()
        self.assertIsNone(self.mgr._csrf_cache)
        self.assertEqual(self.mgr._csrf_timestamp, 0.0)

    def test_invalid_token_from_auth_not_cached(self):
        """Invalid token from auth should not be cached."""
        self.mock_auth.csrf = "invalid"  # Too short

        with self.assertRaises(SecurityError):
            self.mgr.get_csrf(validate=True)

        self.assertIsNone(self.mgr._csrf_cache)


class TestCSRFManagerSafety(unittest.TestCase):
    """Test thread safety and error handling."""

    def setUp(self):
        """Setup mock auth for each test."""
        self.mock_auth = Mock()
        self.mock_auth.csrf = "amzn.valid_token_12345"
        self.mgr = CSRFManager(self.mock_auth)

    def test_get_csrf_validation_enabled(self):
        """get_csrf with validate=True should raise on invalid token."""
        self.mock_auth.csrf = "invalid"  # Too short

        with self.assertRaises(SecurityError):
            self.mgr.get_csrf(validate=True)

    def test_get_csrf_validation_disabled(self):
        """get_csrf with validate=False should return token even if invalid."""
        self.mock_auth.csrf = "invalid"  # Too short
        token = self.mgr.get_csrf(validate=False)
        self.assertEqual(token, "invalid")

    def test_get_csrf_safe_returns_default_on_error(self):
        """get_csrf_safe should return default instead of raising."""
        self.mock_auth.csrf = "invalid"

        token = self.mgr.get_csrf_safe(default="DEFAULT_TOKEN")
        self.assertEqual(token, "DEFAULT_TOKEN")

    def test_thread_safety_concurrent_access(self):
        """Multiple threads should safely access token without race conditions."""
        tokens = []
        errors = []

        def thread_get_token():
            try:
                token = self.mgr.get_csrf(validate=False)
                tokens.append(token)
            except Exception as e:
                errors.append(e)

        # Create 10 concurrent threads
        threads = [threading.Thread(target=thread_get_token) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should succeed
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(tokens), 10)

        # All should have same token (cached)
        self.assertTrue(all(t == tokens[0] for t in tokens))

    def test_thread_safety_concurrent_invalidate(self):
        """Thread safety: concurrent invalidate and get_csrf."""
        self.mgr.get_csrf(validate=False)

        errors = []

        def thread_invalidate():
            try:
                self.mgr.invalidate()
            except Exception as e:
                errors.append(e)

        def thread_get():
            try:
                self.mgr.get_csrf(validate=False)
            except Exception as e:
                errors.append(e)

        # Mix invalidate and get operations
        threads = (
            [threading.Thread(target=thread_get) for _ in range(5)]
            + [threading.Thread(target=thread_invalidate) for _ in range(3)]
            + [threading.Thread(target=thread_get) for _ in range(5)]
        )

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)


class TestCSRFManagerStats(unittest.TestCase):
    """Test stats and diagnostic methods."""

    def setUp(self):
        """Setup mock auth for each test."""
        self.mock_auth = Mock()
        self.mock_auth.csrf = "amzn.valid_token_12345"
        self.mgr = CSRFManager(self.mock_auth)

    def test_stats_empty_cache(self):
        """Stats should show empty cache if not initialized."""
        stats = self.mgr.get_stats()

        self.assertFalse(stats["cached"])
        self.assertIsNone(stats["age_seconds"])
        self.assertEqual(stats["token_length"], 0)

    def test_stats_cached_token(self):
        """Stats should show cached token info."""
        self.mgr.get_csrf(validate=False)
        stats = self.mgr.get_stats()

        self.assertTrue(stats["cached"])
        self.assertTrue(stats["valid"])
        self.assertGreaterEqual(stats["token_length"], 10)
        self.assertLess(stats["age_seconds"], 1)  # Very fresh

    def test_stats_aged_token(self):
        """Stats should show token age."""
        self.mgr.get_csrf(validate=False)
        self.mgr._csrf_timestamp = time.time() - 60  # 60 seconds old

        stats = self.mgr.get_stats()

        self.assertTrue(stats["cached"])
        self.assertAlmostEqual(stats["age_seconds"], 60, delta=1)
        self.assertFalse(stats["needs_refresh"])

    def test_stats_needs_refresh(self):
        """Stats should indicate refresh needed after TTL."""
        self.mgr.get_csrf(validate=False)
        self.mgr._csrf_timestamp = time.time() - 1801  # > 30 min

        stats = self.mgr.get_stats()

        self.assertTrue(stats["needs_refresh"])


if __name__ == "__main__":
    unittest.main()
