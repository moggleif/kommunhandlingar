"""Krav: K5 i docs/02-KRAV.md, ADR-0028 och ADR-0029. Test:
tests/test_sammanslagna.py.

En cells textrader och slag när en tabell med linjer delas (`delade.py`):
en cell inom en kolumn, eller en sammanslagen cell som går över flera
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import pairwise

from kommunhandlingar.konvertering.falt import Falt, falt, radvis
from kommunhandlingar.konvertering.tabeller import inom, mitt, siffra, talfalt

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
    def har_tal(self) -> bool:
        return med_tal(self.falt)


def med_tal(falt_: Iterable[str]) -> bool:
    """En siffra, eller ett streck som står för ett tal."""
    return any(siffra(f) or talfalt(f) for f in falt_)


def cellens(cell: tuple, ord_: list[dict], granser: tuple) -> tuple[str, list | None]:
    """Cellens slag och textrader med sin kolumn. En cell som går över
    flera kolumner delas efter fälten, när varje fält ligger inom en
    kolumn; en text som går över en gräns ger slaget `over`."""
    rader = radvis([o for o in ord_ if inom(mitt(o), cell)])
    falten = [(r[0]["top"], f) for r in rader for f in falt(r, True)]
    egen = kolumn(cell[0], cell[2], granser)
    if egen is not None:
        return "egen", textrader([(topp, egen, f) for topp, f in falten])
    placerade = [(topp, faltets(f, granser), f) for topp, f in falten]
    slag, ut = slaget(cell, textrader(placerade), granser)
    over = any(kolumn(f.x0, f.x1, granser) is None for _, f in falten)
    return ("over", ut) if over and ut is not None else (slag, ut)


def textrader(placerade: list[tuple]) -> list[tuple[int | None, Textrad]]:
    per_rad: dict[tuple[float, int | None], list[str]] = {}
    for topp, i, f in placerade:
        per_rad.setdefault((topp, i), []).append(f.text)
    return [(i, Textrad(topp, tuple(d))) for (topp, i), d in per_rad.items()]


def faltets(f: Falt, granser: tuple) -> int | None:
    """Fältets kolumn. En text utan siffror som går över en kolumngräns,
    som en rubrik över två kolumner, står i den första den täcker."""
    i = kolumn(f.x0, f.x1, granser)
    if i is None and not med_tal((f.text,)):
        return kolumn(f.x0, f.x0, granser)
    return i


def slaget(cell: tuple, ut: list[tuple], granser: tuple) -> tuple[str, list | None]:
    """`text` utan tal, `hel` över hela bredden, och för en cell med
    text i varje kolumn den täcker slaget enligt `fylld`. Annars är
    cellen sammanslagen med flit och går inte att dela."""
    kolumner = {i for i, _ in ut}
    if None in kolumner:
        return "", None
    if not any(r.har_tal for _, r in ut):
        return "text", ut
    tackta_kolumner = tackta(cell, granser)
    if tackta_kolumner == range(len(granser) - 1):
        return "hel", ut
    slag = fylld([r for _, r in ut]) if kolumner == set(tackta_kolumner) else ""
    return (slag, ut) if slag else ("", None)


def fylld(textrader_: list[Textrad]) -> str:
    """Slaget efter cellens rader på samma höjd: `rubrik` när någon rad
    har en siffra eller ett streck i varje fält och inget fält som bara
    är ett tal, som `Bokslut 2025`, annars `tal` när någon rad bara har
    tal. Övriga rader ska sakna tal; en rad som blandar går inte."""
    hojder: dict[float, list[str]] = {}
    for r in textrader_:
        hojder.setdefault(r.topp, []).extend(r.falt)
    slag = {radens(falt_) for falt_ in hojder.values()}
    if "" in slag:
        return ""
    return "rubrik" if "rubrik" in slag else "tal"


def radens(falt_: list[str]) -> str:
    if all(map(talfalt, falt_)):
        return "tal"
    if any(map(talfalt, falt_)):
        return ""
    return "rubrik" if med_tal(falt_) else "text"


def tackta(cell: tuple, granser: tuple) -> range:
    def narmast(x: float) -> int:
        return min(range(len(granser)), key=lambda i: abs(granser[i] - x))

    return range(narmast(cell[0]), narmast(cell[2]))


def kolumn(x0: float, x1: float, granser: tuple) -> int | None:
    for i, (vanster, hoger) in enumerate(pairwise(granser)):
        if vanster - I_LINJE <= x0 and x1 <= hoger + I_LINJE:
            return i
    return None
