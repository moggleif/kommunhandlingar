"""Krav: K19 i docs/02-KRAV.md, ADR-0024. Test: tests/test_skarvar.py.

Det en sida lästa ur textlagret behöver visa för att dess tabeller ska
kunna slås ihop med grannsidornas (docs/03-ARKITEKTUR.md#tabeller-över-flera-sidor):
kolumngränserna på den första och den sista tabellen, om den sista slutar
i sidans nedersta fjärdedel, raderna ovanför den första och under den
sista, och raderna i sidans marginaler, så att sidhuvud och sidfot känns
igen på andra sidor. En rad är läget och texten utan siffror. Raderna
jämförs bara och skrivs aldrig, så de behöver inte maskas.
"""

import re
from dataclasses import dataclass

from pdfplumber.page import Page

SIFFROR = re.compile(r"\d+")
MARGINAL = 0.1
NEDERSTA = 0.75

# En textrad: överkanten avrundad till hela punkter, och texten utan siffror.
Rad = tuple[int, str]


@dataclass(frozen=True)
class Skarv:
    marginalen: frozenset[Rad]
    forsta: tuple[float, ...] = ()
    sista: tuple[float, ...] = ()
    ovanfor: tuple[Rad, ...] = ()
    nedanfor: tuple[Rad, ...] = ()
    sista_nederst: bool = False


def skarv(utanfor: Page, tabeller: list[tuple[tuple, tuple]]) -> Skarv:
    """`utanfor` är sidan utan tabellernas tecken, `tabeller` varje tabells
    ruta och kolumngränser i sidans ordning."""
    linjer = utanfor.extract_text_lines()
    hojd = utanfor.height
    marginalen = frozenset(
        rad(t) for t in linjer if not MARGINAL * hojd < t["top"] < (1 - MARGINAL) * hojd
    )
    if not tabeller:
        return Skarv(marginalen)
    (forsta, kanter_forsta), (sista, kanter_sista) = tabeller[0], tabeller[-1]
    return Skarv(
        marginalen,
        kanter_forsta,
        kanter_sista,
        tuple(rad(t) for t in linjer if t["bottom"] <= forsta[1]),
        tuple(rad(t) for t in linjer if t["top"] >= sista[3]),
        sista[3] >= NEDERSTA * hojd,
    )


def rad(linje: dict) -> Rad:
    return round(linje["top"]), " ".join(SIFFROR.sub("", linje["text"]).split())
