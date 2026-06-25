"""
feedback.py  --  Burrito-of-the-day. The bot learns from yesterday's mistakes.

Without this, every order is independent and Pepper happily suggests the same
five passwords on a loop. The Feedback board collects the guesses we've already
tried and *rejected*, and quietly slips that list into the next order's prompt:
"these were wrong, go in a different direction." It's a closed loop -- each miss
makes the next guess smarter.

Thread-safe, because the queso cluster reads it from several registers at once.
Bounded, because nobody wants to read a prompt with 500 rejected burritos in it.
"""

from __future__ import annotations

import threading


class Feedback:
    """A running, bounded list of WRONG guesses to feed back to the bot."""

    def __init__(self, enabled: bool = True, max_items: int = 12):
        self.enabled = enabled
        self.max_items = max_items
        self._items: list[str] = []
        self._lock = threading.Lock()

    def reject(self, guess: str) -> None:
        """Record a guess that didn't work (keeps only the most recent ones)."""
        if not self.enabled or not guess:
            return
        with self._lock:
            if guess in self._items:
                return
            self._items.append(guess)
            if len(self._items) > self.max_items:
                self._items = self._items[-self.max_items:]

    def snapshot(self) -> list[str]:
        if not self.enabled:
            return []
        with self._lock:
            return list(self._items)
