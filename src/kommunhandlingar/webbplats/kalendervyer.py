"""Krav: K22 i docs/02-KRAV.md, ADR-0032. Test: tests/test_kalender.py.

Kalenderns två vyer: en tabell per månad, måndag först, med en ruta per
sammanträde, och en lista med en tabell per månad.
"""

import calendar
from collections import defaultdict
from html import escape
from urllib.parse import urlparse

from kommunhandlingar.webbplats.kalender import Sammantrade

MANADER = ["januari", "februari", "mars", "april", "maj", "juni", "juli"]
MANADER += ["augusti", "september", "oktober", "november", "december"]
VECKODAGAR = ["måndag", "tisdag", "onsdag", "torsdag", "fredag", "lördag", "söndag"]


def manadsnamn(ar: int, manad: int) -> str:
    return f"{MANADER[manad - 1]} {ar}"


def per_manad(sammantraden: list[Sammantrade]) -> dict[tuple[int, int], list]:
    manader = defaultdict(list)
    for s in sorted(sammantraden, key=lambda s: (s.datum, s.organ)):
        manader[(s.datum.year, s.datum.month)].append(s)
    return manader


def manader(sammantraden: list[Sammantrade]) -> str:
    moten = per_manad(sammantraden)
    tabeller = "".join(
        f'<section class="manad" data-manad="{ar}-{manad:02}">'
        f"<h3>{manadsnamn(ar, manad)}</h3>"
        f"{manadstabell(ar, manad, moten.get((ar, manad), []))}</section>"
        for ar, manad in alla_manader(list(moten))
    )
    knappar = (
        '<p class="blad" hidden><button type="button" data-steg="-1">'
        'Föregående månad</button> <button type="button" data-steg="1">'
        "Nästa månad</button></p>"
    )
    return f"<h2>Månad för månad</h2>{knappar}{tabeller}"


# Också en månad utan sammanträden får en tabell, så att bläddringen inte
# hoppar över den.
def alla_manader(manader: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not manader:
        return []
    (ar, manad), sista = manader[0], manader[-1]
    alla = []
    while (ar, manad) <= sista:
        alla.append((ar, manad))
        ar, manad = (ar + 1, 1) if manad == 12 else (ar, manad + 1)
    return alla


def manadstabell(ar: int, manad: int, moten: list[Sammantrade]) -> str:
    dagar = defaultdict(list)
    for s in moten:
        dagar[s.datum.day].append(ruta(s))
    huvud = "".join(f'<th scope="col">{d[:2]}</th>' for d in VECKODAGAR)
    veckor = "".join(
        "<tr>" + "".join(dagcell(dag, dagar[dag]) for dag in vecka) + "</tr>"
        for vecka in calendar.Calendar().monthdayscalendar(ar, manad)
    )
    return (
        f'<div class="tabell"><table class="kalender"><thead><tr>{huvud}</tr>'
        f"</thead><tbody>{veckor}</tbody></table></div>"
    )


def dagcell(dag: int, rutor: list[str]) -> str:
    if not dag:
        return "<td></td>"
    return f'<td><span class="dag">{dag}</span>{"".join(rutor)}</td>'


def ruta(s: Sammantrade) -> str:
    text = " ".join(filter(None, [s.organ.upper(), s.tid, "?" if s.osakert else ""]))
    klass = f"ruta o-{s.organ}" + (" osakert" if s.osakert else "")
    return f'<span class="{klass}" data-organ="{s.organ}">{escape(text)}</span> '


def lista(sammantraden: list[Sammantrade], namn: dict[str, str]) -> str:
    huvud = "".join(
        f'<th scope="col">{k}</th>' for k in ["Datum", "Organ", "Tid", "Plats", "Källa"]
    )
    tabeller = "".join(
        f'<section class="listmanad"><h3>{manadsnamn(ar, manad)}</h3>'
        f'<div class="tabell"><table><thead><tr>{huvud}</tr></thead>'
        f"<tbody>{''.join(listrad(s, namn) for s in moten)}</tbody></table></div>"
        "</section>"
        for (ar, manad), moten in per_manad(sammantraden).items()
    )
    return f"<h2>Lista</h2>{tabeller}"


def listrad(s: Sammantrade, namn: dict[str, str]) -> str:
    osakert = (
        f'<br><a href="#osakra" title="{escape(s.osakert)}">osäkert</a>'
        if s.osakert
        else ""
    )
    celler = [
        datumtext(s) + osakert,
        f'<span class="ruta o-{s.organ}">{s.organ.upper()}</span> '
        + escape(namn[s.organ]),
        escape(s.tid),
        escape(s.plats),
        kallank(s.kalla),
    ]
    return (
        f'<tr data-organ="{s.organ}" data-datum="{s.datum.isoformat()}">'
        + "".join(f"<td>{c}</td>" for c in celler)
        + "</tr>"
    )


def datumtext(s: Sammantrade) -> str:
    return f"{VECKODAGAR[s.datum.weekday()]} {s.datum.isoformat()}"


def kallank(kalla: str) -> str:
    if kalla.startswith("https://"):
        return f'<a href="{escape(kalla)}">{escape(urlparse(kalla).netloc)}</a>'
    organ, _, datum, fil = kalla.split("/", 3)
    adress = kalla.removesuffix(".md") + ".html"
    text = f"{organ.upper()} {datum}, {fil.split('-')[0].removesuffix('.md')}"
    return f'<a href="{escape(adress)}">{escape(text)}</a>'
