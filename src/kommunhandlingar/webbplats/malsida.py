"""Krav: K26 i docs/02-KRAV.md, ADR-0044. Test: tests/test_mal.py.

Sidan om ett organs mål och direktiv: en hopfälld del om metoden, urvalet
av slag, översikten med ett mål per rad och ett år per kolumn, och ett
avsnitt per år. Skriptet i `mal.js` döljer det som valts bort; utan det
står allt på sidan.
"""

from collections import defaultdict
from html import escape
from pathlib import Path

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mal import SLAG, Mal
from kommunhandlingar.webbplats.mall import Mall, rot, sida, stig

SKRIPT = Path(__file__).with_name("mal.js")
ADR = (
    "/blob/main/docs/decisions/"
    "0044-namndens-mal-och-direktiv-las-ur-dokumenten-och-skrivs-for-hand.md"
)
INLEDNING = (
    "<p>Nämndens egna mål och direktiv år för år, ur nämndbudgetarna, "
    "delårsrapporterna och årsredovisningarna i poolen. Välj ett mål i "
    "översikten för att följa det genom åren.</p>"
)
METOD = (
    "<p>Målen är lästa ur poolens dokument och skrivna ordagrant, med "
    "dokumentet och sidan som källa. Bygget prövar att texten står på den "
    "sidan. Bara det nämnden själv beslutat står med, inte "
    "kommunfullmäktiges mål eller direktiv. Statusen är uppföljningens egen "
    "formulering; i en delårsrapport är den en prognos. Samma mål är samma "
    "rubrik; ett mål som bytt rubrik står på två rader. Ett år utan "
    "dokument i poolen är en lucka i poolen, inte ett år utan mål.</p>"
)
STIL = """
[hidden] { display: none !important; }
button.spar { background: none; border: none; padding: 0; font: inherit;
              color: inherit; text-align: left; text-decoration: underline;
              cursor: pointer; }
.urval label { display: inline-block; margin: 0 1rem 0.25rem 0; }
details { margin-bottom: 1rem; }
"""
Spar = tuple[str, str, str]


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
        + oversikt(spar, alla_ar, luckor)
        + "".join(arsavsnitt(a, spar, a in luckor) for a in reversed(alla_ar))
        + f"<script>{SKRIPT.read_text(encoding='utf-8')}</script>"
    )
    return sida(mall, sidans, f"Mål och direktiv – {namn}", innehall)


# Ett mål per spår, i ordning efter första år, slag och rubrik.
def sparen(malen: list[Mal]) -> dict[Spar, list[Mal]]:
    spar = defaultdict(list)
    for mal in sorted(malen, key=ordning):
        spar[mal.spar].append(mal)
    return dict(spar)


def ordning(mal: Mal) -> tuple[int, int, str]:
    return mal.ar, SLAG.index(mal.slag), mal.rubrik.casefold()


def om_sidan(mall: Mall) -> str:
    adr = f'<a href="{escape(mall.repo + ADR)}">ADR-0044</a>'
    return (
        f"<details><summary>Om sidan</summary>{METOD}"
        f"<p>Hur och varför står i {adr}.</p></details>"
    )


def urval(malen: list[Mal]) -> str:
    rutor = "".join(
        f'<label><input type="checkbox" checked data-slag="{slag}"> {slag}</label>'
        for slag in SLAG
        if any(m.slag == slag for m in malen)
    )
    knapp = '<button type="button" id="alla" hidden>Visa alla mål</button>'
    return f'<fieldset class="urval"><legend>Visas</legend>{rutor} {knapp}</fieldset>'


def oversikt(spar: dict[Spar, list[Mal]], alla_ar: range, luckor: set[int]) -> str:
    huvud = "".join(
        f'<th scope="col">{a}{"<br>lucka" if a in luckor else ""}</th>' for a in alla_ar
    )
    rader = "".join(
        f'<tr data-slag="{nyckel[1]}" data-spar="{nr}"><th scope="row">'
        f'<button type="button" class="spar">{escape(malen[0].rubrik)}</button>'
        f" ({nyckel[1]})</th>"
        + "".join(
            f"<td>{cell([m for m in malen if m.ar == a], a)}</td>" for a in alla_ar
        )
        + "</tr>"
        for nr, (nyckel, malen) in enumerate(spar.items())
    )
    return (
        '<h2 id="oversikt">Översikt</h2><div class="tabell"><table>'
        f'<thead><tr><th scope="col">Mål eller direktiv</th>{huvud}</tr></thead>'
        f"<tbody>{rader}</tbody></table></div>"
    )


def cell(arets: list[Mal], ar: int) -> str:
    if not arets:
        return ""
    status = "".join(
        f"<br><small>{escape(m.status)}</small>" for m in arets if m.status
    )
    return f'<a href="#ar-{ar}" aria-label="Med {ar}">●</a>{status}'


def arsavsnitt(ar: int, spar: dict[Spar, list[Mal]], lucka: bool) -> str:
    artiklar = "".join(
        artikel(nr, [m for m in malen if m.ar == ar])
        for nr, malen in enumerate(spar.values())
        if any(m.ar == ar for m in malen)
    )
    if lucka:
        artiklar = "<p>Poolen har inga dokument från organet det här året.</p>"
    elif not artiklar:
        artiklar = "<p>Inga mål eller direktiv i poolens dokument från året.</p>"
    return f'<section id="ar-{ar}"><h2>{ar}</h2>{artiklar}</section>'


def artikel(nr: int, arets: list[Mal]) -> str:
    forsta = arets[0]
    poster = "".join(f"<li>{post(m)}</li>" for m in arets)
    return (
        f'<article data-slag="{forsta.slag}" data-spar="{nr}">'
        f"<h3>{escape(forsta.rubrik)}</h3><p>{forsta.slag.capitalize()}</p>"
        f"<ul>{poster}</ul></article>"
    )


def post(mal: Mal) -> str:
    delar = []
    if mal.formulering:
        delar.append(f"<q>{escape(mal.formulering)}</q>")
    if mal.status:
        delar.append(f"Status: {escape(mal.status)}")
    return "<br>".join([*delar, f"Källa: {kallank(mal.kalla)}"])


# Sidan ligger i organets katalog, bredvid årens kataloger.
def kallank(kalla: str) -> str:
    dokument, sidnr = kalla.split("#sida-")
    _, _, datum, fil = dokument.split("/")
    adress = dokument.split("/", 1)[1].removesuffix(".md") + f".html#sida-{sidnr}"
    text = f"{fil.removesuffix('.md')} {datum}, sida {sidnr}"
    return f'<a href="{escape(adress)}">{escape(text)}</a>'
