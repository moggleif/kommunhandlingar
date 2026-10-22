"""Krav: K36, K37 och K38 i docs/02-KRAV.md, ADR-0057, ADR-0058 och ADR-0059.
Test: tests/test_lokalbehov.py, tests/test_initiativ.py,
tests/test_handlingsplaner.py.

Ett kort per sak, under tidslinjen, som målkorten: åren, vem som står
bakom, det senaste steget, en länk till själva saken när den finns i
poolen, en remsa med årens ikoner och, under "Läs mer", hela historiken
med källans text och en länk till källans sida. Här står också det
tidslinjen och korten delar: årets ikoner, egenskaperna för urvalet och
länken till en källa, som kan vara vilket organs dokument som helst.
"""

from dataclasses import dataclass
from html import escape

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.spar import Slag, Steg
from kommunhandlingar.webbplats.sparikon import ikon

# Namnet, stegen och sakens märken för urvalet utöver faserna.
Sak = tuple[str, list[Steg], list[str]]


@dataclass(frozen=True)
class Vy:
    slag: Slag
    kommun: Kommun
    ar: range

    @classmethod
    def over(cls, slag: Slag, kommun: Kommun, stegen: list[Steg]) -> "Vy":
        aren = [s.ar for s in stegen]
        return cls(slag, kommun, range(min(aren), max(aren) + 1))


def korten(vy: Vy, sakerna: list[Sak]) -> str:
    return (
        f'<h2 id="sakerna">{vy.slag.saker}</h2><div class="malkort">'
        + "".join(kort(vy, nr, s) for nr, s in enumerate(sakerna))
        + "</div>"
    )


def kort(vy: Vy, nr: int, sak: Sak) -> str:
    namn, stegen, _ = sak
    borjan, slut = stegen[0].ar, stegen[-1].ar
    aren = str(borjan) if borjan == slut else f"{borjan}–{slut}"
    senaste = stegen[-1]
    poster = "".join(post(vy, s) for s in reversed(stegen))
    return (
        f'<article id="sak-{nr}" {egenskaper(nr, sak)}>'
        f'<p class="markor"><span>{aren}</span>{avsandare(vy.slag, stegen)}</p>'
        f"<h3>{escape(namn)}</h3>"
        f"<p>Senast: {vy.slag.faser[senaste.fas][1]} {senaste.ar}"
        f"{f' ({escape(senaste.varde)})' if senaste.varde else ''}"
        f"{' <small>tolkad</small>' if senaste.tolkad else ''}</p>"
        f"{planen(vy, stegen)}{remsa(vy, stegen)}"
        f"<details><summary>Läs mer: historiken och källorna, {len(stegen)} steg"
        "</summary>"
        f"<ol>{poster}</ol></details></article>"
    )


def planen(vy: Vy, stegen: list[Steg]) -> str:
    kallorna = [kalla(s.kalla, vy.kommun) for s in stegen if s.fas == vy.slag.planen]
    return "".join(
        f'<p>Planen: <a href="{escape(adress)}">{escape(text)}</a></p>'
        for adress, text in kallorna
    )


def avsandare(slag: Slag, stegen: list[Steg]) -> str:
    return "".join(f"<span>{escape(v)}</span>" for v in avsandarna(slag, stegen))


def avsandarna(slag: Slag, stegen: list[Steg]) -> list[str]:
    return list(
        dict.fromkeys(s.varde for s in stegen if s.fas == slag.avsandare and s.varde)
    )


def remsa(vy: Vy, stegen: list[Steg]) -> str:
    falten = "".join(falt(vy, stegen, a) for a in vy.ar)
    return f'<ol class="remsa" aria-label="År för år">{falten}</ol>'


def falt(vy: Vy, stegen: list[Steg], ar: int) -> str:
    etikett = f'<small><span class="dold">{str(ar)[:2]}</span>{str(ar)[2:]}</small>'
    if not any(s.ar == ar for s in stegen):
        return f'<li class="tom" title="{ar}">{etikett}</li>'
    return f'<li title="{ar}">{arets(vy, stegen, ar)}{etikett}</li>'


def arets(vy: Vy, stegen: list[Steg], ar: int) -> str:
    return "".join(
        ikon(vy.slag, s, kalla(s.kalla, vy.kommun)) for s in stegen if s.ar == ar
    )


# Egenskaperna för målsidans skript: `slag` är faserna saken nått och
# dess märken.
def egenskaper(nr: int, sak: Sak) -> str:
    _, stegen, markor = sak
    slag = " ".join([*dict.fromkeys(s.fas for s in stegen), *markor])
    return f'data-mal="{nr}" data-slag="{escape(slag)}"'


def post(vy: Vy, steg: Steg) -> str:
    adress, text = kalla(steg.kalla, vy.kommun)
    varde = f" ({escape(steg.varde)})" if steg.varde else ""
    tolkad = " <small>tolkad</small>" if steg.tolkad else ""
    return (
        f"<li>{ikon(vy.slag, steg, (adress, text))} <b>{steg.ar}</b> "
        f"{vy.slag.faser[steg.fas][1]}{varde}{tolkad}<br><q>{escape(steg.text)}</q>"
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
