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
from concurrent.futures import ThreadPoolExecutor

from chipotle_gpu import ChipotleGPU, GuacOrder, build_prompt


def _urls_from_env(explicit: str | None = None) -> list[str]:
    """Figure out which Chipotles to dial: CLI > CHIPOTLE_GPU_URLS > single URL."""
    raw = explicit or os.environ.get("CHIPOTLE_GPU_URLS")
    if raw:
        return [u.strip() for u in raw.split(",") if u.strip()]
    return [ChipotleGPU().url]  # falls back to single CHIPOTLE_GPU_URL/default


class ChipotleCluster:
    """A franchise of Chipotle Processing Units, melted together with queso."""

    def __init__(self, urls: list[str] | None = None, model: str | None = None,
                 key: str | None = None, parallel: int | None = None,
                 explicit_urls: str | None = None):
        url_list = urls if urls is not None else _urls_from_env(explicit_urls)

        kw = {}
        if model is not None:
            kw["model"] = model
        if key is not None:
            kw["key"] = key
        # Each location names itself @loc1, @loc2, ... for friendly output.
        self.locations = [
            ChipotleGPU(url=u, label=f"@loc{i + 1}", **kw)
            for i, u in enumerate(url_list)
        ]
        self.open_locations = [loc for loc in self.locations if loc.online]

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
        bit = f"{up}/{total} Chipotle Processing Unit(s) open"
        if closed:
            bit += f" ({closed} closed for remodeling)"
        return f"{bit}, queso x{min(self.parallel, max(1, up))}"

    def guesses(self, zip_name: str, hint: str | None, rounds: int,
                exclude: set[str] | None = None):
        """
        Yield GuacOrders. Round-robin across open locations (load balancing),
        `parallel` orders in flight at once (queso clustering).
        """
        seen: set[str] = set(exclude or ())
        locs = self.open_locations
        if not locs:
            return

        width = min(self.parallel, len(locs)) or 1
        idx = 0
        placed = 0
        with ThreadPoolExecutor(max_workers=width) as pool:
            while placed < rounds:
                batch = []
                for _ in range(min(width, rounds - placed)):
                    loc = locs[idx % len(locs)]
                    idx += 1
                    placed += 1
                    fut = pool.submit(loc.order, build_prompt(zip_name, hint, placed))
                    batch.append((loc, fut))
                for loc, fut in batch:
                    candidate = fut.result()
                    if candidate and candidate not in seen:
                        seen.add(candidate)
                        yield GuacOrder(candidate=candidate,
                                        source="chipotle", location=loc.label)
