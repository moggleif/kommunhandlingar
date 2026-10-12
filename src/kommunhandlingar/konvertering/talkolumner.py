"""Krav: K5 i docs/02-KRAV.md, ADR-0029. Test: tests/test_talkolumner.py.

Kolumngränser mellan tal som står i linje i en tabell med linjer, men
utan lodrät linje emellan
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

from itertools import pairwise

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.tabeller import siffra, talfalt

Rader = list[list[Falt]]


def granser(kolumner: list[Rader]) -> list[float]:
    """Gränserna i varje kolumn mellan linjerna, givna som fälten rad för
    rad. Ingen gräns när tabellens första kolumn med text har färre än två
    textrader med en etikett utan siffror, eftersom etiketterna då står
    utanför tabellen och det som står där är en rubrik."""
    kolumner = [k for k in kolumner if any(k)]
    if not kolumner or etiketter(kolumner[0]) < 2:
        return []
    return [x for nr, k in enumerate(kolumner) for x in i_kolumnen(k, nr == 0)]


def etiketter(rader: Rader) -> int:
    return sum(1 for r in rader if not all(siffra(f.text) for f in r))


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
    """Fälten med siffror i grupper som överlappar, från den första gruppen
    med ett tal. None när det blir färre än två grupper, när en grupp har
    ett enda tal, eller två tal på samma rad; en grupp utan tal är en
    rubrik över en tom kolumn."""
    med_siffra = sorted(
        (f for r in rader for f in r if siffra(f.text)), key=lambda f: f.x0
    )
    grupper = overlappande(med_siffra)
    forsta = next((i for i, g in enumerate(grupper) if any(map(ar_tal, g))), None)
    grupper = [] if forsta is None else grupper[forsta:]
    if len(grupper) < 2 or any(sum(map(ar_tal, g)) == 1 for g in grupper):
        return None
    tva = (
        sum(1 for f in r if ar_tal(f) and f in g) > 1 for r in rader for g in grupper
    )
    return None if any(tva) else grupper


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
