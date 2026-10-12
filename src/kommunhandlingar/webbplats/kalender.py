"""Krav: K22 i docs/02-KRAV.md, ADR-0032. Test: tests/test_kalender.py.

Läser `kalender/<kommun>.csv` och stoppar bygget med raden när den inte
går ihop med kommunfilen och poolen (docs/03-ARKITEKTUR.md#kalendern).
"""

import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun

DATUM = re.compile(r"\d{4}-\d{2}-\d{2}")
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
    sammantraden = []
    for nr, rad in enumerate(rader[1:], 2):
        try:
            sammantraden.append(tolka(rad, organ, data, sammantraden))
        except ValueError as fel:
            raise Datafel(f"{fil}, rad {nr}: {fel}") from None
    return sammantraden


def tolka(rad: list[str], organ: set[str], data: Path, tidigare: list) -> Sammantrade:
    if len(rad) != len(KOLUMNER):
        raise ValueError(f"{len(rad)} fält, inte {len(KOLUMNER)}")
    if not DATUM.fullmatch(rad[1]):
        raise ValueError(f"datumet {rad[1]!r} är inte ÅÅÅÅ-MM-DD")
    s = Sammantrade(rad[0], date.fromisoformat(rad[1]), *rad[2:])
    if s.organ not in organ:
        raise ValueError(f"organet {s.organ!r} står inte i kommunfilen")
    if any((t.organ, t.datum) == (s.organ, s.datum) for t in tidigare):
        raise ValueError("organet har redan ett sammanträde den dagen")
    if not (s.kalla.startswith("https://") or i_poolen(s.kalla, data)):
        raise ValueError(f"källan {s.kalla!r} är inget dokument i poolen")
    if s.datum.weekday() >= 5 and not s.osakert:
        raise ValueError(f"{s.datum} är en lördag eller söndag, inte märkt osäkert")
    return s


# Ett dokument ligger på <organ>/<år>/<datum>/<typ>.md (ADR-0003).
def i_poolen(kalla: str, data: Path) -> bool:
    delar = kalla.split("/")
    ratt_form = len(delar) == 4 and ".." not in delar and kalla.endswith(".md")
    return ratt_form and (data / kalla).is_file()
