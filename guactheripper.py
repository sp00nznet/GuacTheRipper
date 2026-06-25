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
import sys
import time
import zipfile

from queso import ChipotleCluster
from sour_cream import SourCream

# ASCII tokens instead of emoji so output renders on every console, including
# Windows cp1252 terminals that treat a burrito glyph as a capital offense.
BURRITO = "#"          # one (1) burrito of progress
GUAC = "[guac]"
PEPPER = "[ CPU ]"     # Chipotle Processing Unit
FIRE = "***"
CREAM = "[cream]"      # sour cream cache


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


def _attempt(path: str, candidate: str, n: int, label: str, source: str) -> bool:
    """Show one order on the board and test it. Returns True on a crack."""
    bar = (BURRITO * min(n, 18)).ljust(18, ".")
    tag = f"{source:<11}"
    print(f"  [{bar}] order #{n:<3} {tag}{label:<8} {candidate!r}")
    return _can_open(path, candidate)


def chipotle_mode(path: str, cluster: ChipotleCluster, cache: SourCream,
                  hint: str | None, rounds: int) -> str | None:
    """The main event: Pepper guesses, we verify. Compute, but make it Tex-Mex."""
    zip_name = path.replace("\\", "/").split("/")[-1]
    key = f"{zip_name}|{hint or ''}"
    tried: set[str] = set()

    # 1. Sour Cream: have we already cracked THIS exact archive? Instant guac.
    remembered = cache.remembered_password(path)
    if remembered and _can_open(path, remembered):
        print(f"{CREAM}  We've cracked this archive before. "
              f"Pulling the password from the fridge -- zero orders placed.")
        return remembered

    print(f"{PEPPER}  {cluster.status()}")

    # 2. Sour Cream: replay every guess Pepper has ever made for this job, cold.
    leftovers = cache.cached_guesses(key)
    if leftovers:
        print(f"{CREAM}  Replaying {len(leftovers)} cached guess(es) before ordering fresh.")
    elif cache.enabled:
        print(f"{CREAM}  Fresh archive, nothing in the fridge -- ordering fresh.")
    n = 0
    for candidate in leftovers:
        if candidate in tried:
            continue
        tried.add(candidate)
        n += 1
        if _attempt(path, candidate, n, "leftovers", "sour-cream"):
            cache.remember_password(path, candidate)
            return candidate

    # 3. Fresh orders, load-balanced + queso-clustered across open locations.
    print(f"{GUAC}  Pepper is on the clock. Placing up to {rounds} fresh orders.\n")
    for order in cluster.guesses(zip_name, hint, rounds, exclude=tried):
        tried.add(order.candidate)
        n += 1
        cache.add_guess(key, order.candidate)
        time.sleep(0.02)  # respect the drive-thru
        if _attempt(path, order.candidate, n, order.location, order.source):
            cache.remember_password(path, order.candidate)
            return order.candidate
    return None


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Crack ZIP passwords using a Chipotle instead of a GPU.")
    ap.add_argument("zipfile", help="the encrypted .zip you (definitely) own")
    ap.add_argument("--hint", help="a hint to whisper to Pepper at the register")
    ap.add_argument("--rounds", type=int, default=50,
                    help="how many burritos to order before giving up (default 50)")
    ap.add_argument("--locations", metavar="URLS",
                    help="comma-separated Pepper proxy URLs to load-balance across "
                         "(else $CHIPOTLE_GPU_URLS, else a single location)")
    ap.add_argument("--queso", type=int, metavar="N",
                    help="how many orders to place CONCURRENTLY across locations "
                         "(default: one per open Chipotle)")
    ap.add_argument("--no-cache", action="store_true",
                    help="skip Sour Cream caching (don't read or write the fridge)")
    ap.add_argument("--doordash", metavar="WORDLIST",
                    help="skip Chipotle, use a local wordlist (cold, sad, offline)")
    args = ap.parse_args()

    banner()

    if not zipfile.is_zipfile(args.zipfile):
        print(f"{FIRE}  That's not a ZIP file. Pepper only caters archives.")
        return 2

    # Already unencrypted? Don't waste guac.
    if _can_open(args.zipfile, ""):
        print(f"{GUAC}  That archive isn't even encrypted. Free chips for you.")
        return 0

    found: str | None = None
    cache = SourCream(enabled=not args.no_cache)

    if args.doordash:
        found = doordash_mode(args.zipfile, args.doordash, gpu_offline=False)
    else:
        cluster = ChipotleCluster(explicit_urls=args.locations, parallel=args.queso)
        if cluster.online:
            found = chipotle_mode(args.zipfile, cluster, cache, args.hint, args.rounds)
            cache.save()
        else:
            dialed = ", ".join(loc.url for loc in cluster.locations)
            print(f"{FIRE}  No Chipotle Processing Units are open (tried: {dialed}).")
            print("   Tip: start @Gonzih's proxy -> "
                  "https://github.com/Gonzih/chipotle-llm-provider")
            print("   ...or the chipotlai-max bundle -> "
                  "https://github.com/cyberpapiii/chipotlai-max\n")
            return 3

    print()
    if found is not None:
        print(f"{FIRE}{FIRE}{FIRE}  CRACKED! The password is: {found!r}")
        print(f"{GUAC}  Brought to you by Chipotle. Please tip your model.")
        return 0

    print(f"{BURRITO}  No luck this lunch rush. Try --rounds higher or a better --hint.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
