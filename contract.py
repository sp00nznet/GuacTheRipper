"""
contract.py  --  Catering contracts. A JSON job file for big multi-archive runs.

Instead of a giant command line, describe the whole job once:

    {
      "defaults": { "heat": "hot", "rounds": 100, "provider": "chipotle",
                    "combo": 3, "receipt": true, "stats": true },
      "archives": [
        { "path": "q3_backups.zip", "hint": "project codename + year" },
        { "path": "photos.zip", "hint": "dog name", "heat": "medium" },
        "misc.zip"
      ]
    }

Run it with `--contract job.json`. `defaults` set the whole run; each archive may
override `hint`, `heat`, `rounds`, or `combo`. Bare strings are just a path.
"""

from __future__ import annotations

import json

# Keys a contract's "defaults" block may set on the run (json key -> args attr).
DEFAULT_KEYS = {
    "hint": "hint", "rounds": "rounds", "heat": "heat", "combo": "combo",
    "provider": "provider", "providers": "providers", "budget": "budget",
    "queso": "queso", "receipt": "receipt", "stats": "stats",
    "no_toppings": "no_toppings", "no_chips": "no_chips",
    "no_feedback": "no_feedback", "no_cache": "no_cache",
    "no_loyalty": "no_loyalty", "salsa": "salsa", "locations": "locations",
}

# Keys an individual archive entry may override.
ARCHIVE_KEYS = ("hint", "heat", "rounds", "combo")


def load_contract(path: str):
    """Parse a catering contract. Returns (defaults: dict, archives: list[dict]).

    Raises ValueError with a friendly message on malformed input."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise ValueError(f"couldn't read contract {path!r}: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("a contract must be a JSON object with 'archives'")

    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("'defaults' must be an object")

    raw = data.get("archives", [])
    if not isinstance(raw, list) or not raw:
        raise ValueError("'archives' must be a non-empty list")

    archives = []
    for entry in raw:
        if isinstance(entry, str):
            archives.append({"path": entry})
        elif isinstance(entry, dict) and entry.get("path"):
            archives.append(entry)
        else:
            raise ValueError(f"bad archive entry: {entry!r} (need a path)")
    return defaults, archives
