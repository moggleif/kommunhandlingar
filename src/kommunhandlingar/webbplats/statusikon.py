"""Krav: K27 och K29 i docs/02-KRAV.md, ADR-0045 och ADR-0050.
Test: tests/test_malgrupper.py.

En uppföljnings bedömning som ikon. Bedömningen står i målfilen bredvid
källans formulering, som står kvar i pekrutan. Ikonerna skiljs åt med
form, inte bara färg, och en prognos har en streckad ram. Ett år utan
uppföljning har en punkt för beslutet. Stilen står i `mall.py`, så att
andra sidor kan använda dem.
"""

from html import escape

RING = '<circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor"/>'
DRAG = 'fill="none" stroke="currentColor" stroke-width="2"'
IKONER = {
    "uppnatt": (RING + f'<path d="M4.5 8.5l2.5 2.5 4.5-5" {DRAG}/>', "uppnått"),
    "delvis": (
        RING + '<path d="M8 1.5a6.5 6.5 0 0 0 0 13z" fill="currentColor"/>',
        "delvis uppnått eller på väg",
    ),
    "ej": (RING + f'<path d="M5.5 5.5l5 5M10.5 5.5l-5 5" {DRAG}/>', "ej uppnått"),
    "ingen": (RING, "ingen bedömning i källan"),
}
BESLUTAT = '<circle cx="8" cy="8" r="2.5" fill="currentColor"/>'
FORMER = {**{b: form for b, (form, _) in IKONER.items()}, "beslutat": BESLUTAT}


def ikon(bedomning: str, status: str, prognos: bool) -> str:
    betyder = IKONER[bedomning][1]
    text = f"{betyder}: {status}" if status else betyder
    return bild(bedomning, text + (" (prognos)" if prognos else ""), prognos)


def teckenforklaring() -> str:
    poster = "".join(
        f"<li>{bild(bedomning, betyder, False)} {betyder}</li>"
        for bedomning, (_, betyder) in IKONER.items()
    )
    poster += f"<li>{bild('ingen', 'prognos', True)} prognos (streckad ram)</li>"
    beslutat = bild("beslutat", "beslutat", False)
    poster += f"<li>{beslutat} beslutat, utan uppföljning</li>"
    return f'<ul class="teckenforklaring">{poster}</ul>'


def bild(bedomning: str, text: str, prognos: bool) -> str:
    klass = f"status {bedomning}" + (" prognos" if prognos else "")
    return (
        f'<span class="{klass}" role="img" title="{escape(text)}" '
        f'aria-label="{escape(text)}"><svg viewBox="0 0 16 16" width="1.25em" '
        f'height="1.25em" aria-hidden="true">{FORMER[bedomning]}'
        "</svg></span>"
    )
