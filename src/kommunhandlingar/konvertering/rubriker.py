"""Krav: K5 i docs/02-KRAV.md, ADR-0016, ADR-0035, ADR-0037 och ADR-0040.
Test: tests/test_olinjerade.py, tests/test_mellanrader.py,
tests/test_rubrikrader.py och tests/test_spann.py.

Rubrikraderna ovanför en tabell utan lodräta linjer: kolumnrubrikerna och
de avsnittsrubriker som står mellan dem och de första talen
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

from itertools import pairwise

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.rader import MEST_EMELLAN, Rad, ar_varde, nara
from kommunhandlingar.konvertering.spann import Celler, Fack, rubrikceller, rubrikrad


def ovanfor(rader_: list[Rad], fack: Fack) -> tuple[list[list[str]], list[Rad]]:
    """Cellerna och textraderna för rubriken och högst två avsnittsrubriker
    närmast ovanför tabellen. Avsnittsrubrikerna tas med bara när rubriken
    finns."""
    n = 0
    while n < min(MEST_EMELLAN, len(rader_) - 1) and ensam_ovanfor(rader_, n, fack):
        n += 1
    huvud = huvudet(rader_[: len(rader_) - n], fack)
    celler = rubrikceller(huvud, len(fack.kolumner)) if huvud else None
    if not celler:
        return [], []
    avsnitt = rader_[-1 - n : -1]
    tomma = [""] * len(fack.kolumner)
    rader_i_huvudet = [r for r, _ in huvud]
    return celler + [
        [r.falt[0].text, *tomma] for r in avsnitt
    ], rader_i_huvudet + avsnitt


def ensam_ovanfor(rader_: list[Rad], n: int, fack: Fack) -> bool:
    ovre, undre = rader_[-2 - n], rader_[-1 - n]
    return bara_etikett(ovre.falt, fack) and nara(ovre, undre)


def huvudet(rader_: list[Rad], fack: Fack) -> list[tuple[Rad, Celler]]:
    """Rubrikens textrader med sina celler, uppåt till en rad med värden,
    som en tabell ovanför, eller en rad text ovanför; annars inga, så att
    rubriken aldrig blir halv."""
    huvud: list[tuple[Rad, Celler]] = []
    for ovre, undre in reversed(list(pairwise(rader_))):
        if not nara(ovre, undre) or any(map(ar_varde, ovre.falt or [])):
            break
        celler = rubrikrad(ovre, fack)
        if celler is None:
            return [] if not ensam_text(ovre.falt, fack) else huvud
        huvud.insert(0, (ovre, celler))
    return huvud


def ensam_text(falt_: list[Falt] | None, fack: Fack) -> bool:
    """Ett ensamt fält som slutar före kolumnerna eller börjar bland
    etiketterna, som en rubrik eller löptext ovanför tabellen, och inte en
    del av kolumnrubriken."""
    return bara_etikett(falt_, fack) or (
        falt_ is not None and len(falt_) == 1 and falt_[0].x0 < fack.etiketternas_slut
    )


def bara_etikett(falt_: list[Falt] | None, fack: Fack) -> bool:
    return falt_ is not None and len(falt_) == 1 and falt_[0].x1 < fack.kolumner[0][0]
