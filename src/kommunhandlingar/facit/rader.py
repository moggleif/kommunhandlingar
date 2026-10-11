"""Krav: K20 i docs/02-KRAV.md, ADR-0025. Test: tests/test_facit.py.

Hur en rad i en CSV jämförs med en rad i facit; reglerna står i
docs/03-ARKITEKTUR.md#facit-för-konverteringen.
"""

import re

from kommunhandlingar.konvertering.tabeller import TALRAD

SIFFROR = re.compile(r"\d+")
TECKEN_OCH_TAL = re.compile(r"^([-−–+]) (?=\d)")


def lika(rad: list[str], facitrad: list[str]) -> bool:
    if len(rad) != len(facitrad):
        return False
    for a, b in zip(map(cell, rad), map(cell, facitrad), strict=True):
        if (ar_tal(a) or ar_tal(b)) and a != b:
            return False
    egen, facits = bokstaver(rad), bokstaver(facitrad)
    if facits and not egen:
        return False
    return facits.startswith(egen) or facits.endswith(egen)


def cell(text: str) -> str:
    return TECKEN_OCH_TAL.sub(r"\1", " ".join(text.split()))


def ar_tal(text: str) -> bool:
    return TALRAD.fullmatch(text) is not None


def talrad(rad: list[str]) -> bool:
    return any(ar_tal(cell(c)) for c in rad)


def bokstaver(rad: list[str]) -> str:
    text = "".join(c for c in map(cell, rad) if not ar_tal(c))
    return "".join(t for t in text.lower() if t.isalpha())


def siffror(rader: list[list[str]]) -> list[str]:
    return [s for rad in rader for c in rad for s in SIFFROR.findall(c)]


def kolumnernas_siffror(rader: list[list[str]]) -> list[list[str]]:
    """Talen kolumn för kolumn uppifrån och ned, oavsett hur raderna delats."""
    bredd = max(map(len, rader), default=0)
    return [siffror([[r[j]] for r in rader if j < len(r)]) for j in range(bredd)]
