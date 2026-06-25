"""Render faithful mockups of the gui.py order kiosk for the README."""
from PIL import Image, ImageDraw, ImageFont
import os

# palette (mirrors gui.py exactly)
BG = (24, 20, 18)        # #181412
PANEL = (36, 30, 26)     # #241e1a
OUTBG = (15, 12, 10)     # #0f0c0a
RED = (197, 64, 48)
GREEN = (122, 196, 92)
TXT = (228, 224, 218)
DIM = (140, 132, 124)
YELLOW = (228, 196, 92)
CREAM = (224, 220, 206)
TITLEBAR = (43, 34, 30)

F = "C:/Windows/Fonts/"
def font(name, size): return ImageFont.truetype(F + name, size)
title_f = font("consolab.ttf", 22)
sub_f = font("consola.ttf", 11)
lbl_f = font("consola.ttf", 13)
ent_f = font("segoeui.ttf", 13)
btn_f = font("consolab.ttf", 14)
out_f = font("consola.ttf", 13)
bar_f = font("segoeui.ttf", 12)

W, TB = 760, 32
H = 620 + TB


def draw_kiosk(path_text, hint_text, out_lines, btn_label):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # window chrome
    d.rectangle([0, 0, W, TB], fill=TITLEBAR)
    d.text((10, 8), "GuacTheRipper - Order Kiosk", font=bar_f, fill=DIM)
    d.line([W - 64, 16, W - 52, 16], fill=DIM, width=1)                       # min
    d.rectangle([W - 44, 10, W - 34, 22], outline=DIM)                        # max
    d.line([W - 24, 10, W - 14, 22], fill=DIM, width=1)                       # close
    d.line([W - 14, 10, W - 24, 22], fill=DIM, width=1)

    def center(text, y, fnt, fill):
        w = d.textlength(text, font=fnt)
        d.text(((W - w) / 2, y), text, font=fnt, fill=fill)

    center("GUAC THE RIPPER", TB + 12, title_f, GREEN)
    center("self-order kiosk  -  the GPU is a burrito", TB + 44, sub_f, DIM)

    def label(x, y, t): d.text((x, y), t, font=lbl_f, fill=TXT)

    def entry(x, y, w, t, h=26):
        d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=(70, 60, 54))
        d.text((x + 6, y + 5), t, font=ent_f, fill=TXT if t else DIM)

    def button(x, y, w, t, bg, fg, h=26, f=lbl_f):
        d.rectangle([x, y, x + w, y + h], fill=bg)
        tw = d.textlength(t, font=f)
        d.text((x + (w - tw) / 2, y + (h - 16) / 2), t, font=f, fill=fg)

    def dropdown(x, y, w, t, h=26):
        d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=(70, 60, 54))
        d.text((x + 8, y + 5), t, font=ent_f, fill=TXT)
        ax = x + w - 14
        d.polygon([(ax, y + 10), (ax + 8, y + 10), (ax + 4, y + 16)], fill=DIM)

    def spin(x, y, w, t, h=26):
        d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=(70, 60, 54))
        d.text((x + 8, y + 5), t, font=ent_f, fill=TXT)
        d.polygon([(x + w - 12, y + 6), (x + w - 4, y + 6), (x + w - 8, y + 2)], fill=DIM)
        d.polygon([(x + w - 12, y + 20), (x + w - 4, y + 20), (x + w - 8, y + 24)], fill=DIM)

    def check(x, y, t, on):
        d.rectangle([x, y, x + 16, y + 16], fill=PANEL, outline=(90, 80, 72))
        if on:
            d.line([x + 3, y + 9, x + 7, y + 13], fill=GREEN, width=2)
            d.line([x + 7, y + 13, x + 14, y + 3], fill=GREEN, width=2)
        d.text((x + 22, y + 1), t, font=lbl_f, fill=TXT)
        return x + 22 + d.textlength(t, font=lbl_f) + 22

    y = TB + 78
    label(16, y + 4, "Archive:"); entry(110, y, 470, path_text); button(590, y, 80, "Browse", RED, "white")
    y += 36
    label(16, y + 4, "Hint:"); entry(110, y, 470, hint_text)
    y += 36
    label(16, y + 4, "Heat:"); dropdown(110, y, 110, "medium")
    label(300, y + 4, "Chain:"); dropdown(370, y, 130, "chipotle")
    y += 36
    label(16, y + 4, "Rounds:"); spin(110, y, 80, "50")
    label(300, y + 4, "Combo:"); spin(370, y, 80, "1")
    y += 40
    cx = 16
    for t, on in (("Toppings", True), ("Chips basket", True), ("Receipt", False), ("Stats", True)):
        cx = check(cx, y, t, on)

    # output box
    oy0 = y + 34
    oy1 = H - 66
    d.rectangle([16, oy0, W - 16, oy1], fill=OUTBG, outline=(60, 50, 44))
    ty = oy0 + 8
    for segs in out_lines:
        tx = 26
        for text, color in segs:
            d.text((tx, ty), text, font=out_f, fill=color)
            tx += d.textlength(text, font=out_f)
        ty += 19

    button((W - 200) // 2, H - 54, 200, btn_label, GREEN, (16, 32, 8), h=38, f=btn_f)
    return img


# ---- screenshot 1: ready to order ------------------------------------------
ready = [
    [("Pick an archive, choose your spice, and hit PLACE ORDER.", DIM)],
    [("", TXT)],
    [("(the GPU is a Chipotle. the password is extra guac.)", DIM)],
]
draw_kiosk("C:/Users/sp00nz/secret_backups.zip",
           "dog's name + birth year", ready, "PLACE ORDER").save(
    os.path.join(os.path.dirname(__file__), "gui_order.png"))

# ---- screenshot 2: cracked! ------------------------------------------------
cracked = [
    [("================================================================", DIM)],
    [("  secret_backups.zip", TXT)],
    [("================================================================", DIM)],
    [("[ CPU ]", RED), ("  1/1 Chipotle Processing Unit(s) open via Chipotle", RED)],
    [("[chips]", CREAM), ("  Munching the free chips basket (43 suspects)...", CREAM)],
    [("[guac]", GREEN), ("  Pepper is on the clock. Placing up to 50 orders.", GREEN)],
    [("", TXT)],
    [("  [###...............] ", YELLOW), ("order #3   chipotle @loc1  ", DIM), ("'Buddy'", RED)],
    [("           + topping ", DIM), ("'Buddy2024!'", GREEN), (" cracked it", DIM)],
    [("", TXT)],
    [("*** CRACKED *** ", RED), ("the password is: ", TXT), ("'Buddy2024!'", GREEN)],
    [("[loyal]", CREAM), ("  Loyalty stamp earned!  [****......] 4/10", CREAM)],
]
draw_kiosk("C:/Users/sp00nz/secret_backups.zip",
           "dog's name + birth year", cracked, "PLACE ORDER").save(
    os.path.join(os.path.dirname(__file__), "gui_cracked.png"))

print("wrote gui_order.png and gui_cracked.png")
