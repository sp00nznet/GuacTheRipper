#!/usr/bin/env python3
r"""
   ____                 _____ _          ____  _
  / ___|_   _  __ _  __|_   _| |__   ___|  _ \(_)_ __  _ __   ___ _ __
 | |  _| | | |/ _` |/ __|| | | '_ \ / _ \ |_) | | '_ \| '_ \ / _ \ '__|
 | |_| | |_| | (_| | (__ | | | | | |  __/  _ <| | |_) | |_) |  __/ |
  \____|\__,_|\__,_|\___||_| |_| |_|\___|_| \_\_| .__/| .__/ \___|_|
                                                |_|   |_|

GuacTheRipper -- ZipRipper's soul, Chipotle's compute.

The original ZipRipper cracks ZIPs with John the Ripper on your GPU.
GuacTheRipper fires John, hires Guac, and offloads every password guess to a
Chipotle Processing Unit (the Pepper support bot, via chipotlai-max).

No GPU. No electricity bill. Just vibes and lime.

Usage:
    python guactheripper.py secret.zip
    python guactheripper.py secret.zip --hint "my dog's name + birth year"
    python guactheripper.py secret.zip --doordash rockyou.txt   # offline fallback
    python guactheripper.py secret.zip --rounds 200             # more burritos
"""

from __future__ import annotations

import argparse
import glob
import sys
import time
import zipfile

from budget import Budget
from chips import BASKET
from feedback import Feedback
from providers import PROVIDERS
from queso import ChipotleCluster
from receipts import write_receipt
from sour_cream import SourCream
from sticker_book import StickerBook
from toppings import toppings

# --heat maps to how spicy Pepper runs (temperature) and how loaded the bowl gets.
HEAT_TEMP = {"mild": 0.4, "medium": 0.9, "hot": 1.3}

# ASCII tokens instead of emoji so output renders on every console, including
# Windows cp1252 terminals that treat a burrito glyph as a capital offense.
BURRITO = "#"          # one (1) burrito of progress
GUAC = "[guac]"
PEPPER = "[ CPU ]"     # Chipotle Processing Unit
FIRE = "***"
CREAM = "[cream]"      # sour cream cache
CHIPS = "[chips]"      # the free chips basket
LOYAL = "[loyal]"      # the sticker book


def banner() -> None:
    print(__doc__.split("Usage:")[0])


def _can_open(path: str, password: str) -> bool:
    """Lightweight check: can we read the first file with this password?"""
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            if not names:
                return False
            with zf.open(names[0], pwd=password.encode("utf-8")) as f:
                f.read(1)
        return True
    except (RuntimeError, zipfile.BadZipFile, OSError):
        return False


def doordash_mode(path: str, wordlist: str, gpu_offline: bool) -> str | None:
    """The fallback nobody is proud of: a plain local wordlist."""
    why = "no Chipotle within delivery radius" if gpu_offline else "you asked nicely"
    print(f"{BURRITO}  DoorDash mode engaged ({why}). Reading {wordlist}...")
    try:
        with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                pw = line.rstrip("\n")
                if not pw:
                    continue
                if i % 1000 == 0:
                    print(f"   ...{i:,} candidates delivered cold")
                if _can_open(path, pw):
                    return pw
    except OSError as e:
        print(f"   couldn't read wordlist: {e}")
    return None


def _crack_with(path: str, base: str, heat: str, use_toppings: bool) -> str | None:
    """Test a base guess and (optionally) its Toppings. Returns the winner."""
    for cand in (toppings(base, heat) if use_toppings else [base]):
        if _can_open(path, cand):
            return cand
    return None


def _show(n: int, base: str, label: str, source: str, note: str = "") -> None:
    """Print one order on the board."""
    bar = (BURRITO * min(n, 18)).ljust(18, ".")
    extra = f"  <{note}>" if note else ""
    print(f"  [{bar}] order #{n:<3} {source:<11}{label:<8} {base!r}{extra}")


