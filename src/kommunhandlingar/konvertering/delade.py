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

# Hur långt, i punkter, en kant eller ett fält får ligga från en kolumngräns.
I_LINJE = 2


@dataclass(frozen=True)
class Textrad:
    topp: float
    falt: tuple[str, ...]

    @property
    def text(self) -> str:
        return " ".join(self.falt)

    @property
    def har_siffra(self) -> bool:
        return any(c.isdigit() for c in self.text)


def tabell(t: Table, ord_: list[dict]) -> tuple[list, tuple] | None:
    """Raderna, och kolumnernas vänsterkanter och tabellens högerkant
    (K19); None när tabellen inte går att dela."""
    granser = kolumngranser(t)
    rader: list[list[str]] = []
    for nr, rad in enumerate(t.rows):
        platser = placera(rad.cells, ord_, granser)
        # Den första raden är rubriken; i de andra ska talen i en delad
        # cell stå på samma höjd.
        hojd = nr > 0 and any(
            kolumn(c[0], c[2], granser) is None for c in filter(None, rad.cells)
        )
        delrader = None if platser is None else dela(platser, hojd)
        if delrader is None:
            return None
        rader += delrader
    return rader, granser


def kolumngranser(t: Table) -> tuple[float, ...]:
    alla = sorted({x for c in t.cells for x in (c[0], c[2])})
    ut = [alla[0]]
    for x in alla[1:]:
        if x - ut[-1] > I_LINJE:
            ut.append(x)
    return tuple(ut)


def placera(celler: list, ord_: list[dict], granser: tuple) -> list | None:
    """Radens textrader per kolumn; None om en cell inte går att placera."""
    platser: list[list[Textrad]] = [[] for _ in granser[1:]]
    for cell in filter(None, celler):
        placerade = cellens(cell, ord_, granser)
        if placerade is None:
            return None
        for i, textrad in placerade:
            platser[i].append(textrad)
    return platser


def cellens(cell: tuple, ord_: list[dict], granser: tuple) -> list | None:
    """Cellens textrader med sin kolumn. En cell som går över flera
    kolumner delas efter fälten, när varje fält ligger inom en kolumn. Har
    den en siffra ska den också gå över hela tabellens bredd, eller ha en
    siffra i varje textrad och text i varje kolumn den täcker; annars är
    den sammanslagen med flit."""
    egen = kolumn(cell[0], cell[2], granser)
    per_rad: dict[tuple[float, int | None], list[str]] = {}
    rader = radvis([o for o in ord_ if inom(mitt(o), cell)])
    for topp, f in ((r[0]["top"], f) for r in rader for f in falt(r, True)):
        i = egen if egen is not None else kolumn(f.x0, f.x1, granser)
        per_rad.setdefault((topp, i), []).append(f.text)
    ut = [(i, Textrad(topp, tuple(d))) for (topp, i), d in per_rad.items()]
    return ut if egen is not None or delbar(cell, ut, granser) else None


def delbar(cell: tuple, ut: list[tuple], granser: tuple) -> bool:
    kolumner = {i for i, _ in ut}
    if None in kolumner:
        return False
    tackta_kolumner = tackta(cell, granser)
    if not any(r.har_siffra for _, r in ut):
        return True
    if tackta_kolumner == range(len(granser) - 1):
        return True
    alla = all(r.har_siffra for _, r in ut)
    return alla and kolumner == set(tackta_kolumner)


def tackta(cell: tuple, granser: tuple) -> range:
    def narmast(x: float) -> int:
        return min(range(len(granser)), key=lambda i: abs(granser[i] - x))

    return range(narmast(cell[0]), narmast(cell[2]))


def kolumn(x0: float, x1: float, granser: tuple) -> int | None:
    for i, (vanster, hoger) in enumerate(pairwise(granser)):
        if vanster - I_LINJE <= x0 and x1 <= hoger + I_LINJE:
            return i
    return None


def dela(platser: list[list[Textrad]], hojd: bool) -> list[list[str]] | None:
    """Raden som den står när ingen cell rymmer mer än ett tal, och med
    `hojd` när talen står på samma höjd; annars delad nerifrån. None när
    det inte går ihop."""
    if not flera(platser):
        return [celler(platser)] if not hojd or talen_i_hojd(platser) else None
    return nerifran(platser)


def nerifran(platser: list[list[Textrad]]) -> list[list[str]] | None:
    """Den nedersta textraden blir en egen rad när den står på samma höjd
    i varje cell som inte är tom. Det som står ovanför blir en rad när
    varje textrad med en siffra står på samma höjd som en textrad i
    varje cell."""
    if not any(platser):
        return []
    if not flera(platser):
        return [celler(platser)] if talen_i_hojd(platser) else None
    sista = [p[-1].topp for p in platser if p]
    nederst = [p[-1:] for p in platser]
    if max(sista) - min(sista) > RADTOLERANS or flera(nederst):
        return None
    ovanfor = nerifran([p[:-1] for p in platser])
    return None if ovanfor is None else [*ovanfor, celler(nederst)]


def talen_i_hojd(platser: list[list[Textrad]]) -> bool:
    hojder = [r.topp for p in platser for r in p if r.har_siffra]
    if not hojder:
        return True
    if max(hojder) - min(hojder) > RADTOLERANS:
        return False
    return all(
        any(abs(r.topp - hojder[0]) <= RADTOLERANS for r in p) for p in platser if p
    )


def celler(platser: list[list[Textrad]]) -> list[str]:
    return ["\n".join(r.text for r in p) for p in platser]


def flera(platser: list[list[Textrad]]) -> bool:
    """Mer än ett tal i någon cell, efter cellens text eller dess fält."""
    if any(map(flera_tal, celler(platser))):
        return True
    rader = (r for p in platser for r in p)
    return any(sum(1 for f in r.falt if TALRAD.fullmatch(f)) > 1 for r in rader)
