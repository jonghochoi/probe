"""The background cards a comparison may open on — one picture and one line each.

A comparison holds papers a reader may not have the background for, and the
answer is not a paragraph of definitions: a card is a drawing and one plain
line, and a page shows at most three (`comparison/AUTHORING.md` §2-1,
`primer`). The cards live here, drawn once, so every comparison that needs
"행동 청크" shows the same picture of it rather than redefining it in prose.

Each drawing is inline SVG in a 260 × 150 box, coloured only through the
site's tokens so the light and the dark theme are one drawing. A card says
the idea and nothing a paper measured: no number on a card is a result.
Adding a card is a change here and a line in the contract's list; a
comparison names cards by id and cannot define its own.

Standard library only: `comparisons.py` reads the ids at discovery, and
`query.py` imports that.
"""

from __future__ import annotations

import html
import math

_W, _H = 260, 150


def _t(x: float, y: float, s: str, size: float = 12, anchor: str = "start",
       cls: str = "pr-t", weight: int | None = None) -> str:
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" text-anchor="{anchor}" '
            f'class="{cls}"{w}>{html.escape(s)}</text>')


def _arrow(x0: float, y0: float, x1: float, y1: float) -> str:
    """A straight connector ending in a small head — the one arrow every card uses."""
    a = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - 7 * math.cos(a), y1 - 7 * math.sin(a)
    left = (hx + 4 * math.sin(a), hy - 4 * math.cos(a))
    right = (hx - 4 * math.sin(a), hy + 4 * math.cos(a))
    return (f'<path d="M{x0:.1f} {y0:.1f} L{hx:.1f} {hy:.1f}" class="pr-line"/>'
            f'<path d="M{x1:.1f} {y1:.1f} L{left[0]:.1f} {left[1]:.1f} L{right[0]:.1f} {right[1]:.1f} Z" class="pr-head"/>')


def _hand(cx: float, cy: float, fingers: int, s: float = 1.0) -> str:
    """A flat hand: a palm, `fingers` fingers across its top and a thumb."""
    out = [f'<g transform="translate({cx} {cy}) scale({s})">']
    xs = {4: [-15, -5, 5, 15], 3: [-12, 0, 12]}[fingers]
    lens = {4: [30, 36, 33, 26], 3: [32, 34, 32]}[fingers]
    for dx, ln in zip(xs, lens):
        out.append(f'<rect x="{dx - 4.5}" y="{-20 - ln}" width="9" height="{ln + 6}" rx="4.5" class="pr-soft"/>')
    out.append('<rect x="-29" y="-6" width="9" height="28" rx="4.5" transform="rotate(-45 -24 10)" class="pr-soft"/>')
    out.append(f'<rect x="-21" y="-22" width="42" height="44" rx="{12 if fingers == 4 else 5}" class="pr-box"/>')
    out.append("</g>")
    return "".join(out)


def _frame(x: float, y: float, w: float, h: float, cls: str = "pr-box") -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" class="{cls}"/>'


# ── the cards ───────────────────────────────────────────────────────────────

def _vla() -> str:
    return "".join([
        _frame(10, 36, 64, 46, "pr-soft"),
        '<circle cx="42" cy="59" r="11" class="pr-ring"/>',
        _t(42, 98, "카메라 화면", 11.5, "middle", "pr-m"),
        '<rect x="10" y="108" width="64" height="24" rx="12" class="pr-box"/>',
        _t(42, 124, "“컵을 집어”", 10.5, "middle"),
        '<path d="M78 70 H100 M78 120 H92 V82 H100" class="pr-line"/>',
        '<rect x="104" y="48" width="70" height="56" rx="6" class="pr-key"/>',
        _t(139, 81, "VLA", 14, "middle", weight=800),
        _arrow(178, 76, 202, 76),
        '<path d="M214 120 V96 L236 74 L250 84" class="pr-arm"/>',
        '<rect x="204" y="118" width="22" height="10" rx="2" class="pr-soft"/>',
        _t(228, 146, "로봇 행동", 11.5, "middle", "pr-m"),
    ])


