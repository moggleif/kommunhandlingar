"""Krav: K36 i docs/02-KRAV.md, ADR-0057. Test: tests/test_lokalbehov.py.

Ett lokalbehovs fas som ikon. Faserna skiljs åt med form, inte bara
färg; en prioritet bär sin siffra och ett tolkat steg har en streckad ram.
Varje ikon är en länk till källans sida.
"""

from html import escape

from kommunhandlingar.webbplats import lokalbehov
from kommunhandlingar.webbplats.lokalbehov import Steg

DRAG = 'fill="none" stroke="currentColor" stroke-width="1.5"'
# Ikonen och namnet för varje fas i lokalbehov.FASER, i samma ordning.
FASER = dict(
    zip(
        lokalbehov.FASER,
        [
            (f'<circle cx="8" cy="8" r="6" {DRAG}/>', "i nämndens lokalbehov"),
            ('<circle cx="8" cy="8" r="7" fill="currentColor"/>', "prioriterat"),
            (f'<rect x="2" y="2" width="12" height="12" {DRAG}/>', "i lokalplanen"),
            ('<path d="M4 2.5v11l9-5.5z" fill="currentColor"/>', "startbeslut"),
            (
                f'<path d="M8 1.5l6.5 6.5-6.5 6.5-6.5-6.5z" {DRAG}/>'
                '<path d="M8 1.5v13l-6.5-6.5z" fill="currentColor"/>',
                "på gång",
            ),
            (
                '<rect x="1.5" y="1.5" width="13" height="13" rx="3" '
                'fill="currentColor"/><path d="M4.5 8.5l2.5 2.5 4.5-5" '
                'fill="none" stroke="#fff" stroke-width="2"/>',
                "utfört",
            ),
        ],
        strict=True,
    )
)

PRIORITET = " med siffran, eller första bokstaven i källans ord"


def ikon(steg: Steg, lank: str, kalla: str) -> str:
    text = f"{steg.ar} {FASER[steg.fas][1]}"
    text += f" ({steg.varde})" if steg.varde else ""
    text += f": {steg.text} – {kalla}" + (" (tolkad koppling)" * bool(steg.tolkad))
    klass = f"fas {steg.fas}" + (" tolkad" if steg.tolkad else "")
    return (
        f'<a class="{klass}" href="{escape(lank)}" title="{escape(text)}" '
        f'aria-label="{escape(text)}">{bild(steg.fas, siffra(steg))}</a>'
    )


def siffra(steg: Steg) -> str:
    if steg.fas != "prioritet":
        return ""
    tecken = steg.varde if steg.varde.isdigit() else steg.varde[:1].upper()
    return (
        f'<text x="8" y="11.5" text-anchor="middle" font-size="10" '
        f'font-weight="bold" fill="#fff">{escape(tecken)}</text>'
    )


def bild(fas: str, tillagg: str = "") -> str:
    return (
        f'<svg viewBox="0 0 16 16" width="1.3em" height="1.3em" aria-hidden="true">'
        f"{FASER[fas][0]}{tillagg}</svg>"
    )


def teckenforklaring() -> str:
    poster = "".join(
        f'<li><span class="fas {fas}">{bild(fas)}</span> {betyder}'
        f"{PRIORITET * (fas == 'prioritet')}</li>"
        for fas, (_, betyder) in FASER.items()
    )
    poster += (
        '<li><span class="fas lokalbehov tolkad">'
        f"{bild('lokalbehov')}</span> tolkad koppling (streckad ram)</li>"
    )
    return f'<ul class="teckenforklaring">{poster}</ul>'
