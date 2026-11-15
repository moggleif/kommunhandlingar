"""Krav: K57 i docs/02-KRAV.md, ADR-0080. Test: tests/test_navigering.py.

Webbplatsens meny i den gemensamma form som Giffå ritar (ADR-0080): poolens
namn och högst sex poster, där en post är en länk eller en undermeny. Varje
kommun får en undermeny med sina organ i kommunfilens grupper och en länk
till sin kalender; poolens egna sidor står under *Om poolen*.
"""

from html import escape

from kommunhandlingar.konfiguration import Kommun, Organ
from kommunhandlingar.webbplats import avvikelser
from kommunhandlingar.webbplats.organordning import grupperade

NAMN = "Kommunhandlingar"
# Giffå publicerar menyns stil och skript på samma värd som poolens sida.
GEMENSAM = (
    '<link rel="stylesheet" href="/giffa/sajter.css">\n'
    '<script src="/giffa/sajter.js" defer></script>'
)

Grupp = tuple[str, list[tuple[str, str]]]


def meny(kommuner: list[Kommun], kalendrar: frozenset[str], aktuell: str) -> str:
    poster = []
    for k in kommuner:
        poster.append(undermeny(k.namn, organen(k), aktuell))
        if k.id in kalendrar:
            poster.append(post(f"{k.id}/kalender.html", "Kalender", aktuell))
    poster.append(undermeny("Om poolen", [("", poolsidor(kommuner))], aktuell))
    namn = lank("index.html", NAMN, aktuell, ' class="sajtnamn"')
    return (
        f'<nav class="sajtmeny" aria-label="Webbplatsen">{namn}'
        f"<ul>{''.join(poster)}</ul></nav>"
    )


# Översikten först, sedan organen i kommunfilens grupper; utskotten nås från
# sitt organ.
def organen(kommun: Kommun) -> list[Grupp]:
    oversikt = ("Översikt", [(f"{kommun.id}.html", "Alla organ")])
    return [oversikt] + [
        (namn, organlankar(kommun.id, i_gruppen))
        for namn, i_gruppen in grupperade(kommun)
    ]


def organlankar(kommun_id: str, organen: list[Organ]) -> list[tuple[str, str]]:
    return [(f"{kommun_id}/{o.id}.html", o.namn[0]) for o in organen if not o.hor_till]


def poolsidor(kommuner: list[Kommun]) -> list[tuple[str, str]]:
    status = [(statusadress(k.id), f"Poolens status – {k.namn}") for k in kommuner]
    return status + [(avvikelser.ADRESS, "Avvikelser")]


def statusadress(kommun_id: str) -> str:
    return f"{kommun_id}/status.html"


# En enda grupp utan namn blir en lista; annars står grupperna i kolumner.
def undermeny(rubrik: str, grupper: list[Grupp], aktuell: str) -> str:
    if len(grupper) == 1 and not grupper[0][0]:
        panel = lista(grupper[0][1], aktuell)
    else:
        kolumner = "".join(grupp(namn, lankar, aktuell) for namn, lankar in grupper)
        panel = f'<div class="grupper">{kolumner}</div>'
    return f"<li><details><summary>{escape(rubrik)}</summary>{panel}</details></li>"


def grupp(namn: str, lankar: list[tuple[str, str]], aktuell: str) -> str:
    return f'<div><p class="grupp">{escape(namn)}</p>{lista(lankar, aktuell)}</div>'


def lista(lankar: list[tuple[str, str]], aktuell: str) -> str:
    return (
        "<ul>"
        + "".join(post(adress, namn, aktuell) for adress, namn in lankar)
        + "</ul>"
    )


def post(adress: str, namn: str, aktuell: str) -> str:
    return f"<li>{lank(adress, namn, aktuell)}</li>"


def lank(adress: str, namn: str, aktuell: str, klass: str = "") -> str:
    markering = ' aria-current="page"' if adress == aktuell else ""
    upp = "../" * aktuell.count("/")
    return f'<a href="{upp}{adress}"{klass}{markering}>{escape(namn)}</a>'
