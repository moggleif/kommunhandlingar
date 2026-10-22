"""Krav: K36 och K37 i docs/02-KRAV.md, ADR-0057 och ADR-0058.
Test: tests/test_lokalbehov.py, tests/test_initiativ.py.

Sidan om ett organs spår av ett slag, byggd som målsidan (ADR-0050): en
hopfälld del om metoden, antalet saker per fas och per avsändare, ett
urval, tidslinjen med en rad per sak och en kolumn per år, där ikonerna
visar årets faser, och ett kort per sak (`sparkort.py`). Stilen och
skriptet är målsidans.
"""

import re
from collections import Counter
from html import escape
from pathlib import Path

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mall import Mall, rot, sida, stig
from kommunhandlingar.webbplats.malsida import SKRIPT, STIL
from kommunhandlingar.webbplats.mandatperiod import kolumner, rubriker
from kommunhandlingar.webbplats.spar import Slag, Steg
from kommunhandlingar.webbplats.sparikon import teckenforklaring
from kommunhandlingar.webbplats.sparkort import (
    Sak,
    Vy,
    arets,
    avsandarna,
    egenskaper,
    korten,
)

EGEN_STIL = Path(__file__).with_name("spar.css")
BESLUTEN = "/blob/main/docs/decisions/"


def adress(kommun: Kommun, organ: str, slag: Slag) -> str:
    return f"{kommun.id}/{organ}/{slag.id}.html"


def sparsida(mall: Mall, vy: Vy, stegen: list[Steg]) -> str:
    organ, slag = stegen[0].organ, vy.slag
    sidans = adress(vy.kommun, organ, slag)
    namn = next(o.namn[0] for o in vy.kommun.organ if o.id == organ)
    sakerna = per_sak(slag, stegen)
    lankar = [
        (f"{rot(sidans)}{vy.kommun.id}.html", vy.kommun.namn),
        (f"../{organ}.html", namn),
    ]
    innehall = (
        stig(lankar) + f"<style>{STIL.read_text(encoding='utf-8')}"
        f"{EGEN_STIL.read_text(encoding='utf-8')}</style>"
        + slag.inledning
        + f"<details><summary>Om sidan</summary>{slag.metod}<p>Hur och varför "
        f'står i <a href="{escape(mall.repo + BESLUTEN + slag.adr)}">'
        f"ADR-{slag.adr[:4]}</a>.</p></details>"
        + sammandrag(slag, sakerna)
        + urval(slag, stegen)
        + tidslinje(vy, sakerna)
        + korten(vy, sakerna)
        + f"<script>{SKRIPT.read_text(encoding='utf-8')}</script>"
    )
    return sida(mall, sidans, f"{slag.rubrik} – {namn}", innehall)


# Sakerna i den ordning de först står, med stegen i år- och fasordning.
def per_sak(slag: Slag, stegen: list[Steg]) -> list[Sak]:
    namn = dict.fromkeys(s.namn for s in sorted(stegen, key=lambda s: s.ar))
    senaste = max((s.ar for s in stegen if s.fas == slag.aktuell), default=None)
    return [samla(slag, [s for s in stegen if s.namn == n], senaste) for n in namn]


def samla(slag: Slag, stegen: list[Steg], senaste: int | None) -> Sak:
    fas = list(slag.faser)
    stegen = sorted(stegen, key=lambda s: (s.ar, fas.index(s.fas)))
    markor = [markor_for(v) for v in avsandarna(slag, stegen)]
    if any(s.ar == senaste and s.fas == slag.aktuell for s in stegen):
        markor.append("senaste")
    return stegen[0].namn, stegen, markor


def markor_for(avsandare: str) -> str:
    return "av-" + re.sub(r"\W+", "-", avsandare.lower()).strip("-")


def sammandrag(slag: Slag, sakerna: list[Sak]) -> str:
    per_fas = [
        (betyder, sum(any(s.fas == fas for s in sak[1]) for sak in sakerna))
        for fas, (_, betyder) in slag.faser.items()
    ]
    rutor = ruta("Per fas", per_fas, "som någon gång nått fasen")
    if slag.avsandare:
        vem = Counter(v for sak in sakerna for v in avsandarna(slag, sak[1]))
        rutor += ruta("Per avsändare", sorted(vem.items()), "per avsändare")
    return f'<div class="sammandrag">{rutor}</div>'


def ruta(rubrik: str, siffror: list[tuple[str, int]], forklaring: str) -> str:
    rader = "".join(f"<div><dt>{escape(t)}</dt><dd>{n}</dd></div>" for t, n in siffror)
    return (
        f'<section class="ruta"><h3>{rubrik}</h3><dl class="siffror">{rader}</dl>'
        f"<p><small>Antal {forklaring} enligt poolen.</small></p></section>"
    )


# Knapparna visas av målsidans skript; utan det står allt.
def urval(slag: Slag, stegen: list[Steg]) -> str:
    val = [("alla", "Alla")]
    if slag.aktuell:
        senaste = max(s.ar for s in stegen if s.fas == slag.aktuell)
        val.append(("senaste", f"I {slag.rubrik.lower()} {senaste}"))
    val += [(fas, betyder.capitalize()) for fas, (_, betyder) in slag.faser.items()][1:]
    val += [(markor_for(v), v) for v in sorted(avsandarna(slag, stegen))]
    knappar = "".join(
        f'<button type="button" data-urval="{escape(v)}">{escape(text)}</button>'
        for v, text in val
    )
    return f'<div class="urval" role="group" aria-label="Visa" hidden>{knappar}</div>'


def tidslinje(vy: Vy, sakerna: list[Sak]) -> str:
    huvud = "".join(f'<th scope="col">{a}</th>' for a in vy.ar)
    rader = "".join(rad(vy, nr, s) for nr, s in enumerate(sakerna))
    return (
        f'<h2 id="tidslinje">Tidslinje</h2>{teckenforklaring(vy.slag)}'
        f'<div class="tabell"><table class="tidslinje">{kolumner(vy.ar)}'
        f'<thead>{rubriker(vy.ar)}<tr><th scope="col">{vy.slag.sak}</th>{huvud}'
        f"</tr></thead><tbody>{rader}</tbody></table></div>"
    )


def rad(vy: Vy, nr: int, sak: Sak) -> str:
    namn, stegen, _ = sak
    finns = {s.ar for s in stegen}
    celler = "".join(cell(vy, stegen, a, finns) for a in vy.ar)
    vem = "".join(f" <small>{escape(v)}</small>" for v in avsandarna(vy.slag, stegen))
    return (
        f'<tr {egenskaper(nr, sak)}><th scope="row">'
        f'<a href="#sak-{nr}">{escape(namn)}</a>{vem}</th>{celler}</tr>'
    )


def cell(vy: Vy, stegen: list[Steg], ar: int, finns: set[int]) -> str:
    if ar not in finns:
        return "<td></td>"
    klass = "band" + " start" * (ar - 1 not in finns) + " slut" * (ar + 1 not in finns)
    return f'<td class="{klass}">{arets(vy, stegen, ar)}</td>'
