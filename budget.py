"""
budget.py  --  A burrito budget. Don't bankrupt the franchise (or anger the grill).

Pepper's proxy is rate-limited by anonymous sessions (MAX_POOL_SIZE=5). Hammering
it is rude and gets you throttled. The Budget caps how many *orders* (Pepper round
trips) a whole run may place -- shared across every archive in a catering job and
every thread in the queso cluster. Local work (chips basket, toppings, cached
leftovers) is free and never counts against it.

`None` total means "order till you drop" (the old behavior).
"""

from __future__ import annotations

import threading


class Budget:
    """A thread-safe cap on Pepper orders for one run."""

    def __init__(self, total: int | None = None):
        self.total = total
        self._spent = 0
        self._lock = threading.Lock()

    def take(self) -> bool:
        """Reserve one order. Returns False once the budget is spent."""
        with self._lock:
            if self.total is None or self._spent < self.total:
                self._spent += 1
                return True
            return False

    @property
    def spent(self) -> int:
        with self._lock:
            return self._spent

    def remaining(self) -> int | None:
        if self.total is None:
            return None
        with self._lock:
            return max(0, self.total - self._spent)

    def exhausted(self) -> bool:
        if self.total is None:
            return False
        with self._lock:
            return self._spent >= self.total
