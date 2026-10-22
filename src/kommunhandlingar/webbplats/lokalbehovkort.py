"""Krav: K36 i docs/02-KRAV.md, ADR-0057. Test: tests/test_lokalbehov.py.

Ett kort per lokalbehov, under tidslinjen, som målkorten: åren, det
senaste steget, en remsa med årens ikoner och hela historiken med källans
text och en länk till källans sida. Här står också det tidslinjen och
korten delar: årets ikoner, egenskaperna för urvalet och länken till en
källa, som kan vara vilket organs dokument som helst.
"""

from html import escape

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.fasikon import FASER, ikon
from kommunhandlingar.webbplats.lokalbehov import Steg

Behov = tuple[str, list[Steg]]


def korten(behoven: list[Behov], ar: range, kommun: Kommun) -> str:
    return (
        '<h2 id="behoven">Behoven</h2><div class="malkort">'
        + "".join(kort(nr, b, ar, kommun) for nr, b in enumerate(behoven))
        + "</div>"
    )


def kort(nr: int, behov: Behov, ar: range, kommun: Kommun) -> str:
    namn, stegen = behov
    borjan, slut = stegen[0].ar, stegen[-1].ar
    aren = str(borjan) if borjan == slut else f"{borjan}–{slut}"
    senaste = max(stegen, key=lambda s: (s.ar, list(FASER).index(s.fas)))
    poster = "".join(post(s, kommun) for s in reversed(stegen))
    antal = f"{len(stegen)} steg"
    return (
        f'<article id="behov-{nr}" {egenskaper(nr, stegen, ar)}>'
        f'<p class="markor"><span>{aren}</span></p><h3>{escape(namn)}</h3>'
        f"<p>Senast: {FASER[senaste.fas][1]} {senaste.ar}"
        f"{f' ({escape(senaste.varde)})' if senaste.varde else ''}</p>"
        f"{remsa(stegen, ar, kommun)}"
        f"<details><summary>Hela historiken, {antal}</summary>"
        f"<ol>{poster}</ol></details></article>"
    )


def remsa(stegen: list[Steg], ar: range, kommun: Kommun) -> str:
    falten = "".join(falt(stegen, a, kommun) for a in ar)
    return f'<ol class="remsa" aria-label="År för år">{falten}</ol>'


def falt(stegen: list[Steg], ar: int, kommun: Kommun) -> str:
    etikett = f'<small><span class="dold">{str(ar)[:2]}</span>{str(ar)[2:]}</small>'
    if not any(s.ar == ar for s in stegen):
        return f'<li class="tom" title="{ar}">{etikett}</li>'
    return f'<li title="{ar}">{arets(stegen, ar, kommun)}{etikett}</li>'


def arets(stegen: list[Steg], ar: int, kommun: Kommun) -> str:
    return "".join(ikon(s, *kalla(s.kalla, kommun)) for s in stegen if s.ar == ar)


# Egenskaperna för målsidans skript: `slag` är faserna behovet nått och
# `aktiv` att det står i nämndens lokalbehov det senaste året.
def egenskaper(nr: int, stegen: list[Steg], ar: range) -> str:
    aktiv = any(s.ar == ar[-1] and s.fas == "lokalbehov" for s in stegen)
    faser = " ".join(dict.fromkeys(s.fas for s in stegen))
    return (
        f'data-mal="{nr}" data-slag="{faser}" data-aktiv="{"ja" if aktiv else "nej"}"'
    )


def post(steg: Steg, kommun: Kommun) -> str:
    adress, text = kalla(steg.kalla, kommun)
    varde = f" ({escape(steg.varde)})" if steg.varde else ""
    tolkad = " <small>tolkad</small>" if steg.tolkad else ""
    return (
        f"<li>{ikon(steg, adress, text)} <b>{steg.ar}</b> "
        f"{FASER[steg.fas][1]}{varde}{tolkad}<br><q>{escape(steg.text)}</q>"
        f'<br>Källa: <a href="{escape(adress)}">{escape(text)}</a></li>'
    )


# Sidan ligger i organets katalog, bredvid de andra organens, och länken
# går till den första av källans sidor.
def kalla(kalla: str, kommun: Kommun) -> tuple[str, str]:
    dokument, sidor = kalla.split("#sida-")
    organ, _, datum, fil = dokument.split("/")
    namn = next(o.namn[0] for o in kommun.organ if o.id == organ)
    adress = f"../{dokument.removesuffix('.md')}.html#sida-{sidor.split('-')[0]}"
    sorten = fil.removesuffix(".md").split("-")[0]
    return adress, f"{namn}, {sorten} {datum}, sida {sidor.replace('-', '–')}"
