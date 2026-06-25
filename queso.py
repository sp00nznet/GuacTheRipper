"""
queso.py  --  Queso clustering + multi-location load balancing.

One Chipotle Processing Unit (a single Pepper proxy) is rate-limited by
anonymous sessions -- the proxy's own README admits MAX_POOL_SIZE=5. At the
lunch rush that single grill becomes the bottleneck.

So we cluster. Point GuacTheRipper at several Pepper proxies (several
"locations") and it will:

  * Multi-location load balancing -- round-robin every order across all the
    Chipotles that are currently open (online).

  * Queso clustering -- place several orders CONCURRENTLY (the `parallel`
    knob, a.k.a. how many registers you're working at once). Melts many CPUs
    into one gooey rig.

Set it up with a comma-separated list:

    export CHIPOTLE_GPU_URLS="http://localhost:3000/v1,http://localhost:3001/v1"

A cluster of one location is still a perfectly valid (if lonely) cluster.
"""

from __future__ import annotations

import os
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from chipotle_gpu import ChipotleGPU, GuacOrder, OrderError, build_prompt


def _urls_from_env(explicit: str | None = None,
                   fallback: str | None = None) -> list[str]:
    """Figure out which locations to dial: CLI > CHIPOTLE_GPU_URLS > provider default."""
    raw = explicit or os.environ.get("CHIPOTLE_GPU_URLS")
    if raw:
        return [u.strip() for u in raw.split(",") if u.strip()]
    return [fallback or ChipotleGPU().url]


class ChipotleCluster:
    """A franchise of Chipotle Processing Units, melted together with queso."""

    def __init__(self, urls: list[str] | None = None, parallel: int | None = None,
                 explicit_urls: str | None = None, temperature: float = 0.9,
                 provider=None):
        from providers import CHIPOTLE
        self.provider = provider or CHIPOTLE

        url_list = (urls if urls is not None
                    else _urls_from_env(explicit_urls, self.provider.url))

        # Each location names itself @loc1, @loc2, ... for friendly output.
        self.locations = [
            ChipotleGPU(url=u, label=f"@loc{i + 1}", temperature=temperature,
                        model=self.provider.model, key=self.provider.api_key,
                        system_prompt=self.provider.persona)
            for i, u in enumerate(url_list)
        ]
        self.open_locations = [loc for loc in self.locations if loc.online]
        self._lock = threading.Lock()  # guards Carnitas hot-swap bookkeeping

        # Default queso = work every open register at once, but never melt past
        # what's actually open. One register if a lonely cluster.
        self.parallel = parallel or max(1, len(self.open_locations))

    @property
    def online(self) -> bool:
        return bool(self.open_locations)

    def status(self) -> str:
        total = len(self.locations)
        up = len(self.open_locations)
        closed = total - up
        bit = (f"{up}/{total} {self.provider.unit}(s) open via "
               f"{self.provider.label} ({self.provider.bot})")
        if closed:
            bit += f" ({closed} closed for remodeling)"
        return f"{bit}, queso x{min(self.parallel, max(1, up))}"

    def _serve(self, prompt: str, start: int):
        """Take one order, with Carnitas hot-swap: if the assigned register is
        down, fail over to the next open one. Returns (guess, location, swapped)."""
        with self._lock:
            locs = list(self.open_locations)
        if not locs:
            return None, None, False

        n = len(locs)
        for k in range(n):
            loc = locs[(start + k) % n]
            if not loc.online:
                continue
            try:
                return loc.order(prompt), loc, (k > 0)
            except OrderError:
                # Register closed mid-shift. Mark it down so nobody else queues
                # there, then walk to the next open Chipotle.
                with self._lock:
                    loc.online = False
                    if loc in self.open_locations:
                        self.open_locations.remove(loc)
        return None, None, False

    def guesses(self, zip_name: str, hint: str | None, rounds: int,
                exclude: set[str] | None = None, budget=None, feedback=None):
        """
        Yield GuacOrders. Round-robin across open locations (load balancing),
        `parallel` orders in flight at once (queso clustering), each order
        self-healing via Carnitas hot-swap if its register goes down, the next
        batch always cooking while you test the last (Mobile order-ahead), and
        each new order steered away from past misses (Burrito-of-the-day).

        `budget`, if given, caps how many orders we're allowed to place.
        `feedback`, if given, supplies the running list of rejected guesses.
        """
        seen: set[str] = set(exclude or ())
        if not self.open_locations:
            return

        width = min(self.parallel, len(self.open_locations)) or 1
        placed = 0
        inflight: deque = deque()
        pool = ThreadPoolExecutor(max_workers=width)

        def order_ahead() -> bool:
            """Put one more order in the pool, if rounds/budget/grills allow."""
            nonlocal placed
            if placed >= rounds or not self.open_locations:
                return False
            if budget is not None and not budget.take():
                return False
            rejected = feedback.snapshot() if feedback else None
            inflight.append(pool.submit(
                self._serve,
                build_prompt(zip_name, hint, placed + 1, rejected),
                placed))
            placed += 1
            return True

        try:
            for _ in range(width):
                if not order_ahead():
                    break
            while inflight:
                fut = inflight.popleft()
                order_ahead()  # refill BEFORE we hand back a result = order-ahead
                candidate, loc, swapped = fut.result()
                if candidate and loc and candidate not in seen:
                    seen.add(candidate)
                    yield GuacOrder(
                        candidate=candidate, source="chipotle",
                        location=loc.label,
                        note=("carnitas hot-swap" if swapped else ""))
        finally:
            # Consumer cracked it (or bailed) -> stop ordering ahead immediately.
            pool.shutdown(wait=False, cancel_futures=True)
