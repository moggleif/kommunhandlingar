"""Krav: K22 i docs/02-KRAV.md, ADR-0032. Test: tests/test_kalender.py.

Kalendersidan: urvalet av organ, en tabell per månad och listan. Skriptet
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
STIL = """
[hidden] { display: none !important; }
.ruta { display: inline-block; border: 2px solid; border-radius: 3px;
        padding: 0 0.25rem; margin: 1px 0; font-size: 0.8rem; }
.osakert { border-style: dashed; }
table.kalender { table-layout: fixed; width: 100%; min-width: 44rem; }
table.kalender td { height: 5rem; }
.dag { display: block; font-size: 0.8rem; color: #555; }
.urval label { display: inline-block; margin: 0 1rem 0.25rem 0; }
"""


def kalendersida(mall: Mall, kommun: Kommun, sammantraden: list[Sammantrade]) -> str:
    adress = f"{kommun.id}/kalender.html"
    namn = {o.id: o.namn[0] for o in kommun.organ}
    farg = farger(kommun, {s.organ for s in sammantraden})
    innehall = (
        stig([(f"{rot(adress)}{kommun.id}.html", kommun.namn)])
        + f"<style>{STIL}{stil(farg)}</style>"
        + inledning(mall)
        + urval(farg, namn)
        + kalendervyer.manader(sammantraden)
        + kalendervyer.lista(sammantraden, namn)
        + f"<script>{SKRIPT.read_text(encoding='utf-8')}</script>"
    )
    return sida(mall, adress, f"Kalender – {kommun.namn}", innehall)


def inledning(mall: Mall) -> str:
    return (
        "<p>Organens sammanträden, lästa ur deras beslut om sammanträdesdagar "
        "och ur kommunens mötessidor. Varje sammanträde har sin källa i listan. "
        "Ett datum som är osäkert inläst har ett frågetecken och streckad ram, "
        f'och skälet står i listan. Hur kalendern tas fram står i <a href="'
        f'{escape(mall.repo + ADR)}">ADR-0032</a>.</p>'
    )


def urval(farg: dict[str, tuple[str, str]], namn: dict[str, str]) -> str:
    rutor = "".join(
        f'<label><input type="checkbox" checked data-organ="{organ}"> '
        f'<span class="ruta o-{organ}">{organ.upper()}</span> '
        f"{escape(namn[organ])}</label>"
        for organ in farg
    )
    return f'<fieldset class="urval"><legend>Organ som visas</legend>{rutor}</fieldset>'
