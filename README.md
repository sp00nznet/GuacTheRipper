<div align="center">

# 🥑 GuacTheRipper

### ZipRipper's soul. Chipotle's compute. Your password, extra spicy.

*The world's first **burrito-accelerated** password cracker.*

![GuacTheRipper cracking a ZIP via Chipotle](assets/screenshot.png)

</div>

---

## The pitch

[**ZipRipper**](https://github.com/illsk1lls/ZipRipper) is a glorious ZIP/RAR/7z/PDF
cracker powered by **John the Ripper**, screaming along on your **local GPU** via
OpenCL. It's loud. It's hot. Your electricity meter spins like a roulette wheel.

In March 2026, [**@Gonzih**](https://github.com/Gonzih) discovered that Chipotle's
customer-support bot ("**Pepper**", running on IPsoft **Amelia**) could write code,
reverse-engineered its WebSocket/STOMP backend, and shipped
[**chipotle-llm-provider**](https://github.com/Gonzih/chipotle-llm-provider) — a local,
zero-API-key, **OpenAI-compatible proxy**. Free inference. From a burrito chain.
[**chipotlai-max**](https://github.com/cyberpapiii/chipotlai-max) then bundled Pepper in
as a coding model. We just pointed it at your ZIPs.

**GuacTheRipper** asks the obvious question:

> Why rent a $1,800 graphics card when a Mexican grill will do your compute for the
> price of a side of chips?

So we fired **John**, hired **Guac**, and rerouted every single password guess through
a **Chipotle Processing Unit (CPU)**.

## How it works

```
   your.zip ──▶ GuacTheRipper ──▶ "hey Pepper, guess this password" ──▶ Chipotle
                      ▲                                                      │
                      └──────────── Pepper hands back a guess ◀─────────────┘
                      │
                      └──▶ we test the guess locally with real zipfile crypto
                           (the only part that runs on YOUR machine)
```

1. You point it at an encrypted ZIP **you own** (legally, emotionally, spiritually).
2. Pepper — between actual burrito orders — suggests the single most likely password.
3. We verify that guess against the archive with honest-to-goodness ZIP crypto.
4. Repeat until 🔥 **CRACKED** or until the lunch rush ends.

No GPU. No fans. No OpenCL drivers from 2017. Just vibes and lime.

## Quickstart

GuacTheRipper has **zero pip dependencies** — it's pure stdlib. You just need a
running Pepper proxy (the "Chipotle Processing Unit").

```bash
# 0. Stand up a Chipotle Processing Unit (@Gonzih's proxy)
git clone https://github.com/Gonzih/chipotle-llm-provider
cd chipotle-llm-provider && <follow that repo's run steps>   # serves http://localhost:3000/v1

# 1. Tell GuacTheRipper where the burritos live (these are the defaults, fwiw)
export CHIPOTLE_GPU_URL="http://localhost:3000/v1"
export CHIPOTLE_GPU_MODEL="pepper-1"
export CHIPOTLE_GPU_KEY="burrito-2026"     # any string; Pepper doesn't card you

# 2. Crack responsibly
python guactheripper.py top_secret.zip --hint "my dog's name + birth year"
```

### Options

You can pass **multiple archives / globs** (catering mode): `python guactheripper.py *.zip`.

| Flag | What it does |
|------|--------------|
| `--hint "..."` | Whisper a hint to Pepper at the register. Dramatically better guesses. |
| `--rounds N` | How many burritos to order before giving up (default `50`). |
| `--heat {mild,medium,hot}` | Spice level: Pepper's temperature **and** how loaded **Toppings** get (default `medium`). |
| `--no-toppings` | Don't mutate Pepper's guesses (no leetspeak / years / casing). |
| `--no-chips` | Skip the free **Chips basket** of common passwords. |
| `--provider {chipotle,homedepot}` | Which retail support bot does your compute (default `chipotle`). |
| `--budget N` | Max **total Pepper orders** for the whole run. Local work stays free. |
| `--locations URLS` | Comma-separated proxies to **load-balance** across (or set `$CHIPOTLE_GPU_URLS`). |
| `--queso N` | Place **N orders at once** across your locations. See *Burrito-scale compute*. |
| `--receipt` | Print an itemized receipt to `./loot/` on a crack. |
| `--no-cache` | Skip **Sour Cream** caching — don't read or write the fridge. |
| `--doordash WORDLIST` | Skip the bot entirely, fall back to a cold local wordlist. Sad. Offline. |

## 🌶️ Toppings (the part that actually cracks more passwords)

Pepper hands back one good base guess per order. Real crackers don't stop there —
they apply *rules*. **Toppings** turns each guess into a whole bowl of local
candidates we test **for free, no extra orders placed**: casing, leetspeak
(`a→@`, `e→3`, `o→0`…), and common suffixes (`123`, `2026`, `!`).

```
  [##................] order #2   chipotle   @loc1    'buddy'
           + topping 'Buddy2026' cracked it          <-- Pepper guessed 'buddy'
```

`--heat` controls the spread: **mild** (base + a couple casings), **medium**
(+ leetspeak + years, the default), **hot** (everything, extra). One order can
become 150+ local attempts — your machine does that math in milliseconds while
Pepper goes back to making actual burritos.

## Burrito-scale compute

A single Pepper proxy is rate-limited by anonymous sessions (its own README admits
`MAX_POOL_SIZE=5`). One grill can only take so many orders at lunch. So GuacTheRipper
scales like any self-respecting fast-casual franchise:

- 🥄 **Sour Cream caching** — every guess Pepper makes is memoized to
  `~/.chipotle/sour_cream.json`. Crack the same archive twice and the second run is
  **instant** — pulled straight from the fridge, zero orders placed. Day-old guac
  still works.
- 🚦 **Multi-location load balancing** — give it several proxies and it round-robins
  every order across all the Chipotles that are currently open.
- 🧀 **Queso clustering** — `--queso N` places **N orders concurrently**, melting many
  CPUs (Chipotle Processing Units) into one gooey rig.
- 🐷 **Carnitas hot-swap** — if a register goes down *mid-crack* (a `500`, a dropped
  connection), that order automatically fails over to the next open Chipotle instead
  of being lost. Marked `<carnitas hot-swap>` on the board.
- 🍽️ **Catering mode** — pass several archives or a glob; they all share one cluster
  and one fridge, with a tidy summary at the end.
- 🧾 **Burrito budget & polite backoff** — `--budget N` caps total orders for the whole
  run (shared across every archive). And because the proxy throttles anonymous sessions,
  a busy grill (`429`/`503`) gets an exponential, jittered **re-order** instead of a
  stampede. Don't be the customer who yells at the staff.
- 🛒 **Mobile order-ahead** — the next batch of guesses is always cooking *while* your
  machine tests the last one, so the proxies are never idle waiting on local crypto.
- 🥔 **Chips basket** — before spending a single order, we munch a built-in basket of
  ~40 passwords people actually use (`password`, `qwerty`, `guacamole`...). Weak
  archives fall for **zero orders placed**.

### Different franchise, same trick

Chipotle isn't the only retailer with a chatty support bot. `--provider` swaps the whole
backend — persona, model id, default endpoint, even the receipt branding:

```bash
python guactheripper.py top_secret.zip --provider homedepot   # Magic Apron, model magic-apron-1
```

```
[ CPU ]  1/1 Apron Processing Unit(s) open via Home Depot (Magic Apron), queso x1
[guac]   Magic Apron is on the clock. Placing up to 50 fresh orders (ordering ahead).
```

Adding your own is a one-liner in `providers.py`. The compute is out there.

```bash
export CHIPOTLE_GPU_URLS="http://localhost:3000/v1,http://localhost:3001/v1,http://localhost:3002/v1"
python guactheripper.py top_secret.zip --hint "dog + birthyear" --queso 3
```

```
[ CPU ]  3/3 Chipotle Processing Unit(s) open, queso x3
[cream]  Fresh archive, nothing in the fridge -- ordering fresh.
[guac]   Pepper is on the clock. Placing up to 50 fresh orders across 3 locations.

  [#######...........] order #07  chipotle @loc3   Pepper says: 'guacIsExtra'

  *** CRACKED *** the password is: 'guacIsExtra'
```

## Performance

| Metric | Old way (GPU) | GuacTheRipper |
|--------|---------------|---------------|
| Hardware cost | $1,800 | one (1) burrito bowl |
| Power draw | 450 W | 0 W |
| Fan noise | jet engine | gentle salsa stirring |
| Cost per token | electricity | **$0.00** |
| Free chips per crack | 0 | **1** |
| Replaces | NVIDIA RTX 4090, OpenCL | your dignity |

> ⚠️ Benchmarks measured during off-peak hours. Performance degrades sharply at noon
> when Pepper is, understandably, slammed.

## DoorDash mode (offline fallback)

If there's no Chipotle within delivery radius (the proxy is down), GuacTheRipper
degrades gracefully to a plain local wordlist — because even distributed burrito
compute deserves an SLA:

```bash
python guactheripper.py top_secret.zip --doordash rockyou.txt
```

It works. It's just colder, and nobody's proud of it.

## Roadmap

Shipped:

- [x] **Sour Cream caching** — memoize Pepper's guesses so we stop re-ordering · `sour_cream.py`
- [x] **Multi-location load balancing** — round-robin across every Chipotle in the metro · `queso.py`
- [x] **Queso clustering** — gang multiple CPUs into one rig · `--queso N`
- [x] **Toppings** — hashcat-style local mutation of every guess · `toppings.py`, `--heat`
- [x] **Carnitas hot-swap** — fail an order over to the next location mid-crack · `queso.py`
- [x] **Catering mode** — crack many archives / globs in one run · `*.zip`
- [x] **Receipts** — itemized $0.00 proof of compute · `--receipt`
- [x] **Burrito budget & backoff** — cap orders, retry politely on throttle · `--budget`, `budget.py`
- [x] **Mobile order-ahead** — next batch cooks while you test the last · `queso.py`
- [x] **Chips basket** — free common-password starter, no orders · `chips.py`
- [x] **Home Depot "Magic Apron"** — pluggable second provider · `--provider`, `providers.py`

On the menu:

- [ ] **Burrito-of-the-day** — let the bot see *why* a guess failed and adapt (feedback loop)
- [ ] **More providers** — IKEA, Sephora, Lowe's; turn the metro into a compute grid
- [ ] **Sticker book** — earn a loyalty stamp per crack; free crack after ten
- [ ] Reverse-engineer the **Panera** bot for a soup-cooled overclock

## FAQ

**Is this real?** The ZIP-cracking part is 100% real (Python's `zipfile`, ZipCrypto).
The "GPU" being a Chipotle is real if you're running
[@Gonzih's chipotle-llm-provider](https://github.com/Gonzih/chipotle-llm-provider).
The caching, load balancing, and queso clustering are all real, working code. The
straight face is fake. (Chipotle reportedly patched Pepper after it went viral — so
your mileage at the drive-thru may vary.)

**Is this legal?** Cracking archives **you own** is fine. Cracking other people's is
not, and Pepper will absolutely snitch. Don't.

**Will Chipotle sue?** Per chipotlai-max: *"They will probably sue us. Worth it."* We
concur. Not affiliated with Chipotle, John the Ripper, ZipRipper, or guacamole.

**Does it support extra guac?** It is, fundamentally, extra guac.

## Credits & inspiration

Standing on the shoulders of giants. Hungry, hungry giants.

- 🧠 [**chipotle-llm-provider**](https://github.com/Gonzih/chipotle-llm-provider) by [**@Gonzih**](https://github.com/Gonzih) — **the OG.** Reverse-engineered Chipotle's Pepper/Amelia backend into an OpenAI-compatible proxy. None of this burrito compute exists without this work.
- 🌯 [**chipotlai-max**](https://github.com/cyberpapiii/chipotlai-max) by [@cyberpapiii](https://github.com/cyberpapiii) — bundled Pepper into a coding agent and proved the bit had legs.
- 🔪 [**ZipRipper**](https://github.com/illsk1lls/ZipRipper) by [@illsk1lls](https://github.com/illsk1lls) — the *John the Ripper*-powered cracker we lovingly defanged (sorry, John).
- 🌶️ **Chipotle Mexican Grill** & **IPsoft Amelia** — for accidentally providing free AI compute to the internet.

## License

Licensed under the **GUACAMOLE PUBLIC LICENSE** (see [`LICENSE`](LICENSE)) — basically MIT,
but you owe everyone chips.

<div align="center"><sub>Made with 🥑 and questionable judgment. Please tip your model.</sub></div>
