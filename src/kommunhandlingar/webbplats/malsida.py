"""Krav: K26, K27, K29, K35, K39, K50 och K60 i docs/02-KRAV.md, ADR-0044,
ADR-0045, ADR-0050, ADR-0051, ADR-0056, ADR-0073 och ADR-0086. Test: tests/test_mal.py,
tests/test_malkort.py, tests/test_malar.py och tests/test_fokusomraden.py.

Sidan om ett organs mål och direktiv: en hopfälld del om metoden, antalet
per år (`malstatistik.py`), ett urval och tre perspektiv: tidslinjen
(`maltidslinje.py`), ett år i taget (`malar.py`) och ett kort per spår
(`malkort.py`). Skriptet i `mal.js` visar bara det som valts och öppnar
kortet för ett mål som väljs i tidslinjen, och `perspektiv.js` visar ett
perspektiv i taget; utan dem står allt på sidan. Stilen står i `mal.css`.
"""

from collections import defaultdict
from html import escape
from pathlib import Path

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.flikar import MAL, flikar
from kommunhandlingar.webbplats.mal import SLAG, Mal
from kommunhandlingar.webbplats.malar import Underlag, aren
from kommunhandlingar.webbplats.malkort import korten
from kommunhandlingar.webbplats.mall import KALLKOD, Mall, sida
from kommunhandlingar.webbplats.malstatistik import protokollar, statistik
from kommunhandlingar.webbplats.maltidslinje import namnden_rad, tidslinje

SKRIPT = Path(__file__).with_name("mal.js")
PERSPEKTIVSKRIPT = Path(__file__).with_name("perspektiv.js")
STIL = Path(__file__).with_name("mal.css")
ADR = "/blob/main/docs/decisions/"
ADR_0044 = "0044-namndens-mal-och-direktiv-las-ur-dokumenten-och-skrivs-for-hand.md"
ADR_0045 = "0045-omdopta-mal-grupperas-protokollet-gar-fore-och-status-blir-ikoner.md"
ADR_0050 = "0050-malsidan-visas-som-tidslinje-och-malkort.md"
ADR_0051 = "0051-tidslinjen-visar-varje-rubrik-och-nya-formuleringar.md"
ADR_0056 = "0056-kommunfullmaktiges-mal-med-fokusomraden-och-farg.md"
INLEDNING = (
    "<p>Organets egna mål och direktiv år för år, ur budgetarna, "
    "delårsrapporterna och årsredovisningarna i poolen. Välj ett mål i "
    "tidslinjen för att se hela dess historik.</p>"
)
METOD = (
    "<p>Målen är lästa ur poolens dokument och skrivna ordagrant, med "
    "dokumentet och sidan som källa. Bygget prövar att texten står på den "
    "sidan. Bara det organet självt beslutat står med, så en nämnds sida "
    "har inte kommunfullmäktiges mål eller direktiv. Säger protokollet något "
    "annat än handlingarna till samma möte, gäller protokollet.</p>"
    "<p>Ett mål som bytt rubrik har en rad per rubrik i tidslinjen, i den "
    "ordning de först står, och ett kort med de tidigare rubrikerna under "
    "den senaste. Ett år då samma rubrik får en ny formulering är markerat. "
    "Där källan inte själv säger att det är samma mål, och formuleringen "
    "inte är densamma, är kopplingen en bedömning och rubriken märkt "
    "tolkad.</p>"
    "<p>Statusen är en ikon för uppföljningens bedömning, med källans egen "
    "formulering i pekrutan och i kortets historik. En delårsrapport ger en "
    "prognos, som har en streckad ram. Ett år utan dokument i poolen är en "
    "lucka i poolen, inte ett år utan mål, också före organets första "
    "dokument i poolen.</p>"
)
# Delas med spårsidorna (K60, ADR-0086).
AREN = (
    "<p>Åren är desamma på alla kommunens sidor över tid, så att de går att "
    "jämföra: från poolens första år, eller ett äldre år som någon rad "
    "har, till i år, eller ett senare år som någon rad har, som en budget "
    "för nästa år. Ett år utan rader står tomt.</p>"
)
FOKUS = (
    "<p>Ett mål med fokusområden har dem under sig i tidslinjen och i sitt "
    "kort. En uppföljning kan bedöma med färg i stället för ord. Färgen "
    "följer inte med in i texten, så den är avläst ur PDF:en på källans "
    "sida, visas som ikonen för uppnått, delvis eller ej och är märkt "
    "som avläst ur färgen. Hur källan använder färgerna står i "
    "beskrivningen av kommunens källor. En rad har en status bara där "
    "källans bedömning står i texten. Budgeten och uppföljningen kan "
    "skriva ett fokusområde på olika sätt samma år, och då har det en rad "
    "för varje.</p>"
)

