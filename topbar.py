"""Top banner with a crime-themed background drawn entirely in code (inline SVG)."""
from __future__ import annotations

import html
import random

import streamlit as st

import config as C
import design as D

_W, _H = 1400, 170


def _fingerprint(cx: float, cy: float) -> str:
    """Concentric broken arcs that read as a fingerprint."""
    rng = random.Random(7)
    parts = []
    for i, r in enumerate(range(8, 96, 6)):
        dash = f"{rng.randint(30, 70)} {rng.randint(5, 12)} {rng.randint(12, 30)} {rng.randint(4, 9)}"
        rot = rng.randint(-14, 14)
        parts.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{r * 0.78:.1f}" ry="{r:.1f}" fill="none" '
            f'stroke="#fff" stroke-opacity="{0.20 if i % 3 else 0.12}" stroke-width="1.6" '
            f'stroke-dasharray="{dash}" transform="rotate({rot} {cx} {cy})"/>'
        )
    return "".join(parts)


def _skyline() -> str:
    """City skyline silhouette along the bottom edge."""
    rng = random.Random(21)
    parts, x = [], 0
    while x < _W:
        w = rng.randint(26, 64)
        h = rng.randint(22, 78)
        parts.append(f'<rect x="{x}" y="{_H - h}" width="{w - 2}" height="{h}" fill="#3A0610" fill-opacity="0.34"/>')
        if h > 46 and rng.random() > 0.35:
            parts.append(
                f'<rect x="{x + w / 2 - 1:.0f}" y="{_H - h - 14}" width="2" height="14" fill="#3A0610" fill-opacity="0.34"/>'
            )
        for wy in range(_H - h + 8, _H - 6, 11):
            for wx in range(x + 6, x + w - 8, 10):
                if rng.random() > 0.72:
                    parts.append(f'<rect x="{wx}" y="{wy}" width="3" height="4" fill="#fff" fill-opacity="0.16"/>')
        x += w
    return "".join(parts)


def _evidence_markers() -> str:
    """Numbered evidence markers, crosshair and map pins."""
    marks = [(610, 46, "1"), (700, 112, "2"), (790, 58, "3"), (905, 120, "4")]
    parts = []
    for x, y, label in marks:
        parts.append(
            f'<g opacity="0.55"><path d="M{x} {y + 22} L{x - 10} {y + 4} A12 12 0 1 1 {x + 10} {y + 4} Z" '
            f'fill="none" stroke="#fff" stroke-width="1.6"/>'
            f'<text x="{x}" y="{y + 1}" text-anchor="middle" font-size="12" font-weight="700" fill="#fff" '
            f'font-family="Inter, Arial, sans-serif">{label}</text></g>'
        )
    cx, cy = 1010, 54
    parts.append(
        f'<g stroke="#fff" stroke-opacity="0.34" stroke-width="1.4" fill="none">'
        f'<circle cx="{cx}" cy="{cy}" r="22"/><circle cx="{cx}" cy="{cy}" r="9"/>'
        f'<line x1="{cx - 34}" y1="{cy}" x2="{cx - 12}" y2="{cy}"/><line x1="{cx + 12}" y1="{cy}" x2="{cx + 34}" y2="{cy}"/>'
        f'<line x1="{cx}" y1="{cy - 34}" x2="{cx}" y2="{cy - 12}"/><line x1="{cx}" y1="{cy + 12}" x2="{cx}" y2="{cy + 34}"/></g>'
    )
    # dotted route between markers
    parts.append(
        '<path d="M610 68 C650 100 670 120 700 130 S760 90 790 78 S870 130 905 140" fill="none" '
        'stroke="#fff" stroke-opacity="0.22" stroke-width="1.4" stroke-dasharray="3 7"/>'
    )
    return "".join(parts)


