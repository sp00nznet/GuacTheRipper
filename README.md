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

| Flag | What it does |
|------|--------------|
| `--hint "..."` | Whisper a hint to Pepper at the register. Dramatically better guesses. |
| `--rounds N` | How many burritos to order before giving up (default `50`). |
| `--locations URLS` | Comma-separated Pepper proxies to **load-balance** across (or set `$CHIPOTLE_GPU_URLS`). |
| `--queso N` | Place **N orders at once** across your Chipotles. See *Burrito-scale compute*. |
| `--no-cache` | Skip **Sour Cream** caching — don't read or write the fridge. |
| `--doordash WORDLIST` | Skip Chipotle entirely, fall back to a cold local wordlist. Sad. Offline. |

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

- [x] **Sour Cream caching** — memoize Pepper's guesses so we stop re-ordering ✅ `sour_cream.py`
- [x] **Multi-location load balancing** — round-robin across every Chipotle in the metro ✅ `queso.py`
- [x] **Queso clustering** — gang multiple CPUs (Chipotle Processing Units) into one rig ✅ `--queso N`
- [ ] **Home Depot "Magic Apron"** backend (`magic-apron-1`) for the rare *DIY brute-force* SKU
- [ ] Reverse-engineer the **Panera** bot for a soup-cooled overclock
- [ ] **Carnitas hot-swap** — fail an order over to the next location mid-crack (currently we just skip duds)

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
