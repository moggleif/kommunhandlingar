"""Krav: K36 och K37 i docs/02-KRAV.md, ADR-0057 och ADR-0058.
Test: tests/test_lokalbehov.py, tests/test_initiativ.py.

Ett stegs fas som ikon. Faserna skiljs åt med form, inte bara färg; en
fas med siffra bär den och ett tolkat steg har en streckad ram. Varje
ikon är en länk till källans sida.
"""

from html import escape

from kommunhandlingar.webbplats.spar import Slag, Steg

SIFFRA = " med siffran, eller första bokstaven i källans ord"


def ikon(slag: Slag, steg: Steg, kallan: tuple[str, str]) -> str:
    lank, kalla = kallan
    text = f"{steg.ar} {slag.faser[steg.fas][1]}"
    text += f" ({steg.varde})" if steg.varde else ""
    text += f": {steg.text} – {kalla}" + (" (tolkad koppling)" * bool(steg.tolkad))
    klass = f"fas {steg.fas}" + (" tolkad" if steg.tolkad else "")
    return (
        f'<a class="{klass}" href="{escape(lank)}" title="{escape(text)}" '
        f'aria-label="{escape(text)}">{bild(slag, steg.fas, siffra(slag, steg))}</a>'
    )


def siffra(slag: Slag, steg: Steg) -> str:
    if steg.fas != slag.siffra:
        return ""
    tecken = steg.varde if steg.varde.isdigit() else steg.varde[:1].upper()
    return (
        f'<text x="8" y="11.5" text-anchor="middle" font-size="10" '
        f'font-weight="bold" fill="#fff">{escape(tecken)}</text>'
    )


def bild(slag: Slag, fas: str, tillagg: str = "") -> str:
    return (
        f'<svg viewBox="0 0 16 16" width="1.3em" height="1.3em" aria-hidden="true">'
        f"{slag.faser[fas][0]}{tillagg}</svg>"
    )


def teckenforklaring(slag: Slag) -> str:
    poster = "".join(
        f'<li><span class="fas {fas}">{bild(slag, fas)}</span> {betyder}'
        f"{SIFFRA * (fas == slag.siffra)}</li>"
        for fas, (_, betyder) in slag.faser.items()
    )
    forsta = next(iter(slag.faser))
    poster += (
        f'<li><span class="fas {forsta} tolkad">'
        f"{bild(slag, forsta)}</span> tolkad koppling (streckad ram)</li>"
    )
    return f'<ul class="teckenforklaring">{poster}</ul>'