def _background_svg() -> str:
    return (
        f'<svg class="tb-bg" viewBox="0 0 {_W} {_H}" preserveAspectRatio="xMidYMid slice" '
        f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        '<defs>'
        '<pattern id="tbGrid" width="44" height="44" patternUnits="userSpaceOnUse">'
        '<path d="M44 0H0V44" fill="none" stroke="#fff" stroke-opacity="0.05" stroke-width="1"/></pattern>'
        '<pattern id="tbTape" width="30" height="30" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<rect width="15" height="30" fill="#fff" fill-opacity="0.22"/></pattern>'
        '<radialGradient id="tbGlow" cx="78%" cy="30%" r="55%">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0.13"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
        '</defs>'
        f'<rect width="{_W}" height="{_H}" fill="url(#tbGrid)"/>'
        f'<rect width="{_W}" height="{_H}" fill="url(#tbGlow)"/>'
        f'<rect x="0" y="0" width="{_W}" height="13" fill="url(#tbTape)"/>'
        f'<rect x="0" y="0" width="{_W}" height="13" fill="none" stroke="#fff" stroke-opacity="0.18"/>'
        + _evidence_markers()
        + _fingerprint(1235, 78)
        + _skyline()
        + '</svg>'
    )


def _css() -> str:
    return f"""
<style>
.topbar {{
    position: relative; overflow: hidden; border-radius: 16px;
    background: linear-gradient(105deg, {D.MAROON} 0%, #8A1420 48%, {D.CRIMSON} 100%);
    box-shadow: 0 6px 22px rgba(110, 15, 26, .28);
    min-height: 150px; margin-bottom: .4rem;
}}
.topbar .tb-bg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
.topbar .tb-content {{
    position: relative; z-index: 2; display: flex; align-items: center;
    justify-content: space-between; gap: 1.5rem; padding: 2.1rem 2.2rem 1.7rem 2.2rem;
    flex-wrap: wrap;
}}
.topbar .tb-eyebrow {{
    font-size: .72rem; font-weight: 700; letter-spacing: .24em; text-transform: uppercase;
    color: {D.ROSE_LIGHT}; opacity: .92;
}}
.topbar h1 {{
    font-family: {D.FONT_DISPLAY}; font-size: 2.1rem; font-weight: 700; color: #fff;
    margin: .2rem 0 .15rem 0; padding: 0; line-height: 1.15;
    text-shadow: 0 2px 10px rgba(58, 6, 16, .45);
}}
.topbar .tb-sub {{ color: {D.ROSE_LIGHT}; font-size: .92rem; }}
.topbar .tb-badges {{ display: flex; gap: .7rem; flex-wrap: wrap; }}
.topbar .tb-badge {{
    background: rgba(58, 6, 16, .38); border: 1px solid rgba(255, 255, 255, .28);
    backdrop-filter: blur(3px); border-radius: 12px; padding: .5rem .95rem; min-width: 112px;
}}
.topbar .tb-badge .k {{
    font-size: .64rem; letter-spacing: .14em; text-transform: uppercase; color: {D.ROSE_LIGHT};
}}
.topbar .tb-badge .v {{ font-size: 1.05rem; font-weight: 700; color: #fff; }}
</style>
"""


def render(shown: int, total: int, language: str, month_range: tuple[int, int]) -> None:
    """Draw the top banner."""
    first, last = C.MONTH_LABELS[month_range[0] - 1], C.MONTH_LABELS[month_range[1] - 1]
    period = f"{first} - {last} {C.DATA_YEAR}" if first != last else f"{first} {C.DATA_YEAR}"
    lang_text = "Urdu + English" if language == "All" else language
    badges = [
        ("Period", period),
        ("News shown", f"{shown:,}"),
        ("Language", lang_text),
    ]
    badge_html = "".join(
        f'<div class="tb-badge"><div class="k">{html.escape(k)}</div><div class="v">{html.escape(v)}</div></div>'
        for k, v in badges
    )
    markup = (
        _css()
        + '<div class="topbar">'
        + _background_svg()
        + '<div class="tb-content"><div>'
        + '<div class="tb-eyebrow">Crime &amp; Justice Monitor</div>'
        + f'<h1>{html.escape(C.APP_TITLE)}</h1>'
        + f'<div class="tb-sub">{C.DATA_YEAR} news coverage across {total:,} reports in Urdu and English</div>'
        + '</div>'
        + f'<div class="tb-badges">{badge_html}</div>'
        + '</div></div>'
    )
    st.markdown(markup, unsafe_allow_html=True)
