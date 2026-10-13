"""Krav: K5 i docs/02-KRAV.md, ADR-0016, ADR-0035 och ADR-0037. Test:
tests/test_olinjerade.py, tests/test_mellanrader.py och
tests/test_rubrikrader.py.

Rubrikraderna ovanför en tabell utan lodräta linjer: kolumnrubrikerna och
de avsnittsrubriker som står mellan dem och de första talen
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

from itertools import pairwise

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.rader import (
    MEST_EMELLAN,
    Rad,
    ar_varde,
    kolumn,
    nara,
)


def ovanfor(rader_: list[Rad], kolumner_: list, etiketternas_slut: float):
    """Högst två avsnittsrubriker närmast ovanför tabellen, och rubriken
    över dem. Avsnittsrubrikerna tas med bara när rubriken finns."""
    n = 0
    while n < min(MEST_EMELLAN, len(rader_) - 1) and ensam_ovanfor(
        rader_, n, kolumner_
    ):
        n += 1
    huvud = huvudet(rader_[: len(rader_) - n], kolumner_, etiketternas_slut)
    tomma = [""] * len(kolumner_)
    rubriker = [[r.falt[0].text, *tomma] for r in rader_[-1 - n : -1]]
    return (rubriker if huvud else []), huvud


def ensam_ovanfor(rader_: list[Rad], n: int, kolumner_: list) -> bool:
    ovre, undre = rader_[-2 - n], rader_[-1 - n]
    return bara_etikett(ovre.falt, kolumner_) and nara(ovre, undre)


def huvudet(rader_: list[Rad], kolumner_: list, etiketternas_slut: float) -> list:
    """Rubrikraderna uppåt till en rad med värden, som en tabell ovanför,
    eller en rad text ovanför; annars ingen, så att rubriken aldrig blir halv."""
    huvud: list[list[str]] = []
    for ovre, undre in reversed(list(pairwise(rader_))):
        if not nara(ovre, undre) or any(map(ar_varde, ovre.falt or [])):
            break
        rubrik = huvudrad(ovre.falt, kolumner_, etiketternas_slut)
        if rubrik is None:
            if not ensam_text(ovre.falt, kolumner_, etiketternas_slut):
                return []
            break
        huvud.insert(0, rubrik)
    return huvud if not huvud or all(huvud[0][1:]) else []


def huvudrad(falt_: list[Falt] | None, kolumner_: list, etiketternas_slut: float):
    if not falt_:
        return None
    rubrik = [""] * (len(kolumner_) + 1)
    forsta = falt_[0]
    if forsta.x0 < etiketternas_slut and forsta.x1 < kolumner_[0][0]:
        rubrik[0], falt_ = forsta.text, falt_[1:]
    granser = [etiketternas_slut] + [x1 for _, x1 in kolumner_]
    for f in falt_:
        i = kolumn(f, kolumner_)
        if i is None or f.x0 <= granser[i]:
            return None
        rubrik[i + 1] = f.text
    return rubrik if any(rubrik[1:]) else None


def ensam_text(falt_: list[Falt] | None, kolumner_: list, slut: float) -> bool:
    """Ett ensamt fält som slutar före kolumnerna eller börjar bland
    etiketterna, som en rubrik eller löptext ovanför tabellen, och inte en
    del av kolumnrubriken."""
    return bara_etikett(falt_, kolumner_) or (
        falt_ is not None and len(falt_) == 1 and falt_[0].x0 < slut
    )


def bara_etikett(falt_: list[Falt] | None, kolumner_: list) -> bool:
    return falt_ is not None and len(falt_) == 1 and falt_[0].x1 < kolumner_[0][0]
