"""Render the README screenshot: a fake GuacTheRipper run in a terminal.

Mirrors the program's actual output so the joke stays credible: multi-location
load balancing (@loc1/@loc2/@loc3), queso clustering, and a Sour Cream line.
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 792
BG = (24, 20, 18)          # near-black, warm
TITLEBAR = (40, 34, 30)
GREEN = (122, 196, 92)     # guac
RED = (197, 64, 48)        # chipotle red
YELLOW = (228, 196, 92)
CREAMC = (224, 220, 206)   # sour cream
WHITE = (228, 224, 218)
GREY = (140, 132, 124)
DIM = (96, 90, 84)

FONTS = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\CascadiaMono.ttf",
    r"C:\Windows\Fonts\lucon.ttf",
]
def load(size):
    for p in FONTS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

mono = load(19)
small = load(15)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# title bar
d.rectangle([0, 0, W, 38], fill=TITLEBAR)
for i, c in enumerate([(237,106,94), (245,191,79), (98,197,84)]):
    d.ellipse([18 + i*24, 13, 32 + i*24, 27], fill=c)
d.text((W//2 - 150, 10), "guactheripper — burrito@chipotle: ~", font=small, fill=GREY)

y = 56
LH = 23
def line(segs, indent=16):
    global y
    x = indent
    for text, color in segs:
        d.text((x, y), text, font=mono, fill=color)
        x += d.textlength(text, font=mono)
    y += LH

def blank(n=1):
    global y
    y += LH * n

art = [
    "  ____                 _____ _          ____  _",
    " / ___|_   _  __ _  __|_   _| |__   ___|  _ \\(_)_ __  _ __   ___ _ __",
    "| |  _| | | |/ _` |/ __|| | | '_ \\ / _ \\ |_) | | '_ \\| '_ \\ / _ \\ '__|",
    "| |_| | |_| | (_| | (__ | | | | | |  __/  _ <| | |_) | |_) |  __/ |",
    " \\____|\\__,_|\\__,_|\\___||_| |_| |_|\\___|_| \\_\\_| .__/| .__/ \\___|_|",
    "                                              |_|   |_|",
]
for a in art:
    d.text((16, y), a, font=mono, fill=GREEN)
    y += LH
blank()
line([("$ ", DIM),
      ("python guactheripper.py top_secret.zip --hint \"dog + birthyear\" --queso 3", WHITE)])
blank()
line([("[ CPU ]", RED), ("  3/3 Chipotle Processing Unit(s) open, queso x3", RED)])
line([("[cream]", CREAMC), ("  Fresh archive, nothing in the fridge -- ordering fresh.", CREAMC)])
line([("[guac]", GREEN), ("  Pepper is on the clock. Placing up to 50 fresh orders across 3 locations.", GREEN)])
blank()

# (bar fill, order#, location, guess)
orders = [
    (1, "01", "@loc1", "Buddy2014"),
    (2, "02", "@loc2", "rex1998!"),
    (3, "03", "@loc3", "Max2012"),
    (4, "04", "@loc1", "P@ssw0rd"),
    (7, "07", "@loc3", "guacIsExtra"),
]
for fill, num, loc, guess in orders:
    bar = "#" * fill + "." * (18 - fill)
    line([("  [", DIM), (bar, YELLOW), ("] ", DIM),
          (f"order #{num}  ", GREY), ("chipotle ", DIM), (f"{loc:<7}", YELLOW),
          (" Pepper says: ", WHITE), (f"{guess!r}", RED)])
blank()
line([("  *** CRACKED *** ", RED), ("the password is: ", WHITE), ("'guacIsExtra'", GREEN)])
line([("[guac]", GREEN), ("  Brought to you by Chipotle. Please tip your model.", GREEN)])
blank()
line([("─" * 62, DIM)])
line([("  GPU      ", DIM), ("Chipotle x3 (Pepper) ", RED), ("- 0 W - 0 fans - extra guac", GREY)])
line([("  Cost     ", DIM), ("$0.00 / token", GREEN), ("   ", GREY), ("(1 free chip per crack)", GREY)])
line([("  Replaces ", DIM), ("NVIDIA RTX 4090, OpenCL, your dignity", GREY)])

img.save(os.path.join(os.path.dirname(__file__), "screenshot.png"))
print("wrote screenshot.png")
