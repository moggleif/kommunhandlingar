"""Krav: K19 i docs/02-KRAV.md, ADR-0024. Test: tests/test_skarvar.py.

Det en sida behöver visa för att dess tabeller ska kunna slås ihop med
grannsidornas: kanterna på den första och den sista tabellen, textraderna
ovanför den första och under den sista, och alla sidans textrader utan
siffror, så att sidhuvud och sidfot känns igen på grannsidan
(docs/03-ARKITEKTUR.md#tabeller-över-flera-sidor).
"""

import re
from dataclasses import dataclass

from pdfplumber.page import Page

BOKSTAV = re.compile(r"[^\W\d_]")
SIFFROR = re.compile(r"\d+")


@dataclass(frozen=True)
class Skarv:
    forsta: tuple[float, float]
    sista: tuple[float, float]
    ovanfor: list[str]
    nedanfor: list[str]
    utan_siffror: frozenset[str]


def skarv(utanfor: Page, rutor: list[tuple]) -> Skarv | None:
    """`utanfor` är sidan utan tabellernas tecken, `rutor` tabellerna i
    sidans ordning."""
    if not rutor:
        return None
    rader = utanfor.extract_text_lines()
    forsta, sista = rutor[0], rutor[-1]
    return Skarv(
        (forsta[0], forsta[2]),
        (sista[0], sista[2]),
        [r["text"] for r in rader if r["bottom"] <= forsta[1]],
        [r["text"] for r in rader if r["top"] >= sista[3]],
        frozenset(utan_siffror(r["text"]) for r in rader),
    )


def utan_siffror(rad: str) -> str:
    return " ".join(SIFFROR.sub("", rad).split())


def ar_marginal(rad: str, granne: Skarv) -> bool:
    """Ett sidnummer, eller en rad som står på grannsidan när siffrorna
    inte räknas."""
    return not BOKSTAV.search(rad) or utan_siffror(rad) in granne.utan_siffror
