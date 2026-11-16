"""Krav: K51 och K58 i docs/02-KRAV.md, ADR-0081 och ADR-0082. Test:
tests/test_navigering.py.

Webbplatsens meny i den gemensamma form som Giffå ritar (ADR-0081): sajtens
namn och högst sex poster, där en post är en länk eller en undermeny. Med
flera kommuner får varje kommun en enda post: en undermeny med översikten,
kalendern och statussidan och sedan organen i kommunfilens grupper, och sist
står avvikelserna. Så ryms fem kommuner. En pool med en enda kommun heter som
den, och då är kommunfilens grupper själva posterna (ADR-0082): kalendern,
en undermeny per grupp och sist *Om poolen*. Översikten är då startsidan.
Knappen för mörkt tema står sist i menyn.
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


EN_KOMMUN = "Handlingar och protokoll"
TEMAKNAPP = '<button type="button" class="tema" hidden>Mörkt tema</button>'


def meny(kommuner: list[Kommun], kalendrar: frozenset[str], aktuell: str) -> str:
    if len(kommuner) == 1:
        poster = en_kommuns_poster(kommuner[0], kalendrar, aktuell)
    else:
        poster = [undermeny(k.namn, sidorna(k, kalendrar), aktuell) for k in kommuner]
        poster.append(post(avvikelser.ADRESS, "Avvikelser", aktuell))
    namn = lank("index.html", sajtnamn(kommuner), aktuell).replace(
        "<a ", '<a class="sajtnamn" ', 1
    )
    return (
        f'<nav class="sajtmeny" aria-label="Webbplatsen">{namn}'
        f"<ul>{''.join(poster)}</ul>{TEMAKNAPP}</nav>"
    )


def en_kommuns_poster(
    kommun: Kommun, kalendrar: frozenset[str], aktuell: str
) -> list[str]:
    kalender = f"{kommun.id}/kalender.html"
    kalenderpost = (
        [post(kalender, "Kalender", aktuell)] if kommun.id in kalendrar else []
    )
    om_poolen = [
        (statusadress(kommun.id), "Poolens status"),
        (avvikelser.ADRESS, "Avvikelser"),
    ]
    return (
        kalenderpost
        + [
            enkel_undermeny(namn or "Organen", organlankar(kommun.id, organen), aktuell)
            for namn, organen in grupperade(kommun)
        ]
        + [enkel_undermeny("Om poolen", om_poolen, aktuell)]
    )


# Med en enda kommun upprepar varken översiktens namn eller en rubrik
# kommunens namn, som är sajtens (ADR-0082).
def oversiktsnamn(kommuner: list[Kommun], kommun: Kommun) -> str:
    return EN_KOMMUN if len(kommuner) == 1 else kommun.namn


def kommunens(kommuner: list[Kommun], rubrik: str, kommun: Kommun) -> str:
    return rubrik if len(kommuner) == 1 else f"{rubrik} – {kommun.namn}"


# En pool med en enda kommun, som Kungsbackas eller regionens datarepo, heter
# som den.
def sajtnamn(kommuner: list[Kommun]) -> str:
    return kommuner[0].namn if len(kommuner) == 1 else NAMN


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
    return utfallbar(rubrik, f'<div class="grupper">{kolumner}</div>')


def enkel_undermeny(rubrik: str, lankar: list[tuple[str, str]], aktuell: str) -> str:
    return utfallbar(rubrik, lista(lankar, aktuell))


def utfallbar(rubrik: str, panel: str) -> str:
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
