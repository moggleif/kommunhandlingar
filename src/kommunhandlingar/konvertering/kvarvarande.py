"""Krav: K5 i docs/02-KRAV.md, ADR-0033. Test: tests/test_kvarvarande.py.

Talrader som står i linje med varandra men inte blev någon tabell, som en
tabell i en spalt bredvid löptext. Raderna delar textrad med spalten
bredvid, så de läses varken som en tabell utan lodräta linjer eller som en
osäker tabell i sidans text. Tre sådana rader gör sidan `tabell-osaker`
(docs/03-ARKITEKTUR.md#konvertering-och-kvalitet).
"""

from pdfplumber.page import Page

from kommunhandlingar.konvertering.falt import falt, radvis
from kommunhandlingar.konvertering.olinjerade import AR_ELLER_KOD, I_LINJE, ar_tal
from kommunhandlingar.konvertering.tabeller import inom, mitt
from kommunhandlingar.konvertering.text import MINSTA_FOLJD


def finns(sida: Page, rutor: list[tuple]) -> bool:
    ord_ = sida.extract_words(extra_attrs=["size"])
    fria = [o for o in ord_ if not any(inom(mitt(o), r) for r in rutor)]
    rader = [k for r in radvis(fria) if len(k := talkanter(r)) >= 2]
    return any(sum(i_linje(a, b) for b in rader) >= MINSTA_FOLJD for a in rader)


def talkanter(rad: list[dict]) -> list[float]:
    """Högerkanten på radens tal. Ett år eller en kod är inget värde."""
    falt_ = falt(rad, dela_tvetydiga=True)
    return [f.x1 for f in falt_ if ar_tal(f) and not AR_ELLER_KOD.fullmatch(f.text)]


def i_linje(a: list[float], b: list[float]) -> bool:
    return sum(any(abs(x - y) <= I_LINJE for y in b) for x in a) >= 2