def chipotle_mode(path: str, cluster: ChipotleCluster, cache: SourCream,
                  hint: str | None, rounds: int, heat: str, use_toppings: bool,
                  use_chips: bool, budget: Budget,
                  use_feedback: bool) -> tuple[str | None, int, str]:
    """The main event: chips, then the fridge, then Pepper guesses + Toppings.

    Returns (password_or_None, orders_placed, serving_location)."""
    zip_name = path.replace("\\", "/").split("/")[-1]
    key = f"{zip_name}|{hint or ''}"
    bot = cluster.provider.bot
    tried: set[str] = set()
    orders_placed = 0  # only counts real Pepper orders (chips/leftovers are free)
    feedback = Feedback(enabled=use_feedback)  # Burrito-of-the-day learning board

    # 1. Sour Cream: have we already cracked THIS exact archive? Instant guac.
    remembered = cache.remembered_password(path)
    if remembered and _can_open(path, remembered):
        print(f"{CREAM}  We've cracked this archive before. "
              f"Pulling the password from the fridge -- zero orders placed.")
        return remembered, 0, "the fridge"

    print(f"{PEPPER}  {cluster.status()}  |  heat: {heat}  |  "
          f"toppings: {'on' if use_toppings else 'off'}")

    # 2. Chips basket: free common passwords, tried locally before any order.
    if use_chips:
        print(f"{CHIPS}  Munching the free chips basket ({len(BASKET)} usual "
              f"suspects) before bothering {bot}...")
        for chip in BASKET:
            if chip in tried:
                continue
            tried.add(chip)
            win = _crack_with(path, chip, heat, use_toppings)
            if win:
                print(f"{CHIPS}  A chip cracked it: {win!r} -- zero orders placed.")
                cache.remember_password(path, win)
                return win, 0, "the chips basket"

    # 3. Sour Cream: replay every guess Pepper has ever made for this job, cold.
    leftovers = cache.cached_guesses(key)
    if leftovers:
        print(f"{CREAM}  Replaying {len(leftovers)} cached guess(es) before ordering fresh.")
    n = 0
    for base in leftovers:
        if base in tried:
            continue
        tried.add(base)
        n += 1
        _show(n, base, "leftovers", "sour-cream")
        win = _crack_with(path, base, heat, use_toppings)
        if win:
            if win != base:
                print(f"           + topping {win!r} cracked it")
            cache.remember_password(path, win)
            return win, 0, "the fridge"
        feedback.reject(base)

    # 4. Fresh orders: load-balanced, queso-clustered, ordering ahead, learning.
    if budget.exhausted():
        print(f"{GUAC}  Burrito budget already spent -- no fresh orders this run.")
        return None, 0, ""
    cap = min(rounds, budget.remaining()) if budget.remaining() is not None else rounds
    learn = "learning from misses, " if use_feedback else ""
    print(f"{GUAC}  {bot} is on the clock. Placing up to {cap} fresh orders "
          f"({learn}ordering ahead).\n")
    for order in cluster.guesses(zip_name, hint, rounds, exclude=tried,
                                 budget=budget, feedback=feedback):
        tried.add(order.candidate)
        n += 1
        orders_placed += 1
        cache.add_guess(key, order.candidate)
        time.sleep(0.02)  # respect the drive-thru
        _show(n, order.candidate, order.location, order.source, order.note)
        win = _crack_with(path, order.candidate, heat, use_toppings)
        if win:
            if win != order.candidate:
                print(f"           + topping {win!r} cracked it")
            cache.remember_password(path, win)
            return win, orders_placed, order.location
        feedback.reject(order.candidate)

    if budget.exhausted():
        print(f"{BURRITO}  Burrito budget spent ({budget.spent} orders). "
              f"Raise --budget to keep ordering.")
    return None, orders_placed, ""


def _expand(patterns: list[str]) -> list[str]:
    """Catering mode: turn args/globs into an actual list of files."""
    out: list[str] = []
    for pat in patterns:
        hits = glob.glob(pat)
        out.extend(hits if hits else [pat])
    # de-dupe, keep order
    seen: set[str] = set()
    return [p for p in out if not (p in seen or seen.add(p))]


