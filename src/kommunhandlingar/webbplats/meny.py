"""Krav: K58 i docs/02-KRAV.md, ADR-0081. Test: tests/test_navigering.py.

Webbplatsens meny i den gemensamma form som Giffå ritar (ADR-0081): poolens
namn och högst sex poster, där en post är en länk eller en undermeny. Varje
kommun får en enda post: en undermeny med översikten, kalendern och
statussidan och sedan organen i kommunfilens grupper. Sist står avvikelserna.
Så ryms fem kommuner.
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
    poster = [undermeny(k.namn, sidorna(k, kalendrar), aktuell) for k in kommuner]
    poster.append(post(avvikelser.ADRESS, "Avvikelser", aktuell))
    namn = lank("index.html", NAMN, aktuell).replace("<a ", '<a class="sajtnamn" ', 1)
    return (
        f'<nav class="sajtmeny" aria-label="Webbplatsen">{namn}'
        f"<ul>{''.join(poster)}</ul></nav>"
    )


# Översikten först, sedan organen i kommunfilens grupper; utskotten nås från
# sitt organ. En kommunfil utan grupper får gruppen "Organen".
def sidorna(kommun: Kommun, kalendrar: frozenset[str]) -> list[Grupp]:
    return [("Översikt", oversikt(kommun.id, kalendrar))] + [
        (namn or "Organen", organlankar(kommun.id, i_gruppen))
        for namn, i_gruppen in grupperade(kommun)
    ]


def oversikt(kommun_id: str, kalendrar: frozenset[str]) -> list[tuple[str, str]]:
    kalender = [(f"{kommun_id}/kalender.html", "Kalender")]
    return (
        [(f"{kommun_id}.html", "Alla organ")]
        + (kalender if kommun_id in kalendrar else [])
        + [(statusadress(kommun_id), "Poolens status")]
    )


def organlankar(kommun_id: str, organen: list[Organ]) -> list[tuple[str, str]]:
    return [(f"{kommun_id}/{o.id}.html", o.namn[0]) for o in organen if not o.hor_till]


def statusadress(kommun_id: str) -> str:
    return f"{kommun_id}/status.html"


def undermeny(rubrik: str, grupper: list[Grupp], aktuell: str) -> str:
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


def lank(adress: str, namn: str, aktuell: str) -> str:
    markering = ' aria-current="page"' if adress == aktuell else ""
    upp = "../" * aktuell.count("/")
    return f'<a href="{upp}{adress}"{markering}>{escape(namn)}</a>'
