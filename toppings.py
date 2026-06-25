"""
toppings.py  --  Extra toppings make every burrito go further.

Real password crackers (hashcat, John) don't just try a wordlist raw -- they
apply *rules*: capitalize it, leetspeak it, slap a year on the end. Pepper hands
us one good base guess per order; Toppings turns that single guess into a whole
bowl of local candidates we test for free, no extra orders placed.

This is the genuinely-useful bit wearing a sombrero. `--heat` controls how
loaded the bowl gets:

    mild    -> base + casing + a couple suffixes      (fast, polite)
    medium  -> + leetspeak + common years             (the default)
    hot     -> + more casing/leet combos + spicy suffixes (everything, extra)
"""

from __future__ import annotations

# a -> @, e -> 3, i -> 1, o -> 0, s -> $  (both cases)
LEET = str.maketrans({
    "a": "@", "A": "@", "e": "3", "E": "3", "i": "1", "I": "1",
    "o": "0", "O": "0", "s": "$", "S": "$",
})

SUFFIXES = {
    "mild":   ["", "1", "!"],
    "medium": ["", "1", "!", "123", "2024", "2025", "2026"],
    "hot":    ["", "1", "!", "12", "123", "1234", "2023", "2024", "2025",
               "2026", "01", "69", "420", "!!", "#1", "$"],
}

# How many local candidates we'll spin out of a single Pepper guess.
CAP = {"mild": 12, "medium": 48, "hot": 160}


def toppings(base: str, heat: str = "medium"):
    """Yield local variants of `base`, base itself first, deduped, capped."""
    heat = heat if heat in SUFFIXES else "medium"

    case_order = [base, base.capitalize(), base.lower(), base.upper()]
    if heat in ("medium", "hot"):
        case_order.append(base.translate(LEET))
    if heat == "hot":
        case_order.append(base.capitalize().translate(LEET))
        case_order.append(base.upper().translate(LEET))

    sfx = SUFFIXES[heat]
    cap = CAP[heat]

    out: list[str] = []
    seen: set[str] = set()
    for v in case_order:
        for s in sfx:
            cand = v + s
            if cand and cand not in seen:
                seen.add(cand)
                out.append(cand)
                if len(out) >= cap:
                    return out
    return out