def _chunk() -> str:
    out = [_t(14, 40, "한 번에 16개를 뽑아", 12, weight=700)]
    for i in range(16):
        cls = "pr-on" if i < 5 else "pr-soft"
        out.append(f'<rect x="{14 + i * 14.5:.1f}" y="58" width="11" height="26" rx="2" class="{cls}"/>')
    out += [_arrow(14, 98, 96, 98), _t(14, 120, "앞에서부터 차례로 실행", 11.5, cls="pr-m"),
            _t(246, 120, "그동안 다시 보지 않음", 11.5, "end", "pr-m")]
    return "".join(out)


def _denoise() -> str:
    out = [_t(14, 26, "잡음", 11.5, cls="pr-m"), _t(246, 26, "다듬어진 행동", 11.5, "end", "pr-m")]
    jag = [0, 1, -1, 1, -1, 1, 0, -1]
    for k in range(6):
        x0, amp = 18 + k * 41, 1 - k / 5
        pts = []
        for j in range(8):
            yy = 72 + 18 * math.sin(j / 7 * math.pi) * (1 - amp) * -1 + 22 * jag[(j + k) % 8] * amp
            pts.append(f"{x0 + j * 4.6:.1f},{yy:.1f}")
        cls = "pr-curve-on" if k >= 4 else "pr-curve"
        out.append(f'<polyline points="{" ".join(pts)}" class="{cls}"/>')
    out += [_arrow(20, 120, 240, 120), _t(130, 142, "단계마다 조금씩 다듬는다", 11.5, "middle", "pr-m")]
    return "".join(out)


def _fk() -> str:
    x, y, a = 40.0, 120.0, -70.0
    pts = [(x, y)]
    for ln, d in [(48, 0), (38, 32), (28, 30)]:
        a += d
        x += ln * math.cos(math.radians(a))
        y += ln * math.sin(math.radians(a))
        pts.append((x, y))
    out = ['<rect x="22" y="120" width="36" height="14" rx="3" class="pr-soft"/>',
           '<polyline points="' + " ".join(f"{p:.1f},{q:.1f}" for p, q in pts) + '" class="pr-arm"/>']
    for p, q in pts[:-1]:
        out.append(f'<circle cx="{p:.1f}" cy="{q:.1f}" r="6" class="pr-joint"/>')
    out.append(_t(pts[1][0] + 14, pts[1][1] + 16, "관절 각도", 11, cls="pr-m"))
    tx, ty = pts[-1]
    out += [f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="7" class="pr-on"/>',
            _arrow(tx + 12, ty, 188, ty),
            _t(194, ty - 3, "손끝 위치", 13, weight=700),
            _t(150, 140, "각도 셋 → 위치 하나", 12, cls="pr-m")]
    return "".join(out)


def _latent() -> str:
    out = [_t(14, 24, "연속 잠재", 12.5, weight=700), _t(246, 24, "실수 묶음", 11, "end", "pr-m")]
    for i, h in enumerate([14, 22, 8, 30, 18, 26, 11, 20, 33, 9, 24, 16, 29, 12, 21, 27]):
        out.append(f'<rect x="{14 + i * 14.5:.1f}" y="{66 - h}" width="10" height="{h}" rx="2" class="pr-on"/>')
    out += ['<line x1="12" y1="67" x2="248" y2="67" class="pr-line"/>',
            _t(14, 94, "토큰", 12.5, weight=700), _t(246, 94, "단어장 번호", 11, "end", "pr-m")]
    for i, n in enumerate([17, 203, 5, 88, 140, 31, 9, 256]):
        x = 14 + i * 29.5
        out.append(f'<rect x="{x:.1f}" y="104" width="25" height="28" rx="4" class="pr-box"/>')
        out.append(_t(x + 12.5, 123, str(n), 10.5, "middle", "pr-mono"))
    return "".join(out)


def _compress() -> str:
    out = [_t(14, 24, "관절값 22개", 12, weight=700)]
    for i in range(22):
        out.append(f'<rect x="{14 + i * 10.6:.1f}" y="34" width="7" height="22" rx="1.5" class="pr-soft"/>')
    out += [_arrow(130, 62, 130, 92), _t(140, 82, "접는다", 11.5, cls="pr-m"),
            _t(14, 112, "숫자 몇 개", 12, weight=700)]
    for i in range(3):
        out.append(f'<rect x="{100 + i * 22}" y="98" width="16" height="30" rx="2" class="pr-on"/>')
    out.append(_t(246, 140, "몇 개로 접을지가 설계다", 11, "end", "pr-m"))
    return "".join(out)


