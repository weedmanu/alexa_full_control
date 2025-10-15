"""
Service de cache persistant multi-niveaux.

Gère le cache disque avec TTL, thread-safe et statistiques.
Optimisé avec compression gzip pour réduire la taille des fichiers.
"""

import gzip
import json
import os
import time
import tempfile
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

from loguru import logger

from utils.logger import SharedIcons

# Optional inter-process locking: use portalocker when available
try:
    import portalocker as _portalocker  # type: ignore
except Exception:
    _portalocker = None


class CacheService:
    """
    Service de gestion du cache persistant.

    Fonctionnalités :
    - Cache fichiers JSON avec TTL configurable
    - Thread-safe (RLock)
    - Auto-expiration basée sur timestamps
    - Invalidation manuelle
    - Statistiques hits/misses

    Example:
        >>> cache = CacheService()
        >>> cache.set("devices", {"devices": [...]}, ttl_seconds=3600)
        >>> data = cache.get("devices")  # Récupère si non expiré
        >>> cache.invalidate("devices")  # Force suppression
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        use_compression: bool = True,
        save_json_copy: bool = True,
    ):
        """
        Initialise le service de cache.

        Args:
            cache_dir: Répertoire de cache (défaut: data/cache)
            use_compression: Activer la compression gzip (défaut: True, réduit ~70% taille)
            save_json_copy: Sauvegarder aussi une copie JSON lisible (défaut: True)
        """
        if cache_dir is None:
            # Déterminer le chemin relatif au script principal
            script_dir = Path(__file__).parent.parent.absolute()
            cache_dir = script_dir / "data" / "cache"

        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_compression = use_compression
        self.save_json_copy = save_json_copy

        self.metadata_file = self.cache_dir / ".metadata.json"
        self._lock = RLock()
        # Whether inter-process file locking is available
        self._portalocker_enabled = _portalocker is not None
        if not self._portalocker_enabled:
            logger.debug(
                "portalocker not available - inter-process cache locking is disabled"
            )
        self._stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "invalidations": 0,
            "compression_ratio": 0.0,
        }
        self.metadata: Dict[str, Dict[str, Any]] = {}

        self._load_metadata()

        # S'assurer que le fichier metadata existe
        if not self.metadata_file.exists():
            self._save_metadata()

        compression_status = "avec compression" if use_compression else "sans compression"
        json_copy_status = "avec copie JSON" if save_json_copy else "sans copie JSON"
        logger.debug(
            f"CacheService initialisé: {self.cache_dir} ({compression_status}, {json_copy_status})"
        )

    def get(self, key: str, ignore_ttl: bool = False) -> Optional[Dict[str, Any]]:
        """
        Récupère une donnée depuis le cache si valide.

        Args:
            key: Clé du cache (nom du fichier sans extension)
            ignore_ttl: Si True, ignore l'expiration TTL et retourne le cache même expiré

        Returns:
            Données du cache ou None si inexistant

        Example:
            >>> devices = cache.get("devices")
            >>> if devices:
            ...     print(f"Trouvé {len(devices['devices'])} appareils")
            >>> # Récupérer même si expiré (fallback)
            >>> devices = cache.get("devices", ignore_ttl=True)
        """
        # Use in-process lock plus optional inter-process file lock per-key
        with self._lock:
            with self._file_lock(key):
                # Vérifier expiration (sauf si ignore_ttl=True)
                if not ignore_ttl and self._is_expired(key):
                    logger.debug(f"📦 Cache MISS (expired): {key}")
                    self._stats["misses"] += 1
                    return None

                # Chercher fichier compressé ou non compressé
                cache_file_gz = self.cache_dir / f"{key}.json.gz"
                cache_file = self.cache_dir / f"{key}.json"

                # Priorité au fichier compressé
                if cache_file_gz.exists():
                    try:
                        with gzip.open(cache_file_gz, "rt", encoding="utf-8") as f:
                            data = json.load(f)
                        ttl_info = " (ignoring TTL)" if ignore_ttl else ""
                        logger.debug(f"✅ Cache HIT (compressed): {key}{ttl_info}")
                        self._stats["hits"] += 1
                        return data
                    except (json.JSONDecodeError, OSError) as e:
                        logger.error(f"Erreur lecture cache compressé {key}: {e}")
                        self._stats["misses"] += 1
                        return None
                elif cache_file.exists():
                    try:
                        data = json.loads(cache_file.read_text(encoding="utf-8"))
                        ttl_info = " (ignoring TTL)" if ignore_ttl else ""
                        logger.debug(f"✅ Cache HIT: {key}{ttl_info}")
                        self._stats["hits"] += 1
                        return data
                    except (json.JSONDecodeError, OSError) as e:
                        logger.error(f"Erreur lecture cache {key}: {e}")
                        self._stats["misses"] += 1
                        return None
                else:
                    logger.debug(f"📦 Cache MISS (not found): {key}")
                    self._stats["misses"] += 1
                    return None

    def set(self, key: str, data: Dict[str, Any], ttl_seconds: int):
        """
        Sauvegarde une donnée dans le cache avec TTL et compression optionnelle.

        Args:
            key: Clé du cache (nom du fichier sans extension)
            data: Données à sauvegarder (doit être JSON-serializable)
            ttl_seconds: Durée de vie en secondes

        Example:
            >>> cache.set("devices", {"devices": devices_list}, ttl_seconds=3600)
            >>> # Cache valide pendant 1 heure, compressé automatiquement
        """
        with self._lock:
            # Acquire per-key file lock to avoid concurrent writers/readers
            with self._file_lock(key):
                try:
                    # Sérialiser JSON (compact, sans indentation pour meilleure compression)
                    json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
                    original_size = len(json_str.encode("utf-8"))

                    if self.use_compression:
                        # Sauvegarder version compressée de façon atomique
                        cache_file = self.cache_dir / f"{key}.json.gz"
                        tmp_fd, tmp_path = tempfile.mkstemp(dir=self.cache_dir, prefix=f"{key}.", suffix='.json.gz.tmp')
                        try:
                            # write compressed bytes to temp file
                            compressed_bytes = gzip.compress(json_str.encode('utf-8'))
                            with os.fdopen(tmp_fd, 'wb') as tf:
                                tf.write(compressed_bytes)
                                tf.flush()
                                os.fsync(tf.fileno())
                            # atomic replace
                            os.replace(tmp_path, str(cache_file))
                            compressed_size = cache_file.stat().st_size
                        finally:
                            # ensure tmp file removed if something went wrong
                            if os.path.exists(tmp_path):
                                try:
                                    os.remove(tmp_path)
                                except OSError:
                                    pass
                        compression_ratio = (
                            (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
                        )

                        # Supprimer ancienne version non compressée si existe
                        old_file = self.cache_dir / f"{key}.json"
                        if old_file.exists():
                            old_file.unlink()

                        log_msg_prefix = f"{SharedIcons.SAVE} Cache saved (compressed): {key}"
                        log_msg_details_part1 = f" (TTL: {ttl_seconds}s, {original_size}→{compressed_size} bytes,"
                        log_msg_details_part2 = f" -{compression_ratio:.1f}%)"
                        log_msg = log_msg_prefix + log_msg_details_part1 + log_msg_details_part2
                    else:
                        # Sauvegarder version non compressée de façon atomique (indentée pour lisibilité)
                        cache_file = self.cache_dir / f"{key}.json"
                        tmp_fd, tmp_path = tempfile.mkstemp(dir=self.cache_dir, prefix=f"{key}.", suffix='.json.tmp')
                        try:
                            with os.fdopen(tmp_fd, 'w', encoding='utf-8') as tf:
                                tf.write(json.dumps(data, indent=2, ensure_ascii=False))
                                tf.flush()
                                os.fsync(tf.fileno())
                            os.replace(tmp_path, str(cache_file))
                            compressed_size = cache_file.stat().st_size
                        finally:
                            if os.path.exists(tmp_path):
                                try:
                                    os.remove(tmp_path)
                                except OSError:
                                    pass
                        compression_ratio = 0

                        # Supprimer ancienne version compressée si existe
                        old_file = self.cache_dir / f"{key}.json.gz"
                        if old_file.exists():
                            old_file.unlink()

                        log_msg = (
                            f"{SharedIcons.SAVE} Cache saved: {key}"
                            f" (TTL: {ttl_seconds}s, Size: {compressed_size} bytes)"
                        )

                    # Sauvegarder aussi une copie JSON lisible si demandé
                    if self.save_json_copy and self.use_compression:
                        # Write JSON copy atomically as well
                        json_file = self.cache_dir / f"{key}.json"
                        tmp_fd, tmp_path = tempfile.mkstemp(
                            dir=self.cache_dir, prefix=f"{key}._copy.", suffix='.json.tmp'
                        )
                        try:
                            with os.fdopen(tmp_fd, 'w', encoding='utf-8') as tf:
                                tf.write(json.dumps(data, indent=2, ensure_ascii=False))
                                tf.flush()
                                os.fsync(tf.fileno())
                            os.replace(tmp_path, str(json_file))
                            logger.debug(f"{SharedIcons.FILE} Copie JSON sauvegardée: {key}.json")
                        except OSError as e:
                            logger.warning(f"Impossible de sauvegarder copie JSON {key}: {e}")
                        finally:
                            if os.path.exists(tmp_path):
                                try:
                                    os.remove(tmp_path)
                                except OSError:
                                    pass

                    # Mettre à jour metadata
                    current_time = time.time()
                    self.metadata[key] = {
                        "timestamp": current_time,
                        "ttl": ttl_seconds,
                        "expires_at": current_time + ttl_seconds,
                        "size_bytes": compressed_size,
                        "compressed": self.use_compression,
                        "original_size": original_size if self.use_compression else compressed_size,
                        "compression_ratio": compression_ratio,
                        "has_json_copy": self.save_json_copy and self.use_compression,
                    }

                    # Save metadata under file lock to avoid concurrent metadata updates
                    with self._file_lock('.metadata'):
                        self._save_metadata()
                    self._stats["writes"] += 1

                    # Mettre à jour ratio compression moyen
                    if self.use_compression:
                        total_ratio = sum(
                            meta.get("compression_ratio", 0)
                            for meta in self.metadata.values()
                            if meta.get("compressed", False)
                        )
                        compressed_count = sum(
                            1 for meta in self.metadata.values() if meta.get("compressed", False)
                        )
                        self._stats["compression_ratio"] = (
                            total_ratio / compressed_count if compressed_count > 0 else 0
                        )

                    logger.info(log_msg)

                except (OSError, TypeError) as e:
                    logger.error(f"Erreur sauvegarde cache {key}: {e}")

    def invalidate(self, key: str) -> bool:
        """
        Supprime une entrée du cache (fichier compressé, JSON et metadata).

        Args:
            key: Clé du cache à supprimer

        Returns:
            True si supprimé, False si n'existait pas

        Example:
            >>> cache.invalidate("devices")  # Force refresh au prochain get()
        """
        with self._lock:
            # Acquire per-key lock to avoid races with writers
            with self._file_lock(key):
                cache_file_gz = self.cache_dir / f"{key}.json.gz"
                cache_file_json = self.cache_dir / f"{key}.json"
                deleted = False

                # Supprimer fichier compressé
                if cache_file_gz.exists():
                    try:
                        cache_file_gz.unlink()
                        deleted = True
                    except OSError as e:
                        logger.error(f"Erreur suppression cache compressé {key}: {e}")

                # Supprimer fichier JSON lisible
                if cache_file_json.exists():
                    try:
                        cache_file_json.unlink()
                        deleted = True
                    except OSError as e:
                        logger.error(f"Erreur suppression cache JSON {key}: {e}")

                # Supprimer metadata
                if key in self.metadata:
                    del self.metadata[key]
                    # update metadata with metadata lock
                    with self._file_lock('.metadata'):
                        self._save_metadata()
                    deleted = True

                if deleted:
                    self._stats["invalidations"] += 1
                    logger.info(f"🗑️  Cache invalidated: {key}")

                return deleted

    def clear_all_except(self, preserve_keys: List[str]) -> int:
        """
        Supprime tous les caches sauf les clés spécifiées.

        Args:
            preserve_keys: Liste des clés à préserver

        Returns:
            Nombre d'entrées supprimées

        Example:
            >>> count = cache.clear_all_except(['auth_data'])
            >>> print(f"{count} caches supprimés, auth_data préservé")
        """
        with self._lock:
            count = 0
            keys_to_delete = [key for key in self.metadata if key not in preserve_keys]

            for key in keys_to_delete:
                if self.invalidate(key):
                    count += 1

            logger.info(f"🗑️  {count} cache(s) supprimé(s), {len(preserve_keys)} préservé(s)")
            return count

    def clean_expired(self) -> int:
        """
        Supprime uniquement les caches expirés.

        Returns:
            Nombre de caches expirés supprimés

        Example:
            >>> count = cache.clean_expired()
            >>> print(f"{count} caches expirés nettoyés")
        """
        with self._lock:
            count = 0
            expired_keys = [key for key in self.metadata if self._is_expired(key)]

            for key in expired_keys:
                if self.invalidate(key):
                    count += 1

            if count > 0:
                logger.info(f"🧹 {count} cache(s) expiré(s) nettoyé(s)")

            return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du cache.

        Returns:
            Dictionnaire avec hits, misses, hit_rate, entries

        Example:
            >>> stats = cache.get_stats()
            >>> print(f"Hit rate: {stats['hit_rate']:.1%}")
        """
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0

            entries = []
            for key, meta in self.metadata.items():
                remaining = meta["expires_at"] - time.time()
                entries.append(
                    {
                        "key": key,
                        "size_bytes": meta.get("size_bytes", 0),
                        "ttl_seconds": meta["ttl"],
                        "expires_in_seconds": max(0, int(remaining)),
                        "expired": remaining <= 0,
                    }
                )

            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "writes": self._stats["writes"],
                "invalidations": self._stats["invalidations"],
                "hit_rate": hit_rate,
                "compression_enabled": self.use_compression,
                "avg_compression_ratio": self._stats.get("compression_ratio", 0),
                "total_entries": len(entries),
                "entries": entries,
            }

    def _is_expired(self, key: str) -> bool:
        """Vérifie si une entrée de cache est expirée."""
        if key not in self.metadata:
            return True
        return time.time() > self.metadata[key]["expires_at"]

    def _load_metadata(self):
        """Charge le fichier metadata au démarrage."""
        # Load metadata under metadata lock to avoid partial reads during writes
        with self._file_lock('.metadata'):
            if self.metadata_file.exists():
                try:
                    self.metadata = json.loads(self.metadata_file.read_text(encoding="utf-8"))
                    logger.debug(f"Metadata chargé: {len(self.metadata)} entrée(s)")
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning(f"Erreur chargement metadata: {e}, réinitialisation")
                    self.metadata = {}

    def _save_metadata(self):
        """Sauvegarde le fichier metadata."""
        try:
            # Write metadata atomically
            tmp_fd, tmp_path = tempfile.mkstemp(dir=self.cache_dir, prefix='.metadata.', suffix='.tmp')
            try:
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as tf:
                    tf.write(json.dumps(self.metadata, indent=2, ensure_ascii=False))
                    tf.flush()
                    os.fsync(tf.fileno())
                os.replace(tmp_path, str(self.metadata_file))
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
        except OSError as e:
            logger.error(f"Erreur sauvegarde metadata: {e}")

    @contextmanager
    def _file_lock(self, name: str, timeout: float = 5.0):
        """Context manager for a per-name file lock inside the cache dir.

        Uses portalocker if available; otherwise a no-op fallback is used.
        The lock file is `.{name}.lock` inside the cache directory.
        """
        lock_path = self.cache_dir / f".{name}.lock"
        # ensure lockfile exists
        try:
            open(lock_path, "a").close()
        except Exception:
            # best-effort - if we cannot create a lock file, fallback to no-op
            if _portalocker is None:
                yield
                return

        if _portalocker is None:
            # No portalocker available: fall back to no-op (best-effort)
            yield
            return

        # Use portalocker to lock the file descriptor
        try:
            with open(lock_path, "r+") as lf:
                try:
                    _portalocker.lock(lf, _portalocker.LOCK_EX)
                except Exception:
                    # If locking fails, proceed but log a debug message
                    logger.debug(f"Failed acquiring portalocker lock for {lock_path}")
                try:
                    yield
                finally:
                    try:
                        _portalocker.unlock(lf)
                    except Exception:
                        pass
        except Exception:
            # If opening/locking fails, yield as fallback
            yield
