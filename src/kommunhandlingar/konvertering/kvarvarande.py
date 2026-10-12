"""Krav: K5 i docs/02-KRAV.md, ADR-0033. Test: tests/test_kvarvarande.py.

Talrader i linje som inte blev någon tabell, som en tabell i en spalt
bredvid löptext (docs/03-ARKITEKTUR.md#konvertering-och-kvalitet). Orden
delas som i tabellerna utan lodräta linjer.
"""

from pdfplumber.page import Page

from kommunhandlingar.konvertering.falt import falt, radvis
from kommunhandlingar.konvertering.olinjerade import fria
from kommunhandlingar.konvertering.rader import I_LINJE, ar_varde

ANDRA_RADER = 2


def har_talrader(sida: Page, rutor: list[tuple]) -> bool:
    ord_ = fria(sida.extract_words(extra_attrs=["size"]), rutor)
    rader = [k for r in radvis(ord_) if len(k := talkanter(r)) >= 2]
    return any(
        sum(i_linje(a, b) for b in rader if b is not a) >= ANDRA_RADER for a in rader
    )


def talkanter(rad: list[dict]) -> list[float]:
    falt_ = falt(rad, dela_tvetydiga=True)
    return [f.x1 for f in falt_ if ar_varde(f)]


def i_linje(a: list[float], b: list[float]) -> bool:
    return sum(any(abs(x - y) <= I_LINJE for y in b) for x in a) >= 2
