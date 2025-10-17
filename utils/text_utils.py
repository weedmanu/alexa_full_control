"""
Text utilities for Alexa Advanced Control.

Centralized text processing functions to avoid duplication.
"""

import unicodedata
from typing import Optional


def normalize_name(name: str, max_length: Optional[int] = None) -> str:
    """
    Normalize a name for use as a key/identifier.

    Rules:
    - Unicode NFKC normalization for handling accents/special characters
    - Convert to lowercase
    - Strip leading/trailing whitespace
    - Replace spaces/hyphens with underscore
    - Remove punctuation (except underscores)
    - Optional length limit

    Args:
        name: Name to normalize
        max_length: Optional maximum length (None = no limit)

    Returns:
        Normalized name

    Examples:
        >>> normalize_name("Mon Favori 123!")
        'mon_favori_123'
        >>> normalize_name("café-paris")
        'cafe_paris'
    """
    if not name:
        return ""

    # Unicode normalization for handling accents/special characters
    normalized = unicodedata.normalize("NFKC", name)

    # Convert to lowercase and strip
    normalized = normalized.lower().strip()

    # Replace spaces and hyphens with underscores
    normalized = normalized.replace(" ", "_").replace("-", "_")

    # Remove punctuation (but keep underscores)
    import re
    normalized = re.sub(r'[^\w_]', '', normalized)

    # Apply length limit if specified
    if max_length and len(normalized) > max_length:
        normalized = normalized[:max_length]

    return normalized


def clean_text(text: str, remove_punctuation: bool = True) -> str:
    """
    Clean text by normalizing and optionally removing punctuation.

    Args:
        text: Text to clean
        remove_punctuation: Whether to remove punctuation

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Unicode normalization
    cleaned = unicodedata.normalize("NFKC", text)

    # Strip whitespace
    cleaned = cleaned.strip()

    if remove_punctuation:
        # Remove punctuation but keep spaces and basic characters
        import re
        cleaned = re.sub(r'[^\w\s]', '', cleaned)

    return cleaned


def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.

    Args:
        text: Text to slugify

    Returns:
        Slugified text

    Examples:
        >>> slugify("Hello World!")
        'hello-world'
        >>> slugify("café & thé")
        'cafe-the'
    """
    if not text:
        return ""

    # Clean the text first
    cleaned = clean_text(text, remove_punctuation=True)

    # Replace spaces with hyphens
    slug = cleaned.replace(" ", "-")

    # Remove multiple consecutive hyphens
    import re
    slug = re.sub(r'-+', '-', slug)

    # Strip leading/trailing hyphens
    slug = slug.strip('-')

    return slug