"""Cache module provides utilities for caching.

This module provides utilities for caching results to disk.
It follows the XDG Base Directory Configuration guidance, and as such caches to
$XDG_CACHE_HOME or $HOME/.cache if $XDG_CACHE_HOME is not set.
"""
import json
import os

from typing import Optional, Any

Serializable = Any  # this doesn't help with type hints at all but is for documentation


class SerializableError(Exception):
    pass


def _get_cache_dir() -> str:
    xdg_cache_home = os.environ.get("XDG_CACHE_HOME")

    if not xdg_cache_home:
        fallback_path = os.path.join(os.environ.get("HOME"), ".cache")
        xdg_cache_home = fallback_path

    allegro_cache = os.path.join(xdg_cache_home, "allegro")
    return allegro_cache


class Cache:
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir if cache_dir else _get_cache_dir()

    def _create_cache_dir(self):
        try:
            os.mkdir(self.cache_dir)
        except FileExistsError:
            pass

    def save(self, serializable_object: Serializable, filename: str):
        self._create_cache_dir()

        try:
            serialized = json.dumps(serializable_object)
        except (TypeError, OverflowError):
            raise SerializableError("Cannot serialize this object.")

        cache_filename = os.path.join(self.cache_dir, filename)

        with open(cache_filename, "w+") as f:
            f.write(serialized)

    def load(self, filename: str) -> Serializable:
        filepath = os.path.join(self.cache_dir, filename)
        if not os.path.exists(filepath):
            raise IOError(f"File {filepath} does not exist.")

        with open(filepath, "r") as f:
            contents = f.read()
            deserialized = json.loads(contents)
            return deserialized
