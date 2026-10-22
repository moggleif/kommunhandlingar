"""Krav: K36 i docs/02-KRAV.md, ADR-0057. Test: tests/test_lokalbehov.py.

Sidan om ett organs lokalbehov, byggd som målsidan (ADR-0050): en
hopfälld del om metoden, antalet behov per fas, ett urval, tidslinjen med
en rad per behov och en kolumn per år, där ikonerna visar årets faser, och
ett kort per behov (`lokalbehovkort.py`). Stilen och skriptet är målsidans.
"""

from html import escape
from pathlib import Path

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.fasikon import FASER, teckenforklaring
from kommunhandlingar.webbplats.lokalbehov import Steg
from kommunhandlingar.webbplats.lokalbehovkort import Behov, arets, egenskaper, korten
from kommunhandlingar.webbplats.mall import Mall, rot, sida, stig
from kommunhandlingar.webbplats.malsida import SKRIPT, STIL
from kommunhandlingar.webbplats.mandatperiod import kolumner, rubriker

EGEN_STIL = Path(__file__).with_name("lokalbehov.css")
ADR = (
    "/blob/main/docs/decisions/"
    "0057-lokalbehoven-foljs-steg-for-steg-ur-alla-organs-dokument.md"
)
INLEDNING = (
    "<p>Nämndens lokalbehov år för år: när de står i nämndens lokalbehov, "
    "hur de prioriteras, om de kommer in i kommunens lokalplan, får "
    "startbeslut och blir utförda. Varje ikon länkar till sidan i dokumentet "
    "som visar steget.</p>"
)
METOD = (
    "<p>Stegen är lästa ur poolens dokument, från vilket organ som helst: "
    "nämndens egna, budgeten, besluten om att starta projekt och "
    "redovisningen från det organ som bygger. Varje steg har en text som "
    "står på källans sida, och bygget prövar det.</p>"
    "<p>Ett behov har ett namn på sidan även när källorna kallar det olika. "
    "Där källan inte själv säger att det gäller behovet är kopplingen en "
    "bedömning och ikonen har en streckad ram. Ett år utan ikon betyder att "
    "inget steg står i poolen det året, inte att inget hände. Sidan visar "
    "vad som står var och värderar inte behoven.</p>"
)


def adress(kommun: Kommun, organ: str) -> str:
    return f"{kommun.id}/{organ}/lokalbehov.html"


def lokalbehovsida(mall: Mall, kommun: Kommun, stegen: list[Steg]) -> str:
    organ = stegen[0].organ
    sidans = adress(kommun, organ)
    namn = next(o.namn[0] for o in kommun.organ if o.id == organ)
    senaste = max(s.ar for s in stegen if s.fas == "lokalbehov")
    behoven = per_behov(stegen, senaste)
    ar = range(min(s.ar for s in stegen), max(s.ar for s in stegen) + 1)
    lankar = [
        (f"{rot(sidans)}{kommun.id}.html", kommun.namn),
        (f"../{organ}.html", namn),
    ]
    innehall = (
        stig(lankar) + f"<style>{STIL.read_text(encoding='utf-8')}"
        f"{EGEN_STIL.read_text(encoding='utf-8')}</style>"
        + INLEDNING
        + f"<details><summary>Om sidan</summary>{METOD}<p>Hur och varför står i "
        f'<a href="{escape(mall.repo + ADR)}">ADR-0057</a>.</p></details>'
        + sammandrag(behoven)
        + urval(senaste)
        + tidslinje(behoven, ar, kommun)
        + korten(behoven, ar, kommun)
        + f"<script>{SKRIPT.read_text(encoding='utf-8')}</script>"
    )
    return sida(mall, sidans, f"Lokalbehov – {namn}", innehall)


# Behoven i den ordning de först står, med stegen i år- och fasordning.
def per_behov(stegen: list[Steg], senaste: int) -> list[Behov]:
    namn = dict.fromkeys(s.behov for s in sorted(stegen, key=lambda s: s.ar))
    return [samla(n, [s for s in stegen if s.behov == n], senaste) for n in namn]


def samla(namn: str, stegen: list[Steg], senaste: int) -> Behov:
    aktiv = any(s.ar == senaste and s.fas == "lokalbehov" for s in stegen)
    return namn, sorted(stegen, key=ordning), aktiv


def ordning(steg: Steg) -> tuple[int, int]:
    return steg.ar, list(FASER).index(steg.fas)


def sammandrag(behoven: list[Behov]) -> str:
    siffror = "".join(
        f"<div><dt>{betyder}</dt><dd>{sum(nadd(b[1], fas) for b in behoven)}</dd></div>"
        for fas, (_, betyder) in FASER.items()
    )
    return (
        '<div class="sammandrag"><section class="ruta"><h3>Behov per fas</h3>'
        f'<dl class="siffror">{siffror}</dl><p><small>Antal behov som någon '
        "gång nått fasen enligt poolen.</small></p></section></div>"
    )


def nadd(stegen: list[Steg], fas: str) -> bool:
    return any(s.fas == fas for s in stegen)


# Knapparna visas av målsidans skript; utan det står allt.
def urval(sista: int) -> str:
    val = [("alla", "Alla"), ("aktiv", f"I lokalbehov {sista}")]
    val += [
        (fas, betyder.capitalize())
        for fas, (_, betyder) in FASER.items()
        if fas != "lokalbehov"
    ]
    knappar = "".join(
        f'<button type="button" data-urval="{v}">{text}</button>' for v, text in val
    )
    return f'<div class="urval" role="group" aria-label="Visa" hidden>{knappar}</div>'


def tidslinje(behoven: list[Behov], ar: range, kommun: Kommun) -> str:
    huvud = "".join(f'<th scope="col">{a}</th>' for a in ar)
    rader = "".join(rad(nr, b, ar, kommun) for nr, b in enumerate(behoven))
    return (
        f'<h2 id="tidslinje">Tidslinje</h2>{teckenforklaring()}'
        f'<div class="tabell"><table class="tidslinje">{kolumner(ar)}'
        f'<thead>{rubriker(ar)}<tr><th scope="col">Behov</th>{huvud}</tr></thead>'
        f"<tbody>{rader}</tbody></table></div>"
    )


def rad(nr: int, behov: Behov, ar: range, kommun: Kommun) -> str:
    namn, stegen, _ = behov
    finns = {s.ar for s in stegen}
    celler = "".join(cell(stegen, a, finns, kommun) for a in ar)
    return (
        f'<tr {egenskaper(nr, behov)}><th scope="row">'
        f'<a href="#behov-{nr}">{escape(namn)}</a></th>{celler}</tr>'
    )


def cell(stegen: list[Steg], ar: int, finns: set[int], kommun: Kommun) -> str:
    if ar not in finns:
        return "<td></td>"
    klass = "band" + " start" * (ar - 1 not in finns) + " slut" * (ar + 1 not in finns)
    return f'<td class="{klass}">{arets(stegen, ar, kommun)}</td>'
