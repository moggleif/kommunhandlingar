"""Krav: K5 i docs/02-KRAV.md, ADR-0016 och ADR-0035. Test: tests/test_olinjerade.py.

Raderna i en tabell utan lodräta linjer: vilka som bär tal, vilka som bara
är en etikett och vilka som står nära varandra
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

import re
from dataclasses import dataclass

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.text import ARTAL, TAL

I_LINJE = 2
RADMELLANRUM = 3
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


def nara(ovre: Rad, undre: Rad) -> bool:
    mellanrum = min(o["top"] for o in undre.ord) - max(o["bottom"] for o in ovre.ord)
    return mellanrum <= RADMELLANRUM * max(ovre.hojd, undre.hojd)


def artalsrad(r: Rad) -> bool:
    """En rubrikrad med bara årtal, som `2025 2026 2027`."""
    return r.falt is not None and all(ARTAL.fullmatch(f.text) for f in r.falt)


def etikettrad(r: Rad) -> bool:
    return r.falt is not None and len(r.falt) == 1 and BOKSTAV.search(r.falt[0].text)


def kolumn(f: Falt, kolumner_: list[tuple[float, float]]) -> int | None:
    traffar = [i for i, (_, x1) in enumerate(kolumner_) if abs(f.x1 - x1) <= I_LINJE]
    return traffar[0] if len(traffar) == 1 else None
