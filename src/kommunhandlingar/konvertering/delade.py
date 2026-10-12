"""Krav: K5 i docs/02-KRAV.md, ADR-0028 och ADR-0029. Test:
tests/test_delade.py, tests/test_delade_kolumner.py och tests/test_delade_rader.py.

En tabell med linjer där en cell rymmer mer än ett tal delas, i stället
för att fällas, när det går ihop: kolumnerna efter de lodräta linjer som
finns i någon rad och efter tal i linje (`talkolumner.py`), och raderna
efter rutornas textrader
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

from itertools import pairwise

from pdfplumber.table import Table

from kommunhandlingar.konvertering import talkolumner
from kommunhandlingar.konvertering.falt import RADTOLERANS, falt, radvis
from kommunhandlingar.konvertering.sammanslagna import I_LINJE, Textrad, cellens, kolumn
from kommunhandlingar.konvertering.tabeller import flera_tal, inom, mitt, talfalt


def tabell(t: Table, ord_: list[dict]) -> tuple[list, tuple] | None:
    """Raderna, och kolumnernas vänsterkanter och tabellens högerkant
    (K19); None när tabellen inte går att dela, eller när gränserna efter
    talen ger rader utan etikett."""
    if any(over_linje(o, t.cells) for o in ord_ if inom(mitt(o), t.bbox)):
        return None
    linjer = kolumngranser(t)
    granser = tuple(sorted({*linjer, *talkolumner.granser(falten(t, ord_, linjer))}))
    rader: list[list[str]] = []
    for nr, rad in enumerate(t.rows):
        placerat = placera(rad.cells, ord_, granser)
        delrader = None if placerat is None else dela(*placerat, forsta=nr == 0)
        if delrader is None:
            return None
        rader += delrader
    utan_etiketter = granser != linjer and not talkolumner.etiketterade(rader)
    return None if utan_etiketter else (rader, granser)


def over_linje(o: dict, celler: list[tuple]) -> bool:
    """Ett ord vars tecken står i olika celler, som en etikett i ett
    diagram vars rutnät pdfplumber läser som en tabell."""
    i_celler = {
        next((i for i, c in enumerate(celler) if inom(mitt(t), c)), None)
        for t in o["chars"]
    }
    return len(i_celler - {None}) > 1


def falten(t: Table, ord_: list[dict], linjer: tuple) -> list[talkolumner.Rader]:
    """Tabellens fält textrad för textrad, för varje kolumn mellan linjerna."""
    rader = [falt(r, True) for r in radvis([o for o in ord_ if inom(mitt(o), t.bbox)])]
    return [
        [[f for f in r if kolumn(f.x0, f.x1, (vanster, hoger)) == 0] for r in rader]
        for vanster, hoger in pairwise(linjer)
    ]


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


def dela(platser: list[list[Textrad]], slag: set[str], forsta: bool) -> list | None:
    """Raden som den står när ingen cell rymmer mer än ett tal, annars
    delad nerifrån; None när det inte går ihop. En rubrikcell och en text
    över en kolumngräns får bara stå i första raden. En rad med en delad
    cell ska ha sina tal på samma höjd, utom i första raden när den
    första kolumnen med text har högst en textrad: då antas den vara en
    rubrik i flera rader."""
    if slag & {"rubrik", "over"} and not forsta:
        return None
    if flera(platser):
        return nerifran(platser)
    if slag <= {"egen"} or talen_i_hojd(platser):
        return [celler(platser)]
    forsta_med_text = next(filter(None, platser), [])
    return [celler(platser)] if forsta and len(forsta_med_text) <= 1 else None


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
    return all(i_hojd(p, hojder[0]) for p in platser if p)


def i_hojd(ruta: list[Textrad], hojd: float) -> bool:
    """En textrad på talens höjd, eller talen mitt emellan två textrader,
    som en etikett som bryts runt sina tal. Mitt emellan är inom en sjättedel
    av avståndet, så att talen inte står närmare den ena."""
    toppar = [r.topp for r in ruta]
    if any(abs(t - hojd) <= RADTOLERANS for t in toppar):
        return True
    ovan = [t for t in toppar if t < hojd]
    under = [t for t in toppar if t > hojd]
    if not ovan or not under:
        return False
    marginal = min(RADTOLERANS, (min(under) - max(ovan)) / 6)
    return abs((max(ovan) + min(under)) / 2 - hojd) <= marginal


def celler(platser: list[list[Textrad]]) -> list[str]:
    return ["\n".join(r.text for r in p) for p in platser]


def flera(platser: list[list[Textrad]]) -> bool:
    """Mer än ett tal i någon cell, efter cellens text eller dess fält."""
    if any(map(flera_tal, celler(platser))):
        return True
    rader = (r for p in platser for r in p)
    return any(sum(1 for f in r.falt if talfalt(f)) > 1 for r in rader)
