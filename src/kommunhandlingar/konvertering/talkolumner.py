"""Krav: K5 i docs/02-KRAV.md, ADR-0029. Test: tests/test_talkolumner.py.

Kolumngränser mellan tal som står i linje i en tabell med linjer, men
utan lodrät linje emellan
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

from itertools import pairwise

from pdfplumber.table import Table

from kommunhandlingar.konvertering.falt import Falt, falt, radvis
from kommunhandlingar.konvertering.sammanslagna import kolumn, med_tal
from kommunhandlingar.konvertering.tabeller import inom, mitt, siffra, talfalt

Rader = list[list[Falt]]


def tabellens(t: Table, ord_: list[dict], linjer: tuple) -> tuple[float, ...]:
    """Kolumngränserna efter linjerna och efter talen. Gränser efter talen
    läggs bara när varje rad med tal under den första har en etikett i
    tabellens första kolumn med text; annars står etiketterna utanför."""
    inne = [o for o in ord_ if inom(mitt(o), t.bbox)]
    if not etiketterade(t, inne, linjer):
        return linjer
    return tuple(sorted({*linjer, *granser(falten(inne, linjer))}))


def etiketterade(t: Table, inne: list[dict], linjer: tuple) -> bool:
    kolumnerna = [kolumn(o["x0"], o["x1"], linjer) for o in inne]
    forsta = min(filter(lambda i: i is not None, kolumnerna), default=None)
    for rad in t.rows[1:]:
        i_raden = [
            (k, med_tal((o["text"],)))
            for o, k in zip(inne, kolumnerna, strict=True)
            if inom(mitt(o), rad.bbox)
        ]
        har_tal = any(tal for _, tal in i_raden)
        if har_tal and not any(k == forsta and not tal for k, tal in i_raden):
            return False
    return True


def falten(inne: list[dict], linjer: tuple) -> list[Rader]:
    """Tabellens fält rad för rad, för varje kolumn mellan linjerna."""
    rader = [falt(r, True) for r in radvis(inne)]
    return [
        [[f for f in r if kolumn(f.x0, f.x1, (vanster, hoger)) == 0] for r in rader]
        for vanster, hoger in pairwise(linjer)
    ]


def granser(kolumner: list[Rader]) -> list[float]:
    """Gränserna i varje kolumn mellan linjerna, givna som fälten rad för
    rad."""
    kolumner = [k for k in kolumner if any(k)]
    return [x for nr, k in enumerate(kolumner) for x in i_kolumnen(k, nr == 0)]


def i_kolumnen(rader: Rader, forsta: bool) -> list[float]:
    """En gräns mitt i mellanrummet mellan två grupper av tal, och före den
    första gruppen när text står till vänster om den. I tabellens första
    kolumn krävs den texten, etiketterna."""
    if not any(sum(map(ar_tal, r)) > 1 for r in rader):
        return []
    grupper = talgrupper(rader)
    if grupper is None:
        return []
    spann = [(min(f.x0 for f in g), max(f.x1 for f in g)) for g in grupper]
    fore = [f.x1 for r in rader for f in r if f.x1 < spann[0][0]]
    if forsta and not fore:
        return []
    mellan = [(vanster[1] + hoger[0]) / 2 for vanster, hoger in pairwise(spann)]
    return [(max(fore) + spann[0][0]) / 2, *mellan] if fore else mellan


def talgrupper(rader: Rader) -> list[list[Falt]] | None:
    """Fälten med siffror i grupper som överlappar, från den första med
    ett tal; en grupp utan tal är en rubrik över en tom kolumn. None vid
    färre än två grupper, ett ensamt tal i en grupp, eller två tal från
    samma rad i en grupp."""
    med_siffra = sorted(
        (f for r in rader for f in r if siffra(f.text)), key=lambda f: f.x0
    )
    grupper = overlappande(med_siffra)
    forsta = next((i for i, g in enumerate(grupper) if any(map(ar_tal, g))), None)
    grupper = [] if forsta is None else grupper[forsta:]
    if len(grupper) < 2 or any(sum(map(ar_tal, g)) == 1 for g in grupper):
        return None
    return None if any(tva_i_en(r, g) for r in rader for g in grupper) else grupper


def tva_i_en(rad: list[Falt], grupp: list[Falt]) -> bool:
    return sum(1 for f in rad if ar_tal(f) and f in grupp) > 1


def overlappande(falt_: list[Falt]) -> list[list[Falt]]:
    grupper: list[list[Falt]] = []
    for f in falt_:
        if grupper and f.x0 <= max(g.x1 for g in grupper[-1]):
            grupper[-1].append(f)
        else:
            grupper.append([f])
    return grupper


def ar_tal(f: Falt) -> bool:
    return talfalt(f.text)
