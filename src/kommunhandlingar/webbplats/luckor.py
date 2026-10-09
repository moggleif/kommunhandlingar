"""Krav: K7 i docs/02-KRAV.md, ADR-0020. Test: tests/test_luckor.py."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

VANTADE = ("kallelse", "handlingar", "protokoll")
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
    vantade = {typ for typer in moten.values() for typ in typer if typ in VANTADE}
    return [
        Lucka(datum, lopnr, saknas)
        for (datum, lopnr), typer in sorted(moten.items())
        if (saknas := saknade(datum, vantade - typer, idag))
    ]


# Datumen är ÅÅÅÅ-MM-DD (datakontrollen), så de jämförs som text.
def saknade(datum: str, typer: set[str], idag: date) -> tuple[str, ...]:
    if datum >= idag.isoformat():
        return ()
    if datum > (idag - JUSTERING).isoformat():
        typer = typer - {"protokoll"}
    return tuple(typ for typ in VANTADE if typ in typer)
