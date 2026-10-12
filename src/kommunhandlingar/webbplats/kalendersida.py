"""Krav: K22 i docs/02-KRAV.md, ADR-0032. Test: tests/test_kalender.py.

Kalendersidan: en hopfälld del om kvaliteten med de osäkra datumen, urvalet
av organ, en tabell per månad och listan. Skriptet
i `kalender.js` visar en månad i taget och döljer det som valts bort; utan
det står allt på sidan.
"""

from html import escape
from pathlib import Path

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats import kalendervyer
from kommunhandlingar.webbplats.kalender import Sammantrade
from kommunhandlingar.webbplats.kalenderfarger import farger, stil
from kommunhandlingar.webbplats.mall import Mall, rot, sida, stig

SKRIPT = Path(__file__).with_name("kalender.js")
ADR = "/blob/main/docs/decisions/0032-kalendern-las-ur-besluten-och-skrivs-for-hand.md"
INLEDNING = (
    "<p>Organens sammanträden månad för månad och som lista från idag. "
    "Välj vilka organ som visas.</p>"
)
METOD = (
    "<p>Datumen är lästa ur organens mötessidor och ur deras beslut om "
    "sammanträdesdagar, och varje sammanträde har sin källa i listan. Inställda "
    "möten och planeringsdagar är inte med, och tid och plats står där källan "
    "anger dem. Ett datum är osäkert när källan är svår att läsa, eller när den "
    "anger en veckodag som datumet inte stämmer med. Ett osäkert datum har ett "
    "frågetecken i månadsvyn och ordet osäkert i listan.</p>"
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
    adr = f'<a href="{escape(mall.repo + ADR)}">ADR-0032</a>'
    return (
        f'<details id="kvalitet"><summary>Kvalitet: {len(osakra)} av '
        f"{len(sammantraden)} datum är osäkra</summary>{METOD}"
        f"<p>Hur och varför står i {adr}.</p>"
        f'<h2 id="osakra">Osäkra datum</h2>{osakra_tabell(osakra, namn)}</details>'
    )


def osakra_tabell(osakra: list[Sammantrade], namn: dict[str, str]) -> str:
    if not osakra:
        return "<p>Inga.</p>"
    huvud = "".join(
        f'<th scope="col">{k}</th>' for k in ["Datum", "Organ", "Skäl", "Källa"]
    )
    rader = "".join(
        f"<tr><td>{kalendervyer.datumtext(s)}</td><td>{escape(namn[s.organ])}</td>"
        f"<td>{escape(s.osakert)}</td><td>{kalendervyer.kallank(s.kalla)}</td></tr>"
        for s in osakra
    )
    return (
        f'<div class="tabell"><table><thead><tr>{huvud}</tr></thead>'
        f"<tbody>{rader}</tbody></table></div>"
    )


def urval(farg: dict[str, tuple[str, str]], namn: dict[str, str]) -> str:
    rutor = "".join(
        f'<label><input type="checkbox" checked data-organ="{organ}"> '
        f'<span class="ruta o-{organ}">{organ.upper()}</span> '
        f"{escape(namn[organ])}</label>"
        for organ in farg
    )
    return f'<fieldset class="urval"><legend>Organ som visas</legend>{rutor}</fieldset>'
