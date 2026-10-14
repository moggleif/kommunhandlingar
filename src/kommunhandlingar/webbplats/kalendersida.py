"""Krav: K22 och K32 i docs/02-KRAV.md, ADR-0032 och ADR-0053.
Test: tests/test_kalender.py.

Kalendersidan: en hopfälld del om kvaliteten med de osäkra datumen och
källorna per organ och år, urvalet av organ, en tabell per månad och
listan. Skriptet i `kalender.js` visar en månad i taget och döljer det som
valts bort; utan det står allt på sidan.
"""

from collections import defaultdict
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats import kalendervyer
from kommunhandlingar.webbplats.kalender import Sammantrade
from kommunhandlingar.webbplats.kalenderfarger import farger, stil
from kommunhandlingar.webbplats.mall import Mall, rot, sida, stig

SKRIPT = Path(__file__).with_name("kalender.js")
ADR = "/blob/main/docs/decisions/"
ADR_0032 = "0032-kalendern-las-ur-besluten-och-skrivs-for-hand.md"
ADR_0053 = "0053-tidigare-sammantraden-las-ur-poolens-mappar.md"
INLEDNING = (
    "<p>Organens sammanträden månad för månad och som lista från idag. "
    "Tidigare sammanträden finns bakåt i månadsvyn och under en knapp i "
    "listan. Välj vilka organ som visas.</p>"
)
METOD = (
    "<p>Datumen är lästa ur organens mötessidor och ur deras beslut om "
    "sammanträdesdagar; källorna står per organ och år under rubriken Källor "
    "nedan, och tidigare sammanträden ur poolen, med sitt eget protokoll som "
    "källa; ett tidigare sammanträde utan dokument i poolen saknas, och ett "
    "utan protokoll är märkt osäkert. Inställda möten och "
    "planeringsdagar är inte med. Tiden står där "
    "källan anger den, och platsen visas när man håller över rutan i "
    "månadsvyn. Ett datum är osäkert när källan är svår att läsa, eller när "
    "den anger en veckodag som datumet inte stämmer med. Ett osäkert datum "
    "har ett frågetecken i månadsvyn och ordet osäkert i listan.</p>"
)
STIL = """
[hidden] { display: none !important; }
.ruta { display: inline-block; border: 2px solid; border-radius: 3px;
        padding: 0 0.25rem; margin: 1px 0; font-size: 0.8rem; }
.osakert { border-style: dashed; }
table.kalender { table-layout: fixed; width: 100%; min-width: 44rem; }
table.kalender td { height: 5rem; }
.dag { display: block; font-size: 0.8rem; color: #555; }
details { margin-bottom: 1rem; }
.urval label { display: inline-block; margin: 0 1rem 0.25rem 0; }
"""


def kalendersida(mall: Mall, kommun: Kommun, sammantraden: list[Sammantrade]) -> str:
    adress = f"{kommun.id}/kalender.html"
    namn = {o.id: o.namn[0] for o in kommun.organ}
    farg = farger(kommun, {s.organ for s in sammantraden})
    innehall = (
        stig([(f"{rot(adress)}{kommun.id}.html", kommun.namn)])
        + f"<style>{STIL}{stil(farg)}</style>"
        + INLEDNING
        + kvalitet(mall, sammantraden, namn)
        + urval(farg, namn)
        + kalendervyer.manader(sammantraden)
        + kalendervyer.lista(sammantraden, namn)
        + f"<script>{SKRIPT.read_text(encoding='utf-8')}</script>"
    )
    return sida(mall, adress, f"Kalender – {kommun.namn}", innehall)


def kvalitet(mall: Mall, sammantraden: list[Sammantrade], namn: dict[str, str]) -> str:
    osakra = [s for s in sammantraden if s.osakert]
    adr = " och ".join(
        f'<a href="{escape(mall.repo + ADR + fil)}">ADR-{fil[:4]}</a>'
        for fil in (ADR_0032, ADR_0053)
    )
    return (
        f'<details id="kvalitet"><summary>Kvalitet: {len(osakra)} av '
        f"{len(sammantraden)} datum är osäkra</summary>{METOD}"
        f"<p>Hur och varför står i {adr}.</p>"
        f'<h2 id="osakra">Osäkra datum</h2>{osakra_tabell(osakra, namn)}'
        f'<h2 id="kallor">Källor</h2>'
        f"{kallor(sammantraden, namn)}</details>"
    )


def osakra_tabell(osakra: list[Sammantrade], namn: dict[str, str]) -> str:
    if not osakra:
        return "<p>Inga.</p>"
    rader = "".join(
        f"<tr><td>{kalendervyer.datumtext(s)}</td><td>{escape(namn[s.organ])}</td>"
        f"<td>{escape(s.osakert)}</td><td>{kallank(s.kalla)}</td></tr>"
        for s in osakra
    )
    return tabell(["Datum", "Organ", "Skäl", "Källa"], rader)


# Sammanträden med sitt eget dokument som källa (ADR-0053) räknas under
# nyckeln "" i stället för att länkas ett och ett.
def kallor(sammantraden: list[Sammantrade], namn: dict[str, str]) -> str:
    celler = defaultdict(dict)
    for s in sammantraden:
        nyckel = "" if eget_dokument(s) else s.kalla
        cell = celler[(s.organ, s.datum.year)]
        cell[nyckel] = cell.get(nyckel, 0) + 1
    ar = sorted({a for _, a in celler})
    organen = {o for o, _ in celler}
    rader = "".join(
        f'<tr><th scope="row">{escape(namn[organ])}</th>'
        + "".join(f"<td>{kallcell(organ, celler.get((organ, a), {}))}</td>" for a in ar)
        + "</tr>"
        for organ in namn
        if organ in organen
    )
    return tabell(["Organ", *ar], rader)


def eget_dokument(s: Sammantrade) -> bool:
    return s.kalla.split("/")[:3] == [s.organ, str(s.datum.year), s.datum.isoformat()]


def tabell(rubriker: list, rader: str) -> str:
    huvud = "".join(f'<th scope="col">{r}</th>' for r in rubriker)
    return (
        f'<div class="tabell"><table><thead><tr>{huvud}</tr></thead>'
        f"<tbody>{rader}</tbody></table></div>"
    )


def kallcell(organ: str, cell: dict[str, int]) -> str:
    lankar = [kallank(k) for k in cell if k]
    if cell.get(""):
        lankar.append(f'<a href="{organ}.html">{cell[""]} sammanträden i poolen</a>')
    return "<br>".join(lankar)


def urval(farg: dict[str, tuple[str, str]], namn: dict[str, str]) -> str:
    rutor = "".join(
        f'<label><input type="checkbox" checked data-organ="{organ}"> '
        f'<span class="ruta o-{organ}">{organ.upper()}</span> '
        f"{escape(namn[organ])}</label>"
        for organ in farg
    )
    return f'<fieldset class="urval"><legend>Organ som visas</legend>{rutor}</fieldset>'


def kallank(kalla: str) -> str:
    if kalla.startswith("https://"):
        return f'<a href="{escape(kalla)}">{escape(urlparse(kalla).netloc)}</a>'
    organ, _, datum, fil = kalla.split("/", 3)
    adress = kalla.removesuffix(".md") + ".html"
    text = f"{organ.upper()} {datum}, {fil.split('-')[0].removesuffix('.md')}"
    return f'<a href="{escape(adress)}">{escape(text)}</a>'
