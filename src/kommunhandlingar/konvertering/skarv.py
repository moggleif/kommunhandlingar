"""Krav: K19 i docs/02-KRAV.md, ADR-0024. Test: tests/test_skarvar.py.

Det en sida lästa ur textlagret behöver visa för att dess tabeller ska
kunna slås ihop med grannsidornas (docs/03-ARKITEKTUR.md#tabeller-över-flera-sidor):
kolumngränserna på den första och den sista tabellen, och sidans
textrader utanför tabellerna som läge och text utan siffror, så att
sidhuvud och sidfot känns igen på andra sidor. Raderna jämförs bara och
skrivs aldrig, så de behöver inte maskas.
"""

import re
from dataclasses import dataclass

from pdfplumber.page import Page

SIFFROR = re.compile(r"\d+")

# En textrad: överkanten avrundad till hela punkter, och texten utan siffror.
Rad = tuple[int, str]


@dataclass(frozen=True)
class Skarv:
    rader: frozenset[Rad]
    forsta: tuple[float, ...] = ()
    sista: tuple[float, ...] = ()
    ovanfor: tuple[Rad, ...] = ()
    nedanfor: tuple[Rad, ...] = ()


def skarv(utanfor: Page, tabeller: list[tuple[tuple, tuple]]) -> Skarv:
    """`utanfor` är sidan utan tabellernas tecken, `tabeller` varje tabells
    ruta och kolumngränser i sidans ordning."""
    linjer = utanfor.extract_text_lines()
    rader = frozenset(rad(t) for t in linjer)
    if not tabeller:
        return Skarv(rader)
    (forsta, kanter_forsta), (sista, kanter_sista) = tabeller[0], tabeller[-1]
    return Skarv(
        rader,
        kanter_forsta,
        kanter_sista,
        tuple(rad(t) for t in linjer if t["bottom"] <= forsta[1]),
        tuple(rad(t) for t in linjer if t["top"] >= sista[3]),
    )


def rad(linje: dict) -> Rad:
    return round(linje["top"]), " ".join(SIFFROR.sub("", linje["text"]).split())
