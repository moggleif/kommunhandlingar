"""Krav: K26, K27 och K29 i docs/02-KRAV.md, ADR-0044, ADR-0045 och ADR-0050.
Test: tests/test_mal.py och tests/test_malkort.py.

Sidan om ett organs mål och direktiv: en hopfälld del om metoden, antalet
per år (`malstatistik.py`), ett urval, tidslinjen (`maltidslinje.py`) och
ett kort per spår (`malkort.py`). Skriptet i `mal.js` visar bara det som
valts och öppnar kortet för ett mål som väljs i tidslinjen; utan det står
allt på sidan. Stilen står i `mal.css`.
"""

from collections import defaultdict
from html import escape
from pathlib import Path

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mal import SLAG, Mal
from kommunhandlingar.webbplats.malkort import korten
from kommunhandlingar.webbplats.mall import Mall, rot, sida, stig
from kommunhandlingar.webbplats.malstatistik import protokollar, statistik
from kommunhandlingar.webbplats.maltidslinje import namnden_rad, tidslinje

SKRIPT = Path(__file__).with_name("mal.js")
STIL = Path(__file__).with_name("mal.css")
ADR = "/blob/main/docs/decisions/"
ADR_0044 = "0044-namndens-mal-och-direktiv-las-ur-dokumenten-och-skrivs-for-hand.md"
ADR_0045 = "0045-omdopta-mal-grupperas-protokollet-gar-fore-och-status-blir-ikoner.md"
INLEDNING = (
    "<p>Nämndens egna mål och direktiv år för år, ur nämndbudgetarna, "
    "delårsrapporterna och årsredovisningarna i poolen. Välj ett mål i "
    "tidslinjen för att se hela dess historik.</p>"
)
METOD = (
    "<p>Målen är lästa ur poolens dokument och skrivna ordagrant, med "
    "dokumentet och sidan som källa. Bygget prövar att texten står på den "
    "sidan. Bara det nämnden själv beslutat står med, inte "
    "kommunfullmäktiges mål eller direktiv. Säger protokollet något annat "
    "än handlingarna till samma möte, gäller protokollet.</p>"
    "<p>Ett mål som bytt rubrik har ett kort, med de tidigare rubrikerna "
    "under den senaste. "
    "Där källan inte själv säger att det är samma mål, och formuleringen "
    "inte är densamma, är kopplingen en bedömning och rubriken märkt "
    "tolkad.</p>"
    "<p>Statusen är en ikon för uppföljningens bedömning, med källans egen "
    "formulering i pekrutan och i kortets historik. En delårsrapport ger en "
    "prognos, som har en streckad ram. Ett år utan dokument i poolen är en "
    "lucka i poolen, inte ett år utan mål.</p>"
)


def adress(kommun: Kommun, organ: str) -> str:
    return f"{kommun.id}/{organ}/mal-och-direktiv.html"


# Alla mål är samma organs, och åren går från målens första till sista år.
# Ett år utan både dokument och mål är en lucka: ett år med mål ur ett
# senare dokument, som en årsredovisning, är det inte.
def malsida(mall: Mall, kommun: Kommun, malen: list[Mal], organets: list[dict]) -> str:
    organ = malen[0].organ
    uppfoljda = [u for u in mall.uppfoljningar.get(kommun.id, []) if u.organ == organ]
    protokoll = protokollar(organets)
    sidans = adress(kommun, organ)
    namn = next(o.namn[0] for o in kommun.organ if o.id == organ)
    spar = sparen(malen)
    ar = range(min(m.ar for m in malen), max(m.ar for m in malen) + 1)
    luckor = set(ar) - {int(d["datum"][:4]) for d in organets} - {m.ar for m in malen}
    lankar = [
        (f"{rot(sidans)}{kommun.id}.html", kommun.namn),
        (f"../{organ}.html", namn),
    ]
    innehall = (
        stig(lankar)
        + f"<style>{STIL.read_text(encoding='utf-8')}</style>"
        + INLEDNING
        + om_sidan(mall)
        + statistik(malen, uppfoljda, protokoll)
        + urval(ar[-1])
        + tidslinje(spar, ar, luckor, namnden_rad(uppfoljda, protokoll, ar))
        + korten(spar, ar, luckor)
        + f"<script>{SKRIPT.read_text(encoding='utf-8')}</script>"
    )
    return sida(mall, sidans, f"Mål och direktiv – {namn}", innehall)


def sparen(malen: list[Mal]) -> list[list[Mal]]:
    spar = defaultdict(list)
    for mal in sorted(malen, key=ordning):
        spar[mal.spar].append(mal)
    return list(spar.values())


def ordning(mal: Mal) -> tuple[int, int, str]:
    return mal.ar, SLAG.index(mal.slag), mal.rubrik.casefold()


def om_sidan(mall: Mall) -> str:
    adr = [
        f'<a href="{escape(mall.repo + ADR + fil)}">ADR-{fil[:4]}</a>'
        for fil in (ADR_0044, ADR_0045)
    ]
    return (
        f"<details><summary>Om sidan</summary>{METOD}"
        f"<p>Hur och varför står i {' och '.join(adr)}.</p></details>"
    )


# Knapparna visas av skriptet; utan det står allt och urvalet behövs inte.
def urval(sista: int) -> str:
    val = [("alla", "Alla"), ("aktiv", f"Gäller {sista}")]
    val += [(slag, slag.capitalize()) for slag in SLAG]
    val += [("bytt", "Har bytt rubrik")]
    knappar = "".join(
        f'<button type="button" data-urval="{v}">{text}</button>' for v, text in val
    )
    return f'<div class="urval" role="group" aria-label="Visa" hidden>{knappar}</div>'
