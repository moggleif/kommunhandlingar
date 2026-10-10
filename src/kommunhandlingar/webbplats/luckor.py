"""Krav: K7 i docs/02-KRAV.md, ADR-0020. Test: tests/test_luckor.py."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

# Kallelsen och handlingarna publiceras ofta som en fil, under endera namnet.
GRUPPER = (("kallelse", "handlingar"), ("protokoll",))
# Kommunallagen ger 14 dagar för justeringen; en vecka till för anslag och publicering.
JUSTERING = timedelta(days=21)


@dataclass(frozen=True)
class Lucka:
    datum: str
    lopnr: str
    saknas: tuple[str, ...]


def luckor(dokument: list[dict[str, str]], idag: date) -> list[Lucka]:
    moten = defaultdict(set)
    for d in dokument:
        moten[(d["datum"], d["lopnr"])].add(d["typ"])
    organets = set().union(*moten.values())
    vantade = [grupp for grupp in GRUPPER if organets.intersection(grupp)]
    return [
        Lucka(datum, lopnr, saknas)
        for (datum, lopnr), typer in sorted(moten.items())
        if (saknas := saknade(datum, [g for g in vantade if not typer & set(g)], idag))
    ]


# Datumen är ÅÅÅÅ-MM-DD (datakontrollen), så de jämförs som text.
def saknade(datum: str, grupper: list[tuple], idag: date) -> tuple[str, ...]:
    if datum >= idag.isoformat():
        return ()
    if datum > (idag - JUSTERING).isoformat():
        grupper = [grupp for grupp in grupper if "protokoll" not in grupp]
    return tuple(" och ".join(grupp) for grupp in grupper)


def motesnamn(datum: str, lopnr: str) -> str:
    return datum if lopnr == "null" else f"{datum}-{lopnr}"
