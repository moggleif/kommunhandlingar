"""Krav: K5 i docs/02-KRAV.md, ADR-0016, ADR-0035 och ADR-0037. Test:
tests/test_olinjerade.py, tests/test_mellanrader.py och
tests/test_rubrikrader.py.

Raderna i en tabell utan lodräta linjer: vilka som bär tal, vilka som bara
är en etikett och vilka som står nära varandra
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

import re
from dataclasses import dataclass
from math import inf

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.text import ARTAL, TAL

I_LINJE = 2
RADMELLANRUM = 4
MEST_EMELLAN = 2
BOKSTAV = re.compile(r"[^\W\d_]")
STRECK = re.compile(r"[-−–]")


@dataclass(frozen=True)
class Rad:
    ord: list[dict]
    falt: list[Falt] | None

    @property
    def hojd(self) -> float:
        return max(o["bottom"] - o["top"] for o in self.ord)


def ar_tal(f: Falt) -> bool:
    return TAL.fullmatch(f.text) is not None


def ar_varde(f: Falt) -> bool:
    """Ett tal som inte är ett årtal, som i en rubrikrad."""
    return ar_tal(f) and not ARTAL.fullmatch(f.text)


def uppdela(falt_: list[Falt] | None) -> tuple[Falt, list[Falt]] | None:
    if not falt_ or len(falt_) < 2 or not BOKSTAV.search(falt_[0].text):
        return None
    etikett, *celler = falt_
    ok = all(ar_tal(f) or STRECK.fullmatch(f.text) for f in celler)
    return (etikett, celler) if ok else None


def delad(r: Rad) -> tuple[Falt, list[Falt]] | None:
    """Etiketten och cellerna; en etikettrad har inga celler."""
    return (r.falt[0], []) if etikettrad(r) else uppdela(r.falt)


def talrad(falt_: list[Falt]) -> bool:
    return sum(map(ar_tal, falt_)) >= 2


def har_tal(r: Rad) -> bool:
    if r.falt is None:
        return sum(1 for o in r.ord if TAL.fullmatch(o["text"])) >= 2
    return uppdela(r.falt) is not None or talrad(r.falt)


def mellanrum(ovre: Rad, undre: Rad) -> float:
    return min(o["top"] for o in undre.ord) - max(o["bottom"] for o in ovre.ord)


def nara(ovre: Rad, undre: Rad) -> bool:
    return mellanrum(ovre, undre) <= RADMELLANRUM * max(ovre.hojd, undre.hojd)


def artalsrad(r: Rad) -> bool:
    """En rubrikrad med bara årtal, som `2025 2026 2027`."""
    return r.falt is not None and all(ARTAL.fullmatch(f.text) for f in r.falt)


def bara_artal(r: Rad) -> bool:
    """En rad med tal där varje tal är ett årtal, som `Kommunen 2021 2022`."""
    tal = [f for f in r.falt or [] if ar_tal(f)]
    return bool(tal) and not any(map(ar_varde, tal))


def till_vanster(foljden: list[Rad], undre: Rad) -> bool:
    """Radens etikett börjar till vänster om följdens vänstraste tal, så att
    en sidfot med sidnummer, som börjar inne bland kolumnerna, inte blir en
    rad i tabellen."""
    tal = [f.x0 for r in foljden for f in r.falt or [] if ar_tal(f)]
    forsta = undre.falt[0] if undre.falt else None
    if forsta is None or not BOKSTAV.search(forsta.text):
        return True
    return forsta.x0 < min(tal, default=inf)


def etikettrad(r: Rad) -> bool:
    """En rad med bara en etikett, som en avsnittsrubrik."""
    falt_ = r.falt
    return falt_ is not None and len(falt_) == 1 and bool(BOKSTAV.search(falt_[0].text))


def med_fortsattning(rader_: list[Rad], slut: int) -> int:
    """Följdens slut efter de etikettrader med liten bokstav som står
    direkt under den, där etiketten på den sista raden fortsätter."""
    while slut < len(rader_) and fortsattning(rader_[slut - 1], rader_[slut]):
        slut += 1
    return slut


def fortsattning(ovre: Rad, undre: Rad) -> bool:
    liten = etikettrad(undre) and undre.falt[0].text[:1].islower()
    return liten and nara(ovre, undre)


def kolumn(f: Falt, kolumner_: list[tuple[float, float]]) -> int | None:
    traffar = [i for i, (_, x1) in enumerate(kolumner_) if abs(f.x1 - x1) <= I_LINJE]
    return traffar[0] if len(traffar) == 1 else None
