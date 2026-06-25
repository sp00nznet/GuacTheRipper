"""
franchise.py  --  The franchise map. Find out which Chipotles are open.

Before you dial, check who's actually serving. `--map` probes every known
provider's default endpoint and prints an open/closed board. And `--providers
all` uses this to dial only the chains that are currently up -- no point queuing
at a Chipotle that's closed for remodeling.
"""

from __future__ import annotations

from chipotle_gpu import ChipotleGPU


def scan(temperature: float = 0.0):
    """Probe every provider's default endpoint. Returns [(provider, online), ...]."""
    from providers import PROVIDERS
    rows = []
    for prov in PROVIDERS.values():
        gpu = ChipotleGPU(url=prov.url, model=prov.model, key=prov.api_key,
                          temperature=temperature, system_prompt=prov.persona)
        rows.append((prov, gpu.online))
    return rows


def open_providers():
    """Just the providers whose proxies are currently reachable."""
    return [prov for prov, up in scan() if up]


def render(rows) -> str:
    lines = ["", "  +======== FRANCHISE MAP ========+"]
    for prov, up in rows:
        mark = "OPEN  " if up else "closed"
        lines.append(f"  [{mark}] {prov.label:<11} {prov.bot:<12} {prov.url}")
    open_n = sum(1 for _, up in rows if up)
    lines.append(f"  --> {open_n}/{len(rows)} locations open for orders.")
    lines.append("  +===============================+")
    return "\n".join(lines)
