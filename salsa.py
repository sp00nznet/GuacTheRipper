"""
salsa.py  --  The salsa bar. Bring your own Toppings rules, no code required.

Toppings ships a fixed set of mutations. The salsa bar lets a user add their own
in a plain text file and pass it with `--salsa myrules.txt` (or drop it at
~/.chipotle/salsa.txt to load automatically). One rule per line:

    # comments and blank lines are ignored
    suffix 2027        # also try every guess with '2027' on the end
    suffix _backup
    prefix !           # also try every guess with '!' on the front
    sub a @            # an extra character substitution (your own leetspeak)
    sub o 0
    99redballoons      # a bare line is treated as a suffix

Mild. Medium. Hot. Now also: as much salsa as you can carry.
"""

from __future__ import annotations

import os

DEFAULT_PATH = os.environ.get(
    "CHIPOTLE_SALSA",
    os.path.join(os.path.expanduser("~"), ".chipotle", "salsa.txt"),
)


class Salsa:
    """User-supplied extra mutation rules for Toppings."""

    def __init__(self):
        self.suffixes: list[str] = []
        self.prefixes: list[str] = []
        self.subs: dict[str, str] = {}

    def empty(self) -> bool:
        return not (self.suffixes or self.prefixes or self.subs)

    @classmethod
    def from_file(cls, path: str) -> "Salsa":
        s = cls()
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    head = parts[0].lower()
                    if head == "suffix" and len(parts) >= 2:
                        s.suffixes.append(" ".join(parts[1:]))
                    elif head == "prefix" and len(parts) >= 2:
                        s.prefixes.append(" ".join(parts[1:]))
                    elif head == "sub" and len(parts) >= 3:
                        s.subs[parts[1]] = parts[2]
                    else:
                        s.suffixes.append(line)  # bare line == a suffix
        except OSError:
            pass
        return s

    def describe(self) -> str:
        bits = []
        if self.suffixes:
            bits.append(f"{len(self.suffixes)} suffix(es)")
        if self.prefixes:
            bits.append(f"{len(self.prefixes)} prefix(es)")
        if self.subs:
            bits.append(f"{len(self.subs)} sub(s)")
        return ", ".join(bits) or "empty"


def load_salsa(path: str | None) -> Salsa | None:
    """Load an explicit salsa file, else the default if it exists. None if neither."""
    if path:
        return Salsa.from_file(path)
    if os.path.exists(DEFAULT_PATH):
        return Salsa.from_file(DEFAULT_PATH)
    return None
