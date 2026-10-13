"""Krav: K26 och K27 i docs/02-KRAV.md, ADR-0044 och ADR-0045.
Test: tests/test_mal.py.

Sidan om ett organs mål och direktiv: en hopfälld del om metoden, urvalet
av slag, översikten med ett spår per grupp av rader och ett år per
kolumn, antalet per år (`malstatistik.py`) och ett avsnitt per år
(`malavsnitt.py`). Skriptet i `mal.js` döljer det som valts bort; utan
det står allt på sidan.
"""

from collections import defaultdict
from html import escape
from pathlib import Path

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mal import SLAG, Mal
from kommunhandlingar.webbplats.malavsnitt import arsavsnitt, namnen
from kommunhandlingar.webbplats.mall import Mall, rot, sida, stig
from kommunhandlingar.webbplats.malstatistik import statistik
from kommunhandlingar.webbplats.statusikon import ikon, teckenforklaring

SKRIPT = Path(__file__).with_name("mal.js")
ADR = "/blob/main/docs/decisions/"
ADR_0044 = "0044-namndens-mal-och-direktiv-las-ur-dokumenten-och-skrivs-for-hand.md"
ADR_0045 = "0045-omdopta-mal-grupperas-protokollet-gar-fore-och-status-blir-ikoner.md"
INLEDNING = (
    "<p>Nämndens egna mål och direktiv år för år, ur nämndbudgetarna, "
    "delårsrapporterna och årsredovisningarna i poolen. Välj ett mål i "
    "översikten för att följa det genom åren.</p>"
)
METOD = (
    "<p>Målen är lästa ur poolens dokument och skrivna ordagrant, med "
    "dokumentet och sidan som källa. Bygget prövar att texten står på den "
    "sidan. Bara det nämnden själv beslutat står med, inte "
    "kommunfullmäktiges mål eller direktiv. Säger protokollet något annat "
    "än handlingarna till samma möte, gäller protokollet.</p>"
    "<p>Ett mål som bytt rubrik står med sina rubriker under varandra. "
    "Där källan inte själv säger att det är samma mål, och formuleringen "
    "inte är densamma, är kopplingen en bedömning och rubriken märkt "
    "tolkad.</p>"
    "<p>Statusen är en ikon för uppföljningens bedömning, med källans egen "
    "formulering i pekrutan och i årets avsnitt. En delårsrapport ger en "
    "prognos, som har en streckad ram. Ett år utan dokument i poolen är en "
    "lucka i poolen, inte ett år utan mål.</p>"
)
STIL = """
[hidden] { display: none !important; }
button.spar { background: none; border: none; padding: 0; font: inherit;
              color: inherit; text-align: left; text-decoration: underline;
              cursor: pointer; }
.urval label { display: inline-block; margin: 0 1rem 0.25rem 0; }
details { margin-bottom: 1rem; }
.teckenforklaring { list-style: none; padding: 0; display: flex;
                   flex-wrap: wrap; gap: 0 1.5rem; }
table.mal tbody { border-top: 3px solid #999; }
svg.graf { max-width: 40rem; height: auto; }
"""


def adress(kommun: Kommun, organ: str) -> str:
    return f"{kommun.id}/{organ}/mal-och-direktiv.html"


# Alla mål är samma organs; åren går från organets första till sista år i
# poolen eller bland målen. Ett år utan både dokument och mål är en lucka:
# ett år med mål ur ett senare dokument, som en årsredovisning, är det inte.
def malsida(mall: Mall, kommun: Kommun, malen: list[Mal], dokumentar: set[int]) -> str:
    organ = malen[0].organ
    sidans = adress(kommun, organ)
    namn = next(o.namn[0] for o in kommun.organ if o.id == organ)
    spar = sparen(malen)
    ar = dokumentar | {m.ar for m in malen}
    alla_ar = range(min(ar), max(ar) + 1)
    luckor = set(alla_ar) - ar
    innehall = (
        stig(
            [
                (f"{rot(sidans)}{kommun.id}.html", kommun.namn),
                (f"../{organ}.html", namn),
            ]
        )
        + f"<style>{STIL}</style>{INLEDNING}{om_sidan(mall)}"
        + urval(malen)
        + teckenforklaring()
        + oversikt(spar, alla_ar, luckor)
        + statistik(malen)
        + "".join(arsavsnitt(a, spar, a in luckor) for a in reversed(alla_ar))
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


def urval(malen: list[Mal]) -> str:
    rutor = "".join(
        f'<label><input type="checkbox" checked data-slag="{slag}"> {slag}</label>'
        for slag in SLAG
        if any(m.slag == slag for m in malen)
    )
    knapp = '<button type="button" id="alla" hidden>Visa alla mål</button>'
    return f'<fieldset class="urval"><legend>Visas</legend>{rutor} {knapp}</fieldset>'


def oversikt(spar: list[list[Mal]], alla_ar: range, luckor: set[int]) -> str:
    huvud = "".join(
        f'<th scope="col">{a}{"<br>lucka" if a in luckor else ""}</th>' for a in alla_ar
    )
    grupper = "".join(grupp(nr, malen, alla_ar) for nr, malen in enumerate(spar))
    return (
        '<h2 id="oversikt">Översikt</h2><div class="tabell"><table class="mal">'
        f'<thead><tr><th scope="col">Mål eller direktiv</th>{huvud}</tr></thead>'
        f"{grupper}</table></div>"
    )


def grupp(nr: int, malen: list[Mal], alla_ar: range) -> str:
    rader = namnen(malen)
    return (
        "<tbody>"
        + "".join(rad(nr, i > 0, r, alla_ar) for i, r in enumerate(rader))
        + "</tbody>"
    )


def rad(nr: int, foljer: bool, rader: list[Mal], alla_ar: range) -> str:
    forsta = rader[0]
    rubrik = (
        f'{"↳ " if foljer else ""}<button type="button" class="spar">'
        f"{escape(forsta.rubrik)}</button> ({forsta.slag})"
        + (" <small>tolkad</small>" if forsta.tolkad else "")
    )
    celler = "".join(
        f"<td>{cell([m for m in rader if m.ar == a], a)}</td>" for a in alla_ar
    )
    return (
        f'<tr data-slag="{forsta.slag}" data-spar="{nr}">'
        f'<th scope="row">{rubrik}</th>{celler}</tr>'
    )


def cell(arets: list[Mal], ar: int) -> str:
    if not arets:
        return ""
    ikoner = "".join(
        ikon(m.bedomning, m.status, m.prognos) for m in arets if m.uppfoljning
    )
    return f'<a href="#ar-{ar}" aria-label="Med {ar}">●</a> {ikoner}'
