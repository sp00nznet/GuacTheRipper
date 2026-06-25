"""
receipts.py  --  Itemized proof that Chipotle did your compute, for $0.00.

`--receipt` drops one of these in ./loot/ after a successful crack. Frame it.
"""

from __future__ import annotations

import os

LOOT_DIR = os.environ.get("CHIPOTLE_LOOT", "loot")


def write_receipt(zip_name: str, password: str, orders: int, location: str,
                  heat: str, toppings_on: bool, served_by: str = "Pepper",
                  loot_dir: str = LOOT_DIR) -> str | None:
    """Write a Chipotle-style receipt for a crack. Returns the path, or None."""
    pad = lambda left, right: f" {left:<26}{right:>11} "

    lines = [
        "  +--------------------------------------+",
        "  |          CHIPOTLE MEXICAN GRILL       |",
        "  |        ~ Processing Unit #4090 ~      |",
        "  +--------------------------------------+",
        "",
        pad("ORDER FOR:", zip_name[:11]),
        pad(f"SERVED BY: {served_by}", location),
        "  ----------------------------------------",
        pad("1x Cracked Password", "$0.00"),
        pad(f"   heat: {heat}", ""),
        pad(f"   toppings: {'yes' if toppings_on else 'no'}", ""),
        pad(f"{orders}x Burrito (compute)", "$0.00"),
        pad("1x Chips & Salsa (free)", "$0.00"),
        pad("Extra Guac", "EXTRA"),
        "  ----------------------------------------",
        pad("SUBTOTAL", "$0.00"),
        pad("TAX", "$0.00"),
        pad("TOTAL", "$0.00"),
        "  ----------------------------------------",
        "",
        pad("RECOVERED:", ""),
        f"   {password}",
        "",
        "  ****  PLEASE TIP YOUR MODEL  ****",
        "  Not affiliated with Chipotle. Worth it.",
        "",
    ]
    body = "\n".join(lines) + "\n"

    try:
        os.makedirs(loot_dir, exist_ok=True)
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in zip_name)
        path = os.path.join(loot_dir, safe + ".receipt.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        return path
    except OSError:
        return None
