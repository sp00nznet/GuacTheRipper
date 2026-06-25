"""
stats.py  --  Guac surcharge analytics.

`--stats` prints a little dashboard at the end of a run: how many actual Pepper
orders you placed, how much free local compute your machine did instead, and --
the whole point -- how many orders you DIDN'T have to place because the Chips
basket, the Sour Cream cache, and Toppings did the work for free.

Guac is extra. The analytics are not.
"""

from __future__ import annotations

from collections import Counter

# Which crack sources placed zero orders vs. rescued a paid one.
ZERO_ORDER = {"chips", "cache"}
RESCUED = {"toppings"}

LABELS = {
    "chips": "chips basket   ",
    "cache": "sour cream     ",
    "toppings": "toppings       ",
    "bot": "the bot         ",
    "doordash": "doordash       ",
    "plaintext": "wasn't encrypted",
}


class Stats:
    """Counters for one run. Mostly touched from the main thread."""

    def __init__(self):
        self.archives = 0
        self.cracked = 0
        self.orders = 0                # bot orders that actually reached the board
        self.local_tested = 0          # candidates tested locally (free compute)
        self.by_source: Counter = Counter()

    def archive(self) -> None:
        self.archives += 1

    def order(self) -> None:
        self.orders += 1

    def local(self, k: int) -> None:
        self.local_tested += k

    def crack(self, source: str) -> None:
        self.cracked += 1
        self.by_source[source] += 1

    def render(self, orders: int, rounds: int) -> str:
        zero = sum(self.by_source[s] for s in ZERO_ORDER)
        rescued = sum(self.by_source[s] for s in RESCUED)
        # Rough but honest: each zero-order crack saved ~a full run of orders.
        saved = zero * rounds + rescued

        lines = [
            "",
            "  +==== GUAC SURCHARGE ANALYTICS ====+",
            f"  Archives processed     : {self.archives}",
            f"  Cracked                : {self.cracked}",
            f"  Pepper orders placed   : {orders}   (real burritos bought)",
            f"  Local candidates tried : {self.local_tested:,}   (free, on your machine)",
        ]
        if self.cracked:
            lines.append("  Cracks by source:")
            for src, n in self.by_source.most_common():
                lines.append(f"     {LABELS.get(src, src):<16}: {n}")
        lines += [
            f"  Orders you DIDN'T place : ~{saved}   "
            f"(chips/cache cracks x rounds, + toppings rescues)",
            "  GPU cost avoided        : $1,800.00. You're welcome.",
            "  +==================================+",
        ]
        return "\n".join(lines)
