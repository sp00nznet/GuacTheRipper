"""
gui.py  --  The GuacTheRipper order kiosk. A small optional desktop GUI.

Like a self-order screen at the counter: pick your archive, choose your spice,
pick a chain, and hit PLACE ORDER. The crack runs in the background and the
register output streams into the receipt window.

Pure stdlib Tkinter, so there's nothing to install. Launch it with:

    python guactheripper.py --gui
"""

from __future__ import annotations

import argparse
import queue
import sys
import threading

# Chipotle-ish palette
BG = "#181412"
PANEL = "#241e1a"
RED = "#c54030"
GREEN = "#7ac45c"
TXT = "#e4e0da"
DIM = "#8c847c"


def _make_args(path, hint, heat, provider, rounds, combo,
               toppings, chips, receipt, stats):
    """Build the same Namespace the CLI would, for crack_one()."""
    return argparse.Namespace(
        zipfiles=[path], hint=hint or None, rounds=int(rounds), heat=heat,
        no_toppings=not toppings, no_chips=not chips, no_feedback=False,
        no_loyalty=False, provider=provider, providers=None, combo=int(combo),
        stats=stats, budget=None, locations=None, queso=None, no_cache=False,
        receipt=receipt, doordash=None, gui=True, franchise_map=False,
        contract=None, salsa=None,
    )


class _StreamToQueue:
    """A stdout stand-in that ships writes to the GUI thread via a queue."""

    def __init__(self, q): self.q = q
    def write(self, s): self.q.put(s)
    def flush(self): pass


