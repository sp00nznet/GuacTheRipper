"""
sticker_book.py  --  The GuacTheRipper loyalty program.

Every crack earns a stamp. Collect ten and your next crack is *on the house* --
an extraordinary $0.00 value, same as all the others. It is a loyalty program
for a free product and we will not be explaining the business model.

Stamps persist across runs in ~/.chipotle/sticker_book.json (override with
$CHIPOTLE_STICKERS). Disable the whole thing with --no-loyalty if you have, for
some reason, no soul.
"""

from __future__ import annotations

import json
import os

DEFAULT_PATH = os.environ.get(
    "CHIPOTLE_STICKERS",
    os.path.join(os.path.expanduser("~"), ".chipotle", "sticker_book.json"),
)


class StickerBook:
    """A punch card. Ten stamps to a free crack."""

    def __init__(self, path: str = DEFAULT_PATH, enabled: bool = True):
        self.path = path
        self.enabled = enabled
        self.data = {"stamps": 0, "total": 0, "free_cracks": 0}
        if enabled:
            self._load()

    def add_crack(self) -> dict:
        """Record one crack, award the reward on every tenth stamp."""
        self.data["total"] += 1
        self.data["stamps"] += 1
        reward = self.data["stamps"] >= 10
        filled = self.data["stamps"]
        if reward:
            self.data["stamps"] = 0
            self.data["free_cracks"] += 1
        self._save()
        return {"filled": filled, "total": self.data["total"],
                "free_cracks": self.data["free_cracks"], "reward": reward}

    @staticmethod
    def card(stamps: int) -> str:
        stamps = max(0, min(10, stamps))
        return "[" + "*" * stamps + "." * (10 - stamps) + f"] {stamps}/10"

    def _load(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            for k in self.data:
                self.data[k] = int(loaded.get(k, self.data[k]))
        except (OSError, ValueError, TypeError):
            pass  # brand-new card

    def _save(self) -> None:
        if not self.enabled:
            return
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except OSError:
            pass
