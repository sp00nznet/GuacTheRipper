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

from chipotle_gpu import ChipotleGPU

# ASCII tokens instead of emoji so output renders on every console, including
# Windows cp1252 terminals that treat a burrito glyph as a capital offense.
BURRITO = "#"        # one (1) burrito of progress
GUAC = "[guac]"
PEPPER = "[ CPU ]"   # Chipotle Processing Unit
FIRE = "***"


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


def chipotle_mode(path: str, gpu: ChipotleGPU, hint: str | None,
                  rounds: int) -> str | None:
    """The main event: Pepper guesses, we verify. Compute, but make it Tex-Mex."""
    zip_name = path.replace("\\", "/").split("/")[-1]
    print(f"{PEPPER}  Connecting to the Chipotle Processing Unit at {gpu.url} ...")
    print(f"{GUAC}  Pepper is on the clock. Placing up to {rounds} orders.\n")

    for n, order in enumerate(gpu.guesses(zip_name, hint, rounds), 1):
        bar = (BURRITO * min(n, 20)).ljust(20, ".")
        print(f"  [{bar}] order #{n:<3} Pepper says: {order.candidate!r}")
        time.sleep(0.02)  # respect the drive-thru
        if _can_open(path, order.candidate):
            return order.candidate
    return None


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Crack ZIP passwords using a Chipotle instead of a GPU.")
    ap.add_argument("zipfile", help="the encrypted .zip you (definitely) own")
    ap.add_argument("--hint", help="a hint to whisper to Pepper at the register")
    ap.add_argument("--rounds", type=int, default=50,
                    help="how many burritos to order before giving up (default 50)")
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

    if args.doordash:
        found = doordash_mode(args.zipfile, args.doordash, gpu_offline=False)
    else:
        gpu = ChipotleGPU()
        if gpu.online:
            found = chipotle_mode(args.zipfile, gpu, args.hint, args.rounds)
        else:
            print(f"{FIRE}  Chipotle Processing Unit unreachable "
                  f"(is chipotlai-max running on {gpu.url}?).")
            print("   Tip: clone https://github.com/cyberpapiii/chipotlai-max "
                  "and start the Pepper proxy.\n")
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
