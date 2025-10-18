"""Utilities to map friendly names to identifiers and back.

This module provides small helpers used by CLI commands and managers to
resolve a user-friendly name to the backend id (serial, id, entityId, ...)
and vice-versa. It is intentionally simple and works on lists of dicts.

Examples:
    serial, item = find_id_by_name(devices, "Salon Echo", name_keys=("accountName",))
    name = find_name_by_id(devices, serial)
"""
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


def _normalize(s: Any) -> str:
    return str(s).lower().strip() if s is not None else ""


def find_id_by_name(
    items: Iterable[Dict[str, Any]],
    name: str,
    *,
    name_keys: Sequence[str] = ("name", "accountName", "friendlyName"),
    id_keys: Sequence[str] = ("id", "serialNumber", "deviceSerialNumber", "entityId"),
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Find the first item whose name matches `name` (case-insensitive).

    Returns a tuple (id_value, matched_item). If not found, returns (None, None).
    The function tries the provided `name_keys` on each item to compare the
    friendly name and then returns the first matching `id_keys` value.
    """
    if not name:
        return None, None

    target = _normalize(name)

    for item in items:
        for nk in name_keys:
            if nk in item and _normalize(item.get(nk)) == target:
                # find id key
                for ik in id_keys:
                    if ik in item and item.get(ik) is not None:
                        return str(item.get(ik)), item
                # If no id key found, still return the matched item
                return None, item

    # fallback: try partial match (contains)
    for item in items:
        for nk in name_keys:
            if nk in item and target in _normalize(item.get(nk)):
                for ik in id_keys:
                    if ik in item and item.get(ik) is not None:
                        return str(item.get(ik)), item
                return None, item

    return None, None


def find_name_by_id(
    items: Iterable[Dict[str, Any]],
    id_value: Any,
    *,
    id_keys: Sequence[str] = ("id", "serialNumber", "deviceSerialNumber", "entityId"),
    name_keys: Sequence[str] = ("name", "accountName", "friendlyName"),
) -> Optional[str]:
    """Find friendly name for the given id_value. Returns None if not found."""
    if id_value is None:
        return None
    target = _normalize(id_value)
    for item in items:
        for ik in id_keys:
            if ik in item and _normalize(item.get(ik)) == target:
                for nk in name_keys:
                    if nk in item and item.get(nk):
                        return item.get(nk)
                # fallback to returning the id string if no name available
                return str(item.get(ik))
    return None


def extract_mapping(items: Iterable[Dict[str, Any]], id_key: str, name_key: str) -> List[Tuple[str, str]]:
    """Return list of (id, name) tuples for the given keys (skip missing)."""
    result: List[Tuple[str, str]] = []
    for it in items:
        if id_key in it and name_key in it and it.get(id_key) is not None and it.get(name_key):
            result.append((str(it.get(id_key)), str(it.get(name_key))))
    return result
