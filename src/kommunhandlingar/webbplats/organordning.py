"""Krav: K39 och K58 i docs/02-KRAV.md, ADR-0060. Test: tests/test_navigering.py.

Organens ordning på kommunens sida och i menyn: kommunfilens grupper och
ordning, med varje utskott direkt efter sitt organ.
"""

from kommunhandlingar.konfiguration import Kommun, Organ


# Utan grupper i kommunfilen står alla organ i en grupp utan namn.
def grupperade(kommun: Kommun) -> list[tuple[str, list[Organ]]]:
    ordnade = ordning(kommun.organ)
    if not kommun.grupper:
        return [("", ordnade)]
    grupp = {o.id: o.grupp for o in kommun.organ}
    return [
        (namn, [o for o in ordnade if grupp[o.hor_till or o.id] == namn])
        for namn in kommun.grupper
    ]


# Kommunfilens ordning, men varje utskott direkt efter sitt organ.
def ordning(organen: tuple[Organ, ...]) -> list[Organ]:
    plats = {o.id: i for i, o in enumerate(organen)}
    return sorted(organen, key=lambda o: (plats[o.hor_till or o.id], bool(o.hor_till)))
