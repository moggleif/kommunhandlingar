"""Krav: K5 i docs/02-KRAV.md, ADR-0028. Test: tests/test_delade.py.

En tabell med linjer där en cell rymmer mer än ett tal delas, i stället
för att fällas, när det går ihop: kolumnerna efter de lodräta linjer som
finns i någon rad, och raderna efter rutornas textrader
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

from dataclasses import dataclass
from itertools import pairwise

from pdfplumber.table import Table

from kommunhandlingar.konvertering.falt import RADTOLERANS, falt, radvis
from kommunhandlingar.konvertering.tabeller import TALRAD, flera_tal, inom, mitt

I_LINJE = 2


@dataclass(frozen=True)
class Textrad:
    topp: float
    falt: tuple[str, ...]

    @property
    def text(self) -> str:
        return " ".join(self.falt)


@dataclass(frozen=True)
class Delad:
    bbox: tuple[float, float, float, float]
    rader: list[list[str]]
    # Kolumnernas vänsterkanter och tabellens högerkant (K19).
    kanter: tuple[float, ...]


def tabell(t: Table, ord_: list[dict]) -> Delad | None:
    kanter_ = kanter(t)
    rader: list[list[str]] = []
    for rad in t.rows:
        platser = placera(rad.cells, ord_, kanter_)
        delrader = None if platser is None else dela(platser)
        if delrader is None:
            return None
        rader += delrader
    return Delad(t.bbox, rader, kanter_)


def kanter(t: Table) -> tuple[float, ...]:
    """Varje cells vänster- och högerkant i hela tabellen, de som ligger
    inom 2 punkter från varandra som en."""
    alla = sorted({x for c in t.cells for x in (c[0], c[2])})
    ut = [alla[0]]
    for x in alla[1:]:
        if x - ut[-1] > I_LINJE:
            ut.append(x)
    return tuple(ut)


def placera(celler, ord_: list[dict], kanter_: tuple) -> list[list[Textrad]] | None:
    """Radens textrader per kolumn; None om ett fält går över en kant."""
    platser: list[list[Textrad]] = [[] for _ in kanter_[1:]]
    for cell in filter(None, celler):
        for i, textrad in cellens(cell, ord_, kanter_):
            if i is None:
                return None
            platser[i].append(textrad)
    return platser


def cellens(cell: tuple, ord_: list[dict], kanter_: tuple) -> list[tuple]:
    """Cellens textrader med sin kolumn. En cell som går över flera
    kolumner delas efter fälten."""
    egen = kolumn(cell[0], cell[2], kanter_)
    ut = []
    for rad in radvis([o for o in ord_ if inom(mitt(o), cell)]):
        per_kolumn: dict[int | None, list[str]] = {}
        for f in falt(rad, dela_tvetydiga=True):
            i = kolumn(f.x0, f.x1, kanter_) if egen is None else egen
            per_kolumn.setdefault(i, []).append(f.text)
        ut += [(i, Textrad(rad[0]["top"], tuple(d))) for i, d in per_kolumn.items()]
    return ut


def kolumn(x0: float, x1: float, kanter_: tuple) -> int | None:
    for i, (vanster, hoger) in enumerate(pairwise(kanter_)):
        if vanster - I_LINJE <= x0 and x1 <= hoger + I_LINJE:
            return i
    return None


def dela(platser: list[list[Textrad]]) -> list[list[str]] | None:
    """Raden som den står, eller delad nerifrån: den nedersta textraden
    blir en egen rad när den står på samma höjd i varje ruta som inte är
    tom. None när en cell ändå rymmer mer än ett tal."""
    if not any(platser):
        return []
    if not flera(platser):
        return [celler(platser)]
    sista = [p[-1].topp for p in platser if p]
    nederst = [p[-1:] for p in platser]
    if max(sista) - min(sista) > RADTOLERANS or flera(nederst):
        return None
    ovanfor = dela([p[:-1] for p in platser])
    return None if ovanfor is None else [*ovanfor, celler(nederst)]


def celler(platser: list[list[Textrad]]) -> list[str]:
    return ["\n".join(r.text for r in p) for p in platser]


def flera(platser: list[list[Textrad]]) -> bool:
    """Mer än ett tal i någon cell, efter cellens text eller dess fält."""
    if any(map(flera_tal, celler(platser))):
        return True
    rader = (r for p in platser for r in p)
    return any(sum(1 for f in r.falt if TALRAD.fullmatch(f)) > 1 for r in rader)