def launch() -> int:
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, scrolledtext
    except Exception as e:  # noqa: BLE001 - headless box, no Tk
        print(f"GUI unavailable (no Tkinter here): {e}")
        print("Use the command line instead: python guactheripper.py your.zip")
        return 1

    # Imported here so `import gui` stays cheap and avoids import cycles.
    import guactheripper as core
    from budget import Budget
    from providers import PROVIDERS
    from salsa import load_salsa
    from sour_cream import SourCream
    from stats import Stats
    from sticker_book import StickerBook
    from queso import ChipotleCluster

    root = tk.Tk()
    root.title("GuacTheRipper - Order Kiosk")
    root.configure(bg=BG)
    root.geometry("760x620")

    out_q: queue.Queue = queue.Queue()

    tk.Label(root, text="GUAC THE RIPPER", bg=BG, fg=GREEN,
             font=("Consolas", 22, "bold")).pack(pady=(12, 0))
    tk.Label(root, text="self-order kiosk  -  the GPU is a burrito", bg=BG,
             fg=DIM, font=("Consolas", 10)).pack()

    form = tk.Frame(root, bg=BG)
    form.pack(fill="x", padx=16, pady=10)

    # --- archive picker ------------------------------------------------------
    path_var = tk.StringVar()
    tk.Label(form, text="Archive:", bg=BG, fg=TXT, font=("Consolas", 10)).grid(
        row=0, column=0, sticky="w")
    tk.Entry(form, textvariable=path_var, width=52, bg=PANEL, fg=TXT,
             insertbackground=TXT).grid(row=0, column=1, columnspan=3, sticky="we", padx=4)

    def browse():
        p = filedialog.askopenfilename(
            title="Pick an encrypted .zip you own",
            filetypes=[("Zip archives", "*.zip"), ("All files", "*.*")])
        if p:
            path_var.set(p)

    tk.Button(form, text="Browse", command=browse, bg=RED, fg="white",
              relief="flat").grid(row=0, column=4, padx=4)

    # --- hint ----------------------------------------------------------------
    hint_var = tk.StringVar()
    tk.Label(form, text="Hint:", bg=BG, fg=TXT, font=("Consolas", 10)).grid(
        row=1, column=0, sticky="w", pady=4)
    tk.Entry(form, textvariable=hint_var, width=52, bg=PANEL, fg=TXT,
             insertbackground=TXT).grid(row=1, column=1, columnspan=3, sticky="we", padx=4)

    # --- spice / chain / counts ---------------------------------------------
    heat_var = tk.StringVar(value="medium")
    prov_var = tk.StringVar(value="chipotle")
    rounds_var = tk.StringVar(value="50")
    combo_var = tk.StringVar(value="1")

    tk.Label(form, text="Heat:", bg=BG, fg=TXT, font=("Consolas", 10)).grid(
        row=2, column=0, sticky="w", pady=4)
    ttk.OptionMenu(form, heat_var, "medium", "mild", "medium", "hot").grid(
        row=2, column=1, sticky="w")
    tk.Label(form, text="Chain:", bg=BG, fg=TXT, font=("Consolas", 10)).grid(
        row=2, column=2, sticky="e", pady=4)
    ttk.OptionMenu(form, prov_var, "chipotle", *PROVIDERS.keys()).grid(
        row=2, column=3, sticky="w")

    tk.Label(form, text="Rounds:", bg=BG, fg=TXT, font=("Consolas", 10)).grid(
        row=3, column=0, sticky="w", pady=4)
    tk.Spinbox(form, from_=1, to=9999, textvariable=rounds_var, width=8,
               bg=PANEL, fg=TXT, insertbackground=TXT).grid(row=3, column=1, sticky="w")
    tk.Label(form, text="Combo:", bg=BG, fg=TXT, font=("Consolas", 10)).grid(
        row=3, column=2, sticky="e", pady=4)
    tk.Spinbox(form, from_=1, to=20, textvariable=combo_var, width=8,
               bg=PANEL, fg=TXT, insertbackground=TXT).grid(row=3, column=3, sticky="w")

    # --- toggles -------------------------------------------------------------
    top_var = tk.BooleanVar(value=True)
    chip_var = tk.BooleanVar(value=True)
    rcpt_var = tk.BooleanVar(value=False)
    stat_var = tk.BooleanVar(value=True)
    toggles = tk.Frame(root, bg=BG)
    toggles.pack(fill="x", padx=16)
    for txt, var in (("Toppings", top_var), ("Chips basket", chip_var),
                     ("Receipt", rcpt_var), ("Stats", stat_var)):
        tk.Checkbutton(toggles, text=txt, variable=var, bg=BG, fg=TXT,
                       selectcolor=PANEL, activebackground=BG, activeforeground=GREEN,
                       font=("Consolas", 10)).pack(side="left", padx=6)

    # --- output --------------------------------------------------------------
    out = scrolledtext.ScrolledText(root, bg="#0f0c0a", fg=TXT, insertbackground=TXT,
                                    font=("Consolas", 10), height=16, wrap="word")
    out.pack(fill="both", expand=True, padx=16, pady=10)
    out.insert("end", "Pick an archive and hit PLACE ORDER.\n")

    order_btn = tk.Button(root, text="PLACE ORDER", bg=GREEN, fg="#102008",
                          font=("Consolas", 13, "bold"), relief="flat")
    order_btn.pack(pady=(0, 12), ipadx=10, ipady=4)

    def worker(args):
        old = sys.stdout
        sys.stdout = _StreamToQueue(out_q)
        try:
            cache = SourCream(enabled=True)
            budget = Budget(None)
            book = StickerBook(enabled=True)
            st = Stats()
            cluster = ChipotleCluster(provider=PROVIDERS[args.provider],
                                      temperature=core.HEAT_TEMP[args.heat])
            if not cluster.online:
                dialed = ", ".join(loc.url for loc in cluster.locations)
                print(f"No {cluster.provider.unit}s are open (tried: {dialed}).")
                print("Start @Gonzih's proxy: https://github.com/Gonzih/chipotle-llm-provider")
                return
            core.crack_one(args.zipfiles[0], args, cluster, cache, budget,
                           book, st, load_salsa(None))
            if args.stats:
                print(st.render(orders=st.orders, rounds=args.rounds))
        except Exception as e:  # noqa: BLE001 - surface any error to the kiosk
            print(f"\n[error] {e}")
        finally:
            sys.stdout = old
            out_q.put(("__DONE__",))

    def place_order():
        path = path_var.get().strip()
        if not path:
            out.insert("end", "\n[!] Pick an archive first.\n")
            out.see("end")
            return
        args = _make_args(path, hint_var.get(), heat_var.get(), prov_var.get(),
                          rounds_var.get(), combo_var.get(), top_var.get(),
                          chip_var.get(), rcpt_var.get(), stat_var.get())
        out.delete("1.0", "end")
        order_btn.config(state="disabled", text="ORDERING...")
        threading.Thread(target=worker, args=(args,), daemon=True).start()

    def pump():
        try:
            while True:
                item = out_q.get_nowait()
                if isinstance(item, tuple) and item and item[0] == "__DONE__":
                    order_btn.config(state="normal", text="PLACE ORDER")
                else:
                    out.insert("end", item)
                    out.see("end")
        except queue.Empty:
            pass
        root.after(60, pump)

    order_btn.config(command=place_order)
    root.after(60, pump)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(launch())
