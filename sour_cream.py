"""
sour_cream.py  --  Sour Cream caching.

Memoize Pepper's guesses so we stop re-ordering the same burrito. Two layers:

  1. Solved archives:  fingerprint(file) -> the password that cracked it.
     Re-run on the same archive = instant crack, zero orders placed.

  2. Guess memory:     (archive name + hint) -> every candidate Pepper has
     ever suggested. On a re-run we replay those cold from the fridge BEFORE
     bothering a Chipotle, because day-old guac still works.

Stored as one tidy JSON tub at ~/.chipotle/sour_cream.json (override with
$CHIPOTLE_CACHE). It's sour cream: it keeps, but don't leave it out forever.
"""

from __future__ import annotations

import hashlib
import json
import os

DEFAULT_PATH = os.environ.get(
    "CHIPOTLE_CACHE",
    os.path.join(os.path.expanduser("~"), ".chipotle", "sour_cream.json"),
)


class SourCream:
    """A small JSON tub of remembered passwords and guesses."""

    def __init__(self, path: str = DEFAULT_PATH, enabled: bool = True):
        self.path = path
        self.enabled = enabled
        self._dirty = False
        self.data = {"solved": {}, "guesses": {}}
        if self.enabled:
            self._load()

    # -- fingerprints ---------------------------------------------------------

    @staticmethod
    def fingerprint(zip_path: str) -> str:
        """A cheap, stable id for an archive: size + first 64 KiB, hashed."""
        h = hashlib.sha256()
        try:
            h.update(str(os.path.getsize(zip_path)).encode())
            with open(zip_path, "rb") as f:
                h.update(f.read(65536))
        except OSError:
            h.update(zip_path.encode())
        return h.hexdigest()[:16]

    # -- solved-password layer ------------------------------------------------

    def remembered_password(self, zip_path: str) -> str | None:
        if not self.enabled:
            return None
        return self.data["solved"].get(self.fingerprint(zip_path))

    def remember_password(self, zip_path: str, password: str) -> None:
        if not self.enabled:
            return
        self.data["solved"][self.fingerprint(zip_path)] = password
        self._dirty = True

    # -- guess-memory layer ---------------------------------------------------

    def cached_guesses(self, key: str) -> list[str]:
        if not self.enabled:
            return []
        return list(self.data["guesses"].get(key, []))

    def add_guess(self, key: str, guess: str) -> None:
        if not self.enabled:
            return
        bucket = self.data["guesses"].setdefault(key, [])
        if guess not in bucket:
            bucket.append(guess)
            self._dirty = True

    # -- the tub itself -------------------------------------------------------

    def _load(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self.data["solved"].update(loaded.get("solved", {}))
            self.data["guesses"].update(loaded.get("guesses", {}))
        except (OSError, ValueError):
            pass  # fresh tub

    def save(self) -> None:
        if not self.enabled or not self._dirty:
            return
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            self._dirty = False
        except OSError:
            pass  # the fridge is full; oh well
