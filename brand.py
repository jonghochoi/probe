"""
probe/brand.py
==============
PROBE brand identity — ASCII art, sigils, and color constants.

Project story:
    In StarCraft, a Probe is the Protoss scout-worker — a small psionic
    drone warped out ahead of the colony to survey unmapped terrain,
    mark veins of minerals and vespene, and ping its findings back to
    the Nexus. It does not fight. It finds.

    This project carries the same mandate.

    The literature is an unmapped field. Every day, 50 to 100 new
    papers drop on arXiv cs.RO and cs.LG. Somewhere in that stream
    are the three or four that would change what you train next week
    — and the researcher who reads them all burns the hours that
    should have gone into the experiment itself.

    PROBE warps out ahead.
    It watches the authors you care about, follows citation chains
    out from your pinned literature, filters the noise, and pings
    back a short decision-grade Scouting Report: *if this paper is
    right, here is what you change in Isaac Lab next week.*

    The scout does not decide. The researcher still judges, still
    discards, still chooses the direction. But the scout covers
    ground that no human has the hours to cover — and the colony
    stops mining the same vein twice.

    My life for Aiur.

Usage:
    from brand import print_banner, SIGIL

    print_banner()
    print(f"{SIGIL} Scouting Report ready for week 2026-W17")
"""

# ── ANSI color codes ──────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
ITALIC  = "\033[3m"
WHITE   = "\033[97m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
RED     = "\033[91m"
CYAN    = "\033[96m"

# ── Claude signature orange ───────────────────────────────────────────
#
# Claude's house color is a warm burnt orange (~#CC785C / #D97757).
# Truecolor rendering first, with a 256-color fallback for older shells.
#
ORANGE       = "\033[38;2;217;119;87m"   # #D97757 — Claude brand orange
ORANGE_DEEP  = "\033[38;2;204;120;92m"   # #CC785C — deeper burnt orange
ORANGE_SOFT  = "\033[38;2;234;162;122m"  # #EAA27A — soft amber
ORANGE_256   = "\033[38;5;208m"          # fallback for 256-color terminals

# ── Inline sigil — use in log lines and CLI prompts ───────────────────
#
#   [PRB]  (bold orange)
#
SIGIL = f"{ORANGE}{BOLD}[PRB]{RESET}"

# ── Full startup banner ───────────────────────────────────────────────
#
#  Visual language:
#    · Ping rings          — the probe's psionic sensor pulse (( · ))
#    · Angular frame       — Protoss crystalline geometry (◆ corners, ━ ┃ edges)
#    · Central probe sigil — ◈ the scout-drone's warp core
#    · Reconnaissance flow — arXiv stream → probe filter → scouting report
#
#  Recon flow diagram:
#
#     ░░░░░░░░░░░░░░░░░░░░░    ← daily arXiv stream  (50–100 / day)
#          │    │    │
#          ▼    ▼    ▼
#           P R O B E          ← author watch · citation graph · anti-topic filter
#               │
#               ▼
#      📡 Scouting Report     ← 3–5 papers · "change what you train next"
#
BANNER = f"""{ORANGE}{BOLD}
  {RESET}{ORANGE}◆━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━◆{BOLD}
  ┃                                            ┃
  ┃          {WHITE}{BOLD}   ◈   P R O B E   ◈             {ORANGE}{BOLD} ┃
  ┃                                            ┃
  ┃  {RESET}{YELLOW}It doesn't read papers. It scouts them.  {ORANGE}{BOLD} ┃
  ┃                                            ┃
  {RESET}{ORANGE}◆━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━◆{BOLD}
{RESET}"""

# ── Recon flow diagram (standalone) ───────────────────────────────────
FLOW = (
    f"{DIM}{ORANGE_SOFT}  ░░░░░░░░░░░░░░░░░░░░░░░{RESET}  "
    f"{DIM}← daily arXiv stream (50–100/day){RESET}\n"
    f"{ORANGE}        │    │    │{RESET}\n"
    f"{ORANGE}        ▼    ▼    ▼{RESET}\n"
    f"         {WHITE}{BOLD}P R O B E{RESET}   "
    f"      {DIM}← author watch · citations · filter{RESET}\n"
    f"{ORANGE}             │{RESET}\n"
    f"{ORANGE}             ▼{RESET}\n"
    f"    {ORANGE}{BOLD}📡 Scouting Report{RESET}   "
    f"  {DIM}← 3–5 papers · decision-grade{RESET}\n"
)

# ── Version ───────────────────────────────────────────────────────────
VERSION = "0.1.0"
VERSION_STRING = f"{ORANGE}{BOLD}PROBE{RESET} {DIM}v{VERSION}{RESET}"


# ── Public functions ──────────────────────────────────────────────────

def print_banner() -> None:
    """Print the full PROBE startup banner."""
    print(BANNER)


def print_flow() -> None:
    """Print the reconnaissance flow diagram."""
    print(FLOW)


def rule(title: str = "", width: int = 54) -> str:
    """Return a styled horizontal rule with an optional centered title."""
    if title:
        pad = (width - len(title) - 2) // 2
        line = f"{'─' * pad} {title} {'─' * (width - len(title) - 2 - pad)}"
    else:
        line = "─" * width
    return f"{ORANGE}{line}{RESET}"


def log(msg: str, level: str = "info") -> str:
    """
    Return a formatted log prefix line.

    Parameters
    ----------
    msg   : message text
    level : "info" | "ok" | "warn" | "error"
    """
    icons = {
        "info":  f"{ORANGE}[PRB]{RESET}",
        "ok":    f"{GREEN}[PRB]{RESET}",
        "warn":  f"{YELLOW}[PRB]{RESET}",
        "error": f"{RED}[PRB]{RESET}",
    }
    prefix = icons.get(level, icons["info"])
    return f"{prefix} {msg}"


if __name__ == "__main__":
    print_banner()
    print()
    print_flow()
    print()
    print(f"  Sigil   : {SIGIL}")
    print(f"  Version : {VERSION_STRING}")
    print()
    print(rule("Scouting Complete"))
    print()
    print(log("Scanned 87 new arXiv submissions this week", "info"))
    print(log("4 papers pass Q#/H# relevance threshold", "ok"))
    print(log("Anti-topic filter caught 12 mobile-manipulation papers", "warn"))
    print(log("semantic-scholar-mcp timed out — retry scheduled", "error"))