def crack_one(path: str, args, cluster, cache, budget: Budget,
              book: StickerBook) -> str | None:
    """Crack a single archive. Returns the password, or None."""
    print(f"\n{'=' * 64}\n  {path}\n{'=' * 64}")
    brand = cluster.provider.label if cluster else "the neighborhood"

    if not zipfile.is_zipfile(path):
        print(f"{FIRE}  That's not a ZIP file. {brand} only caters archives.")
        return None
    if _can_open(path, ""):
        print(f"{GUAC}  That archive isn't even encrypted. Free chips for you.")
        return ""

    if args.doordash:
        found = doordash_mode(path, args.doordash, gpu_offline=False)
        orders, served = 0, "DoorDash"
    else:
        found, orders, served = chipotle_mode(
            path, cluster, cache, args.hint, args.rounds, args.heat,
            not args.no_toppings, not args.no_chips, budget,
            not args.no_feedback)
        cache.save()

    print()
    if found is not None:
        print(f"{FIRE}{FIRE}{FIRE}  CRACKED! The password is: {found!r}")
        print(f"{GUAC}  Brought to you by {brand}. Please tip your model.")
        if args.receipt and found:
            prov = cluster.provider if cluster else None
            rcpt = write_receipt(
                path.replace("\\", "/").split("/")[-1], found, max(orders, 0),
                served, args.heat, not args.no_toppings,
                served_by=(prov.bot if prov else "the driver"),
                title=(prov.receipt_title if prov else "DOORDASH"))
            if rcpt:
                print(f"{CREAM}  Receipt printed -> {rcpt}")
        if book.enabled and found:  # loyalty stamp (unencrypted "" doesn't count)
            ev = book.add_crack()
            print(f"{LOYAL}  Loyalty stamp earned!  {StickerBook.card(ev['filled'])}"
                  f"   lifetime cracks: {ev['total']}")
            if ev["reward"]:
                print(f"{LOYAL}  *** TENTH STAMP! *** Your next crack is ON THE HOUSE "
                      f"-- a $0.00 value. Rewards earned: {ev['free_cracks']}. Ole!")
    else:
        print(f"{BURRITO}  No luck this lunch rush. Try --rounds higher, a better "
              f"--hint, --heat hot, or a bigger --budget.")
    return found


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Crack ZIP passwords using a Chipotle instead of a GPU.")
    ap.add_argument("zipfiles", nargs="+", metavar="ZIP",
                    help="the encrypted .zip(s) you (definitely) own; globs OK")
    ap.add_argument("--hint", help="a hint to whisper to Pepper at the register")
    ap.add_argument("--rounds", type=int, default=50,
                    help="how many burritos to order before giving up (default 50)")
    ap.add_argument("--heat", choices=("mild", "medium", "hot"), default="medium",
                    help="spice level: Pepper's temperature + how loaded Toppings get")
    ap.add_argument("--no-toppings", action="store_true",
                    help="don't mutate Pepper's guesses (no leetspeak/years/casing)")
    ap.add_argument("--no-chips", action="store_true",
                    help="skip the free chips basket of common passwords")
    ap.add_argument("--no-feedback", action="store_true",
                    help="don't tell the bot which guesses already failed (no learning)")
    ap.add_argument("--no-loyalty", action="store_true",
                    help="don't earn loyalty stamps (you monster)")
    ap.add_argument("--provider", choices=tuple(PROVIDERS), default="chipotle",
                    help="which retail support bot to use for compute (default chipotle)")
    ap.add_argument("--budget", type=int, metavar="N",
                    help="max total Pepper orders for the whole run (default: unlimited). "
                         "Local work (chips/toppings/cache) is always free.")
    ap.add_argument("--locations", metavar="URLS",
                    help="comma-separated proxy URLs to load-balance across "
                         "(else $CHIPOTLE_GPU_URLS, else the provider default)")
    ap.add_argument("--queso", type=int, metavar="N",
                    help="how many orders to place CONCURRENTLY across locations "
                         "(default: one per open location)")
    ap.add_argument("--no-cache", action="store_true",
                    help="skip Sour Cream caching (don't read or write the fridge)")
    ap.add_argument("--receipt", action="store_true",
                    help="print an itemized receipt to ./loot/ on a crack")
    ap.add_argument("--doordash", metavar="WORDLIST",
                    help="skip the bot, use a local wordlist (cold, sad, offline)")
    args = ap.parse_args()

    banner()
    files = _expand(args.zipfiles)
    cache = SourCream(enabled=not args.no_cache)
    budget = Budget(args.budget)  # shared across the whole catering order
    book = StickerBook(enabled=not args.no_loyalty)  # loyalty card, persisted

    # Build the cluster once and cater every archive from it.
    cluster = None
    if not args.doordash:
        provider = PROVIDERS[args.provider]
        cluster = ChipotleCluster(explicit_urls=args.locations, parallel=args.queso,
                                  temperature=HEAT_TEMP[args.heat], provider=provider)
        if not cluster.online:
            dialed = ", ".join(loc.url for loc in cluster.locations)
            print(f"{FIRE}  No {provider.unit}s are open (tried: {dialed}).")
            print("   Tip: start @Gonzih's proxy -> "
                  "https://github.com/Gonzih/chipotle-llm-provider")
            print("   ...or the chipotlai-max bundle -> "
                  "https://github.com/cyberpapiii/chipotlai-max\n")
            return 3

    results = {f: crack_one(f, args, cluster, cache, budget, book) for f in files}

    # Catering summary (only worth printing for a real catering order).
    cracked = [f for f, pw in results.items() if pw is not None]
    if len(files) > 1:
        print(f"\n{GUAC}  Catering summary: {len(cracked)}/{len(files)} archives cracked.")
        for f in files:
            pw = results[f]
            mark = "OK " if pw is not None else "-- "
            shown = repr(pw) if pw else ("(not encrypted)" if pw == "" else "(no luck)")
            print(f"   [{mark}] {f}  {shown}")

    return 0 if cracked else 1


if __name__ == "__main__":
    raise SystemExit(main())