# Väljaren visas av skriptet, som visar ett perspektiv i taget (ADR-0073).
PERSPEKTIV = (
    '<div class="perspektiv" role="group" aria-label="Perspektiv" hidden>'
    '<button type="button" data-vy="tidslinje">Tidslinje</button>'
    '<button type="button" data-vy="ar">Ett år i taget</button>'
    '<button type="button" data-vy="kort">Målkort</button></div>'
)


# Sidan börjar med målens första år; poolens dokument kan vara äldre.
def fore_malen(forsta_dokument: int, forsta_mal: int) -> str:
    if forsta_dokument >= forsta_mal:
        return ""
    return (
        f"<p>Poolen har dokument från organet sedan {forsta_dokument}, men "
        f"inga av organets mål före {forsta_mal}.</p>"
    )


def adress(kommun: Kommun, organ: str) -> str:
    return f"{kommun.id}/{organ}/{MAL}.html"


# Alla mål är samma organs, och åren är kommunens (K60). Ett år fram till
# byggåret utan både dokument och mål är en lucka: ett år med mål ur ett
# senare dokument, som en årsredovisning, är det inte.
def malsida(mall: Mall, kommun: Kommun, malen: list[Mal], organets: list[dict]) -> str:
    organ = malen[0].organ
    uppfoljda = [u for u in mall.uppfoljningar.get(kommun.id, []) if u.organ == organ]
    protokoll = protokollar(organets)
    sidans = adress(kommun, organ)
    namn = next(o.namn[0] for o in kommun.organ if o.id == organ)
    spar = sparen(malen)
    malar = {m.ar for m in malen}
    ar = mall.aren[kommun.id]
    dokumentar = {int(d["datum"][:4]) for d in organets}
    luckor = set(range(ar[0], mall.byggd.year + 1)) - dokumentar - malar
    innehall = (
        flikar(mall, kommun.id, organ, MAL)
        + f"<style>{STIL.read_text(encoding='utf-8')}</style>"
        + INLEDNING
        + fore_malen(min(dokumentar), min(malar))
        + om_sidan(mall, any(m.huvudmal for m in malen))
        + statistik(malen, uppfoljda, protokoll, ar)
        + urval(max(malar), {m.slag for m in malen})
        + PERSPEKTIV
        + vy(
            "tidslinje",
            tidslinje(spar, ar, luckor, namnden_rad(uppfoljda, protokoll, ar)),
        )
        + vy("ar", aren(Underlag(spar, ar, luckor, uppfoljda, protokoll)))
        + vy("kort", korten(spar, ar, luckor))
        + skript()
    )
    return sida(mall, sidans, f"Mål och direktiv – {namn}", innehall)


def skript() -> str:
    return "".join(
        f"<script>{fil.read_text(encoding='utf-8')}</script>"
        for fil in (SKRIPT, PERSPEKTIVSKRIPT)
    )


def vy(namn: str, innehall: str) -> str:
    return f'<section data-vy="{namn}">{innehall}</section>'


def sparen(malen: list[Mal]) -> list[list[Mal]]:
    spar = defaultdict(list)
    for mal in sorted(malen, key=ordning):
        spar[mal.spar].append(mal)
    return list(spar.values())


def ordning(mal: Mal) -> tuple[int, int, str]:
    return mal.ar, SLAG.index(mal.slag), mal.rubrik.casefold()


def om_sidan(mall: Mall, fokus: bool) -> str:
    adr = [
        f'<a href="{escape(KALLKOD + ADR + fil)}">ADR-{fil[:4]}</a>'
        for fil in (ADR_0044, ADR_0045, ADR_0050, ADR_0051, ADR_0056)
    ]
    return (
        f"<details><summary>Om sidan</summary>{METOD}{AREN}{FOKUS * fokus}"
        f"<p>Hur och varför står i {', '.join(adr[:-1])} och {adr[-1]}.</p></details>"
    )


# Knapparna visas av skriptet; utan det står allt och urvalet behövs inte.
def urval(sista: int, slagen: set[str]) -> str:
    val = [("alla", "Alla"), ("aktiv", f"Gäller {sista}")]
    val += [(slag, slag.capitalize()) for slag in SLAG if slag in slagen]
    val += [("bytt", "Har bytt rubrik")]
    knappar = "".join(
        f'<button type="button" data-urval="{v}">{text}</button>' for v, text in val
    )
    return (
        f'<div class="urval" role="group" aria-label="Visa" data-sista="{sista}" '
        f"hidden>{knappar}</div>"
    )
