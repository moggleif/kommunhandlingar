"""Krav: K5 i docs/02-KRAV.md, ADR-0029. Test: tests/test_talkolumner.py.

Kolumngränser mellan tal som står i linje i en tabell med linjer, men
utan lodrät linje emellan
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

from itertools import pairwise

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.tabeller import siffra, talfalt

Rader = list[list[Falt]]


def etiketterade(rader: list[list[str]]) -> bool:
    """Varje rad med siffror under den första har en etikett i tabellens
    första kolumn med text: en textrad utan siffror och utan streck."""
    forsta = next(i for i in range(len(rader[0])) if any(r[i] for r in rader))
    return all(
        any(t and not siffra(t) and not talfalt(t) for t in r[forsta].split("\n"))
        for r in rader[1:]
        if any(map(siffra, r))
    )


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
