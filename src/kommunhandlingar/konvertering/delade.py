"""Krav: K5 i docs/02-KRAV.md, ADR-0028. Test: tests/test_delade.py och
tests/test_delade_kolumner.py.

En tabell med linjer där en cell rymmer mer än ett tal delas, i stället
för att fällas, när det går ihop: kolumnerna efter de lodräta linjer som
finns i någon rad, och raderna efter rutornas textrader
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

from dataclasses import dataclass
from itertools import pairwise

from pdfplumber.table import Table

from kommunhandlingar.konvertering.falt import RADTOLERANS, falt, radvis
from kommunhandlingar.konvertering.tabeller import flera_tal, inom, mitt, talfalt

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
        """En siffra, eller ett streck som står för ett tal."""
        siffra = any(c.isdigit() for c in self.text)
        return siffra or any(map(talfalt, self.falt))


def tabell(t: Table, ord_: list[dict]) -> tuple[list, tuple] | None:
    """Raderna, och kolumnernas vänsterkanter och tabellens högerkant
    (K19); None när tabellen inte går att dela."""
    if any(over_linje(o, t.cells) for o in ord_ if inom(mitt(o), t.bbox)):
        return None
    granser = kolumngranser(t)
    rader: list[list[str]] = []
    for nr, rad in enumerate(t.rows):
        placerat = placera(rad.cells, ord_, granser)
        delrader = None if placerat is None else dela(*placerat, forsta=nr == 0)
        if delrader is None:
            return None
        rader += delrader
    return rader, granser


def over_linje(o: dict, celler: list[tuple]) -> bool:
    """Ett ord vars tecken står i olika celler, som en etikett i ett
    diagram vars rutnät pdfplumber läser som en tabell."""
    i_celler = {
        next((i for i, c in enumerate(celler) if inom(mitt(t), c)), None)
        for t in o["chars"]
    }
    return len(i_celler - {None}) > 1


def kolumngranser(t: Table) -> tuple[float, ...]:
    alla = sorted({x for c in t.cells for x in (c[0], c[2])})
    ut = [alla[0]]
    for x in alla[1:]:
        if x - ut[-1] > I_LINJE:
            ut.append(x)
    return tuple(ut)


def placera(celler: list, ord_: list[dict], granser: tuple) -> tuple | None:
    """Radens textrader per kolumn och vilka slags celler den har; None
    om en cell inte går att placera."""
    platser: list[list[Textrad]] = [[] for _ in granser[1:]]
    slag = set()
    for cell in filter(None, celler):
        cellens_slag, placerade = cellens(cell, ord_, granser)
        if placerade is None:
            return None
        slag.add(cellens_slag)
        for i, textrad in placerade:
            platser[i].append(textrad)
    return platser, slag


def cellens(cell: tuple, ord_: list[dict], granser: tuple) -> tuple[str, list | None]:
    """Cellens slag och textrader med sin kolumn. En cell som går över
    flera kolumner delas efter fälten, när varje fält ligger inom en
    kolumn."""
    egen = kolumn(cell[0], cell[2], granser)
    per_rad: dict[tuple[float, int | None], list[str]] = {}
    rader = radvis([o for o in ord_ if inom(mitt(o), cell)])
    for topp, f in ((r[0]["top"], f) for r in rader for f in falt(r, True)):
        i = egen if egen is not None else kolumn(f.x0, f.x1, granser)
        per_rad.setdefault((topp, i), []).append(f.text)
    ut = [(i, Textrad(topp, tuple(d))) for (topp, i), d in per_rad.items()]
    return ("egen", ut) if egen is not None else slaget(cell, ut, granser)


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


def fylld(textrader: list[Textrad]) -> str:
    """`tal` när varje fält är ett tal, `rubrik` när varje textrad har en
    siffra eller ett streck och inget fält är bara ett tal, som
    `Bokslut 2025`."""
    tal = [talfalt(f) for r in textrader for f in r.falt]
    if all(tal):
        return "tal"
    return "rubrik" if all(r.har_tal for r in textrader) and not any(tal) else ""


def tackta(cell: tuple, granser: tuple) -> range:
    def narmast(x: float) -> int:
        return min(range(len(granser)), key=lambda i: abs(granser[i] - x))

    return range(narmast(cell[0]), narmast(cell[2]))


def kolumn(x0: float, x1: float, granser: tuple) -> int | None:
    for i, (vanster, hoger) in enumerate(pairwise(granser)):
        if vanster - I_LINJE <= x0 and x1 <= hoger + I_LINJE:
            return i
    return None


def dela(platser: list[list[Textrad]], slag: set[str], forsta: bool) -> list | None:
    """Raden som den står när ingen cell rymmer mer än ett tal, annars
    delad nerifrån; None när det inte går ihop. En rubrikcell får bara
    stå i första raden. En rad med en delad cell ska ha sina tal på samma
    höjd, utom i första raden när den första kolumnen har högst en
    textrad: då antas den vara en rubrik i flera rader."""
    if "rubrik" in slag and not forsta:
        return None
    if flera(platser):
        return nerifran(platser)
    if slag <= {"egen"} or talen_i_hojd(platser):
        return [celler(platser)]
    return [celler(platser)] if forsta and len(platser[0]) <= 1 else None


def nerifran(platser: list[list[Textrad]]) -> list[list[str]] | None:
    """Den nedersta textraden blir en egen rad när den står på samma höjd
    i varje cell som inte är tom. Det som står ovanför blir en rad när
    varje textrad med ett tal står på samma höjd som en textrad i
    varje cell."""
    if not flera(platser):
        return [celler(platser)] if talen_i_hojd(platser) else None
    sista = [p[-1].topp for p in platser if p]
    nederst = [p[-1:] for p in platser]
    if max(sista) - min(sista) > RADTOLERANS or flera(nederst):
        return None
    ovanfor = nerifran([p[:-1] for p in platser])
    return None if ovanfor is None else [*ovanfor, celler(nederst)]


def talen_i_hojd(platser: list[list[Textrad]]) -> bool:
    hojder = [r.topp for p in platser for r in p if r.har_tal]
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
    return any(sum(1 for f in r.falt if talfalt(f)) > 1 for r in rader)