def _retarget() -> str:
    return "".join([
        _hand(60, 82, 4), _hand(200, 82, 3),
        _arrow(100, 72, 160, 72),
        _t(130, 62, "옮겨 적기", 11.5, "middle", "pr-k", 700),
        _t(60, 132, "사람 손 동작", 12, "middle"),
        _t(200, 132, "다른 손의 관절값", 12, "middle"),
    ])


def _taxel() -> str:
    out = ['<path d="M60 128 V70 Q60 22 105 22 Q150 22 150 70 V128 Z" class="pr-soft"/>']
    hot = {(2, 1), (2, 2), (3, 1), (3, 2), (1, 1)}
    for r in range(6):
        for c in range(5):
            on = (r, c) in hot
            out.append(f'<circle cx="{75 + c * 15}" cy="{46 + r * 14}" r="{4.6 if on else 3.2}" '
                       f'class="{"pr-on" if on else "pr-dot"}"/>')
    out += [_t(166, 64, "손끝의 작은", 11.5), _t(166, 80, "압력 센서 수십 개", 11.5),
            _t(166, 104, "눌린 곳이 진해진다", 11, cls="pr-m")]
    return "".join(out)


def _proprio() -> str:
    return "".join([
        '<path d="M40 128 V92 L92 56 L150 70" class="pr-arm"/>',
        '<circle cx="40" cy="92" r="7" class="pr-joint"/>',
        '<circle cx="92" cy="56" r="7" class="pr-joint"/>',
        '<path d="M80 40 A 18 18 0 0 1 108 46" class="pr-curve-on"/>',
        _t(94, 30, "관절 각도", 11.5, "middle", "pr-k", 700),
        _arrow(150, 70, 150, 100),
        _t(160, 92, "손끝 힘", 11.5, cls="pr-k", weight=700),
        _t(14, 146, "로봇이 제 몸을 스스로 재는 감각", 11.5, cls="pr-m"),
    ])


def _track() -> str:
    out = []
    for k in range(3):
        out.append(_frame(14 + k * 80, 26, 70, 70, "pr-soft"))
    pts = [(30, 70), (40, 60), (52, 52)]
    for k in range(3):
        for j, (x, y) in enumerate(pts):
            xx, yy = x + k * 80 + k * 6, y - k * 6
            out.append(f'<circle cx="{xx:.0f}" cy="{yy:.0f}" r="3.5" class="pr-on"/>')
            if k:
                px_, py_ = x + (k - 1) * 80 + (k - 1) * 6, y - (k - 1) * 6
                out.append(f'<path d="M{px_ + 80:.0f} {py_:.0f} L{xx:.0f} {yy:.0f}" class="pr-trail"/>')
    out.append(_t(14, 122, "같은 점이 프레임마다 어디로 갔는지 잇는다", 11.5, cls="pr-m"))
    return "".join(out)


def _frozen() -> str:
    return "".join([
        '<rect x="20" y="40" width="96" height="56" rx="6" class="pr-ice"/>',
        _t(68, 64, "미리 배운 부분", 12, "middle", weight=700),
        _t(68, 82, "고정", 11.5, "middle", "pr-m"),
        _arrow(120, 68, 140, 68),
        '<rect x="144" y="40" width="96" height="56" rx="6" class="pr-key"/>',
        _t(192, 64, "새로 배우는 부분", 12, "middle", weight=700),
        _t(192, 82, "학습", 11.5, "middle", "pr-m"),
    ])


def _history() -> str:
    out = []
    for k in range(4):
        x = 20 + k * 18
        out.append(f'<rect x="{x}" y="{22 + k * 6}" width="70" height="52" rx="4" class="pr-soft" opacity="{0.45 + k * 0.15:.2f}"/>')
    out += ['<rect x="180" y="40" width="64" height="52" rx="4" class="pr-key"/>',
            _t(212, 71, "지금", 12, "middle", weight=700),
            _arrow(176, 66, 150, 66),
            _t(73, 116, "지난 장면들", 11.5, "middle", "pr-m"),
            _t(212, 116, "지금 장면", 11.5, "middle", "pr-m"),
            _t(130, 142, "어디까지, 어디에 담아 둘까", 11.5, "middle", "pr-k", 700)]
    return "".join(out)


