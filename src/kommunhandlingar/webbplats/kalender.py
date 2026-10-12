"""Krav: K22 i docs/02-KRAV.md, ADR-0032. Test: tests/test_kalender.py.

Läser `kalender/<kommun>.csv` och stoppar bygget med raden när den inte
går ihop med kommunfilen och poolen (docs/03-ARKITEKTUR.md#kalendern).
"""

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun

KOLUMNER = ["organ", "datum", "tid", "plats", "kalla", "osakert"]


@dataclass(frozen=True)
class Sammantrade:
    organ: str
    datum: date
    tid: str
    plats: str
    kalla: str
    osakert: str


def las(fil: Path, kommun: Kommun, data: Path) -> list[Sammantrade]:
    with fil.open(encoding="utf-8", newline="") as f:
        rader = list(csv.reader(f))
    if not rader or rader[0] != KOLUMNER:
        raise Datafel(f"{fil}: rubrikerna är inte {','.join(KOLUMNER)}")
    organ = {o.id for o in kommun.organ}
    sammantraden, sedda = [], set()
    for nr, rad in enumerate(rader[1:], 2):
        try:
            sammantrade = tolka(rad, organ, data)
        except ValueError as fel:
            raise Datafel(f"{fil}, rad {nr}: {fel}") from None
        if (sammantrade.organ, sammantrade.datum) in sedda:
            raise Datafel(f"{fil}, rad {nr}: organet har redan ett sammanträde dagen")
        sedda.add((sammantrade.organ, sammantrade.datum))
        sammantraden.append(sammantrade)
    return sammantraden


def tolka(rad: list[str], organ: set[str], data: Path) -> Sammantrade:
    if len(rad) != len(KOLUMNER):
        raise ValueError(f"{len(rad)} fält, inte {len(KOLUMNER)}")
    sammantrade = Sammantrade(rad[0], date.fromisoformat(rad[1]), *rad[2:])
    if sammantrade.organ not in organ:
        raise ValueError(f"organet {sammantrade.organ!r} står inte i kommunfilen")
    if not (sammantrade.kalla.startswith("https://") or (data / rad[4]).is_file()):
        raise ValueError(f"källan {sammantrade.kalla!r} finns inte i poolen")
    if sammantrade.datum.weekday() >= 5 and not sammantrade.osakert:
        raise ValueError(
            f"{sammantrade.datum} är en lördag eller söndag, inte märkt osäkert"
        )
    return sammantrade
