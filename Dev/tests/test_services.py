
import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
import gzip
from pathlib import Path
import time

from services.cache_service import CacheService

class TestCacheService(unittest.TestCase):

    def setUp(self):
        self.cache_dir = Path("test_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_service = CacheService(cache_dir=self.cache_dir)

    def tearDown(self):
        # Clean up the test cache directory
        for item in self.cache_dir.iterdir():
            item.unlink()
        self.cache_dir.rmdir()

    def test_set_and_get_compressed(self):
        test_data = {"key": "value"}
        self.cache_service.set("test_key", test_data, ttl_seconds=60)

        # Check that the compressed file was created
        compressed_file = self.cache_dir / "test_key.json.gz"
        self.assertTrue(compressed_file.exists())

        # Get the data back and verify it
        retrieved_data = self.cache_service.get("test_key")
        self.assertEqual(retrieved_data, test_data)

    def test_set_and_get_uncompressed(self):
        cache_service = CacheService(cache_dir=self.cache_dir, use_compression=False)
        test_data = {"key": "value"}
        cache_service.set("test_key", test_data, ttl_seconds=60)

        # Check that the uncompressed file was created
        uncompressed_file = self.cache_dir / "test_key.json"
        self.assertTrue(uncompressed_file.exists())

        retrieved_data = cache_service.get("test_key")
        self.assertEqual(retrieved_data, test_data)

    def test_cache_expiration(self):
        test_data = {"key": "value"}
        self.cache_service.set("test_key", test_data, ttl_seconds=1)

        # Should be able to get it immediately
        self.assertIsNotNone(self.cache_service.get("test_key"))

        # Wait for it to expire
        time.sleep(1.1)
        self.assertIsNone(self.cache_service.get("test_key"))

        # Should be able to get it with ignore_ttl
        self.assertIsNotNone(self.cache_service.get("test_key", ignore_ttl=True))

    def test_invalidate(self):
        test_data = {"key": "value"}
        self.cache_service.set("test_key", test_data, ttl_seconds=60)
        self.assertTrue(self.cache_service.invalidate("test_key"))
        self.assertIsNone(self.cache_service.get("test_key"))

    def test_clear_all_except(self):
        self.cache_service.set("key1", {"data": 1}, 60)
        self.cache_service.set("key2", {"data": 2}, 60)
        self.cache_service.set("key3", {"data": 3}, 60)

        self.cache_service.clear_all_except(["key2"])

        self.assertIsNone(self.cache_service.get("key1"))
        self.assertIsNotNone(self.cache_service.get("key2"))
        self.assertIsNone(self.cache_service.get("key3"))

    def test_clean_expired(self):
        self.cache_service.set("key1", {"data": 1}, 1)
        self.cache_service.set("key2", {"data": 2}, 60)

        time.sleep(1.1)

        self.cache_service.clean_expired()

        self.assertIsNone(self.cache_service.get("key1"))
        self.assertIsNotNone(self.cache_service.get("key2"))

    def test_get_stats(self):
        self.cache_service.set("key1", {"data": 1}, 60)
        self.cache_service.get("key1") # Hit
        self.cache_service.get("key2") # Miss

        stats = self.cache_service.get_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['writes'], 1)
        self.assertAlmostEqual(stats['hit_rate'], 0.5)

if __name__ == '__main__':
    unittest.main()