def _edit_obs() -> str:
    return "".join([
        _frame(14, 26, 100, 76, "pr-soft"),
        '<circle cx="50" cy="70" r="10" class="pr-box"/>',
        _t(64, 118, "원래 화면", 11.5, "middle", "pr-m"),
        _arrow(120, 64, 140, 64),
        _frame(146, 26, 100, 76, "pr-soft"),
        '<circle cx="182" cy="70" r="10" class="pr-box"/>',
        '<path d="M160 92 Q176 74 182 70" class="pr-trail"/>',
        '<rect x="208" y="34" width="30" height="26" rx="3" class="pr-mask"/>',
        _t(196, 118, "더하고 지운 화면", 11.5, "middle", "pr-m"),
        _t(14, 142, "선을 그려 넣고, 필요 없는 곳은 가린다", 11.5, cls="pr-m"),
    ])


def _speedup() -> str:
    out = [_t(14, 30, "보통 속도", 11.5, cls="pr-m")]
    for i in range(10):
        out.append(f'<rect x="{80 + i * 16}" y="18" width="12" height="18" rx="2" class="pr-soft"/>')
    out.append(_t(14, 74, "빠르게", 11.5, cls="pr-m"))
    for i in range(5):
        out.append(f'<rect x="{80 + i * 16}" y="62" width="12" height="18" rx="2" class="pr-on"/>')
    out += [_arrow(100, 40, 100, 58),
            _t(14, 112, "같은 동작을 더 짧은 시간에 실행한다", 11.5, cls="pr-m"),
            _t(14, 132, "어디서 빨라지게 할지가 갈림이다", 11, cls="pr-m")]
    return "".join(out)


# id → (title, one line, drawing). The line is what the card says in words,
# 30 characters or fewer and free of Latin script, so it reads before any term
# on the page is explained.
PRIMERS: dict[str, tuple[str, str, object]] = {
    "vla": ("VLA", "카메라 화면과 지시문을 받아 로봇 행동을 내는 모델", _vla),
    "chunk": ("행동 청크", "행동 여러 개를 한 번에 뽑아 차례로 실행하는 묶음", _chunk),
    "denoise": ("디노이징", "잡음에서 시작해 단계마다 다듬어 행동을 만든다", _denoise),
    "fk": ("순기구학", "관절 각도를 넣으면 손끝 위치가 계산된다", _fk),
    "latent": ("잠재와 토큰", "같은 동작을 실수 묶음으로, 또는 단어장 번호로 적는다", _latent),
    "compress": ("잠재 차원", "많은 관절값을 숫자 몇 개로 접는다", _compress),
    "retarget": ("리타게팅", "한 손의 동작을 다른 손의 관절값으로 옮겨 적기", _retarget),
    "taxel": ("손끝 촉각", "손끝에 박힌 압력 센서가 눌린 곳을 알려 준다", _taxel),
    "proprio": ("고유수용", "로봇이 자기 관절 각도와 힘을 스스로 잰다", _proprio),
    "track": ("점 추적", "영상 속 같은 점이 어디로 움직였는지 잇는다", _track),
    "frozen": ("얼린 인코더", "미리 배운 부분은 고정하고 나머지만 학습한다", _frozen),
    "history": ("이력", "지난 장면을 얼마나, 어디에 담아 두는가", _history),
    "edit-obs": ("관찰 편집", "정책에 넣기 전에 화면에 그려 넣거나 가린다", _edit_obs),
    "speedup": ("실행 속도", "같은 동작을 더 짧은 시간에 해내게 한다", _speedup),
}

PRIMER_MAX = 3


def card(pid: str) -> str:
    """One card as markup — the drawing over its title and line."""
    title, line, draw = PRIMERS[pid]
    return (f'<figure class="primer"><svg viewBox="0 0 {_W} {_H}" role="img" '
            f'aria-label="{html.escape(title)} — {html.escape(line)}">{draw()}</svg>'
            f'<figcaption><b>{html.escape(title)}</b>{html.escape(line)}</figcaption></figure>')
