"""Krav: K54 i docs/02-KRAV.md, ADR-0078. Test: tests/test_kortkoppling.py.

Korten på organens sidor över tid, per diarienummer. Ett steg vars källa
är en sida i ett protokoll hör till paragrafen som täcker sidan: de som
börjar där, annars den sista som börjat före. Har sidan paragrafer med
andra diarienummer är kopplingen `tolkad`.
"""

from collections import defaultdict
from dataclasses import dataclass

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.spar import Slag, Steg
from kommunhandlingar.webbplats.sparsida import adress, per_sak

# En paragrafs första sida och diarienummer, per protokoll.
Sidindex = dict[str, list[tuple[int, list[str]]]]
# Varje slags steg i kommunen.
Spar = list[tuple[Slag, list[Steg]]]


@dataclass(frozen=True)
class Kortlank:
    adress: str
    rubrik: str
    tolkad: bool


def sidindex(paragrafer: list[dict]) -> Sidindex:
    index = defaultdict(list)
    for p in paragrafer:
        index[p["fil"].split("/", 2)[2]].append((p["sidnummer"], p["diarienummer"]))
    return index


def tacker(index: Sidindex, kalla: str) -> list[str]:
    fil, _, sida = kalla.partition("#sida-")
    fore = [(s, d) for s, d in index.get(fil, []) if sida and s <= int(sida)]
    forsta = max((s for s, _ in fore), default=None)
    return [n for s, dnr in fore if s == forsta for n in dnr]


def kortlankar(kommun: Kommun, sparen: Spar, index: Sidindex):
    lankar = defaultdict(list)
    for slag, organ, nr, (namn, stegen, _) in alla_saker(sparen):
        sidans = f"{adress(kommun, organ, slag)}#sak-{nr}"
        rubrik = f"{slag.rubrik}, {organnamn(kommun, organ)}: {namn}"
        for dnr, tolkad in kopplingar(index, stegen).items():
            lankar[dnr].append(Kortlank(sidans, rubrik, tolkad))
    return lankar


# Sakerna med sina nummer på organets sida, i sidans ordning.
def alla_saker(sparen: Spar):
    for slag, stegen in sparen:
        for organ in dict.fromkeys(s.organ for s in stegen):
            sakerna = per_sak(slag, [s for s in stegen if s.organ == organ])
            yield from ((slag, organ, nr, sak) for nr, sak in enumerate(sakerna))


def kopplingar(index: Sidindex, stegen: list[Steg]) -> dict[str, bool]:
    funna = {}
    for steg in stegen:
        numren = tacker(index, steg.kalla)
        for dnr in numren:
            funna[dnr] = funna.get(dnr, True) and len(set(numren)) > 1
    return funna


def organnamn(kommun: Kommun, organ: str) -> str:
    return next(o.namn[0] for o in kommun.organ if o.id == organ)
