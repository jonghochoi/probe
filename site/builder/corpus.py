"""Discover the readable rewrites the site publishes.

The site is the readable layer and nothing else. `analysis/` is not read at
all: a rewrite is written from the paper's own arXiv HTML, so everything the
site needs — title, authors, pillars, tags, links, the card preview — is
declared in the rewrite's own front matter. That keeps the two tracks fully
decoupled; `analysis/` stays a GitHub-read markdown corpus and the site never
has to agree with its schema.

One rewrite per file, `readable/<arxiv-id>.md`. It deliberately does NOT live
under `analysis/<id>/`: that folder's contract is one artifact per paper
(`analysis.md`), and a folder holding only a rewrite is reported as a metadata
failure by `scripts/refresh-analysis-index.py --check`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
READABLE_DIR = REPO_ROOT / "readable"

ID_RE = re.compile(r"^\d{4}\.\d{4,5}$")
UNCLASSIFIED = "미분류"

_FENCE = re.compile(r"^```.*?^```", re.S | re.M)
_SPACE = re.compile(r"\s")

# A `metric:` longer than this stops being a value and becomes a sentence — it
# is printed inside a chip on a card, so it has to survive at one line.
METRIC_MAX = 40

# Pillar display names mirror context/MASTER.md §5. Duplicated from
# `scripts/refresh-analysis-index.py` rather than shared: that script parses the
# analysis corpus and this one does not, so a shared module would exist only to
# hold these ten lines and would couple two tracks with no other contact.
PILLAR_NAMES = {
    "P0": "VLA Datasets & Benchmarks",
    "P1": "Heterogeneous Body/Hand Action Expert",
    "P2": "Structured Multimodal Observation Fusion",
    "P3": "Hand-level System0 Module",
    "P4": "Pretraining for Data-Efficient Adaptation",
    "P5": "World Model",
}
PILLAR_ORDER = ["P0", "P1", "P2", "P3", "P4", "P5", UNCLASSIFIED]
PILLAR_RE = re.compile(r"\bP[0-5]\b")

# Link kind → (emoji, label, sort rank). THE single source for the chips'
# icons, labels and display order — AUTHORING §2-10 deliberately does not
# restate them, and states only the kind names, which is what an author types.
# A rewrite declares `links:` as `kind|url` pairs in any order; this sorts them.
LINK_KINDS = {
    "arxiv": ("📄", "arXiv", 0),
    "code": ("💻", "GitHub", 1),
    "weights": ("📦", "Weights", 2),
    "data": ("📊", "Dataset", 3),
    "site": ("🌐", "Website", 4),
    "demo": ("🎬", "Demo", 5),
}


@dataclass
class Paper:
    stem: str                    # arXiv id — the file name
    path: Path
    front: dict
    body: str

    @property
    def title(self) -> str:
        return self.front.get("title", "") or self.stem

    @property
    def authors(self) -> str:
        return self.front.get("authors", "")

    @property
    def pillars(self) -> list[str]:
        return PILLAR_RE.findall(self.front.get("pillars", ""))

    @property
    def primary(self) -> str:
        return self.pillars[0] if self.pillars else UNCLASSIFIED

    @property
    def tags(self) -> list[str]:
        return frontmatter.as_list(self.front.get("tags", ""))

    @property
    def date(self) -> str:
        d = self.front.get("generated", "")
        return d if d[:1].isdigit() else ""

    @property
    def published(self) -> str:
        return self.front.get("published", "")

    @property
    def links(self) -> list[tuple[str, str, str]]:
        """`[(emoji, label, url)]` in R10's order.

        An unrecognised kind is dropped rather than guessed at — a resource
        chip with the wrong label is worse than a missing one.
        """
        ranked = []
        for item in frontmatter.as_list(self.front.get("links", "")):
            kind, _, url = item.partition("|")
            spec = LINK_KINDS.get(kind.strip().lower())
            if spec and url.strip():
                ranked.append((spec[2], spec[0], spec[1], url.strip()))
        return [(emoji, label, url) for _, emoji, label, url in sorted(ranked)]

    @property
    def metric(self) -> str:
        """The result the paper is remembered by, in one printable fragment.

        `399.5 → 129.2 ms`, `25 Hz 폐루프`. The number is always *in* the
        summary already, but as prose — a card cannot pull it out of a sentence,
        so the rewrite states it once as its own field. Optional: a paper whose
        contribution is not a single number leaves it empty rather than having
        one invented for it.
        """
        return self.front.get("metric", "").strip()

    @property
    def term_count(self) -> int:
        """`terms:` as a number — it is authored as a count and printed as one."""
        try:
            return int(str(self.front.get("terms", "")).strip())
        except ValueError:
            return 0

    @property
    def figure_count(self) -> int:
        return len(frontmatter.as_list(self.front.get("figures", "")))

    @property
    def read_minutes(self) -> int:
        """Minutes of prose, at 500 자/분.

        Fenced blocks are excluded on purpose. Term panels are collapsed until
        the reader opens one, quizzes are answered rather than read, and a
        figure is looked at — counting all three would roughly double the
        number and promise a longer sit than the page actually asks for. What
        is left is the text you read top to bottom, which is what the estimate
        is for.
        """
        prose = _FENCE.sub("", self.body)
        return max(1, round(len(_SPACE.sub("", prose)) / 500))

    @property
    def tagline(self) -> str:
        """One line saying what the paper does, under the body's thesis H1.

        The thesis line is ours — a claim, often a metaphor — and on its own it
        does not tell a reader which paper they are about to read. The page
        header prints the paper's own title; this is the sentence between them.
        """
        return self.front.get("tagline", "")

    @property
    def summary_md(self) -> str:
        """The summary as authored — emphasis and math intact, for the page."""
        return self.front.get("summary", "")

    @property
    def preview(self) -> str:
        """The summary flattened for the landing card and `<meta>`."""
        return _plain(self.front.get("summary", ""))


# ── Math → plain text ───────────────────────────────────────────────────────
# A card preview is clamped plain text: no KaTeX runs there. Deleting the math
# is not an option — a summary routinely *opens* with it (`$`\pi\mathbf{R}^{2}`$
# 는 …`), and dropping that decapitates the sentence. These flatten to a
# readable unicode approximation instead. Not a TeX engine: anything
# unrecognised degrades to its own letters rather than vanishing.
_TEX_SYMBOL = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "kappa": "κ", "lambda": "λ",
    "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ", "sigma": "σ",
    "tau": "τ", "phi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Sigma": "Σ",
    "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω", "ell": "ℓ",
    "times": "×", "cdot": "·", "pm": "±", "mid": "|", "in": "∈",
    "to": "→", "rightarrow": "→", "leftarrow": "←", "Rightarrow": "⇒",
    "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥", "neq": "≠",
    "approx": "≈", "sim": "∼", "infty": "∞", "partial": "∂", "nabla": "∇",
    "sum": "Σ", "prod": "Π", "circ": "∘", "cup": "∪", "cap": "∩",
    "quad": " ", "qquad": " ", ",": " ", ";": " ", " ": " ", "%": "%",
}
# `\mathbb{R}` / `{\rm SO}` / `\operatorname{softmax}` — the wrapper is styling,
# only the letters inside survive a trip through plain text.
_TEX_FONT = re.compile(
    r"\\(?:math(?:bb|cal|rm|bf|it|frak|sf|tt|scr)|text(?:rm|bf|it|sf|tt)?"
    r"|bm|boldsymbol|operatorname\*?)\s*\{([^{}]*)\}"
)
_TEX_FONT_INNER = re.compile(r"\{\s*\\(?:rm|bf|it|sf|tt|cal)\s+([^{}]*)\}")
_TEX_CMD = re.compile(r"\\([A-Za-z]+|[,;% ])")
_SUP = {**{d: c for d, c in zip("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")},
        "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾", "n": "ⁿ", "i": "ⁱ"}
_SUB = {**{d: c for d, c in zip("0123456789", "₀₁₂₃₄₅₆₇₈₉")},
        "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎", ".": "."}


def _script(body: str, table: dict) -> str | None:
    """Unicode super/subscript, or None when a character has no such form."""
    out = []
    for ch in body:
        if ch not in table:
            return None
        out.append(table[ch])
    return "".join(out) if out else None


def tex_to_text(tex: str) -> str:
    """Flatten inline TeX to a readable unicode approximation."""
    # Unwrapping leaves the inner letters butted against whatever preceded the
    # wrapper, and `\pi\mathbf{R}` would then read as one command `\piR`. A NUL
    # holds the boundary open until the command pass is done.
    prev = None
    while prev != tex:                       # nested wrappers: \mathrm{\mathbb{R}}
        prev = tex
        tex = _TEX_FONT.sub("\0" + r"\1", tex)
        tex = _TEX_FONT_INNER.sub("\0" + r"\1", tex)
    tex = _TEX_CMD.sub(lambda m: _TEX_SYMBOL.get(m.group(1), m.group(1)), tex)
    tex = tex.replace("\0", "")

    def script(m: re.Match[str], table: dict) -> str:
        body = m.group(1) or m.group(2)
        return _script(body, table) or f"{m.group(0)[0]}{body}"

    tex = re.sub(r"\^\{([^{}]*)\}|\^(\w)", lambda m: script(m, _SUP), tex)
    tex = re.sub(r"_\{([^{}]*)\}|_(\w)", lambda m: script(m, _SUB), tex)
    return tex.replace("{", "").replace("}", "").replace("\\", "").strip()


def _plain(md: str, limit: int = 240) -> str:
    """Strip markup for a plain-text card preview."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\$`([^`]*)`\$", lambda m: tex_to_text(m.group(1)), text)
    text = re.sub(r"[*_`>#]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[: limit - 1] + "…" if len(text) > limit else text


# ── Discovery ───────────────────────────────────────────────────────────────

def discover() -> tuple[list[Paper], list[str]]:
    """Every `readable/<id>.md`, plus the problems found reading them."""
    papers: list[Paper] = []
    problems: list[str] = []
    if not READABLE_DIR.is_dir():
        return papers, problems

    for path in sorted(READABLE_DIR.glob("*.md")):
        stem = path.stem
        if not ID_RE.match(stem):
            problems.append(f"readable/{path.name}: name is not an arXiv id — skipped")
            continue
        try:
            front, body = frontmatter.parse(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append(f"readable/{path.name}: {exc}")
            continue

        declared = front.get("readable_of", "")
        if declared and declared != stem:
            # A copy-paste that landed a rewrite under the wrong id would
            # otherwise publish one paper's text under another's title.
            problems.append(
                f"readable/{path.name}: readable_of is '{declared}' "
                f"but the file is '{stem}'"
            )
            continue
        for required in ("title", "summary"):
            if not front.get(required):
                problems.append(f"readable/{path.name}: missing `{required}`")

        paper = Paper(stem=stem, path=path, front=front, body=body)
        if len(paper.metric) > METRIC_MAX:
            problems.append(
                f"readable/{path.name}: `metric` is {len(paper.metric)} chars — "
                f"keep it under {METRIC_MAX}, it prints inside a chip"
            )
        papers.append(paper)
    return papers, problems


# ── Neighbours ──────────────────────────────────────────────────────────────

def related(paper: Paper, corpus: list[Paper], limit: int = 3) -> list[Paper]:
    """The nearest few rewrites, by shared tags first and pillars second.

    Tags weigh double because they are the specific claim — two papers tagged
    `flow-matching` are about the same machinery, while two papers sharing P1
    may only both be policies. Papers with nothing in common are dropped rather
    than padded out to `limit`: an unrelated suggestion costs more trust than an
    empty row costs space.
    """
    mine_t, mine_p = set(paper.tags), set(paper.pillars)
    scored = []
    for other in corpus:
        if other.stem == paper.stem:
            continue
        score = 2 * len(mine_t & set(other.tags)) + len(mine_p & set(other.pillars))
        if score:
            scored.append((score, other.date, other))
    scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return [row[2] for row in scored[:limit]]
