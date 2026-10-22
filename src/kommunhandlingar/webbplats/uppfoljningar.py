"""Krav: K28 i docs/02-KRAV.md, ADR-0046. Test: tests/test_uppfoljningar.py.

Läser `uppfoljningar/<kommun>.csv`: en rad per paragraf i ett organs
protokoll där nämnden tar upp sina mål, en uppföljning eller en dragning.
Bygget stoppas med raden när den inte går ihop med kommunfilen och poolen.
"""

import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mal import Sidtext, sidlasare, star_pa

KOLUMNER = ["organ", "datum", "paragraf", "slag", "rubrik", "kalla"]
SLAG = ("uppföljning", "dragning")


@dataclass(frozen=True)
class Uppfoljning:
    organ: str
    datum: str
    paragraf: str
    slag: str
    rubrik: str
    kalla: str

    @property
    def ar(self) -> int:
        return int(self.datum[:4])


def las(fil: Path, kommun: Kommun, data: Path) -> list[Uppfoljning]:
    with fil.open(encoding="utf-8", newline="") as f:
        rader = list(csv.reader(f))
    if not rader or rader[0] != KOLUMNER:
        raise Datafel(f"{fil}: rubrikerna är inte {','.join(KOLUMNER)}")
    organ = {o.id for o in kommun.organ}
    sidtext = sidlasare(data)
    uppfoljningar, sedda = [], set()
    for nr, rad in enumerate(rader[1:], 2):
        try:
            uppfoljning = tolka(rad, organ, sidtext)
        except ValueError as fel:
            raise Datafel(f"{fil}, rad {nr}: {fel}") from None
        nyckel = (uppfoljning.organ, uppfoljning.datum, uppfoljning.paragraf)
        if nyckel in sedda:
            raise Datafel(f"{fil}, rad {nr}: paragrafen står redan i filen")
        sedda.add(nyckel)
        uppfoljningar.append(uppfoljning)
    return uppfoljningar


def tolka(rad: list[str], organ: set[str], sidtext: Sidtext) -> Uppfoljning:
    if len(rad) != len(KOLUMNER):
        raise ValueError(f"{len(rad)} fält, inte {len(KOLUMNER)}")
    upp = Uppfoljning(*rad)
    try:
        date.fromisoformat(upp.datum)
    except ValueError:
        raise ValueError(f"datumet {upp.datum!r} är inte ÅÅÅÅ-MM-DD") from None
    if upp.organ not in organ:
        raise ValueError(f"organet {upp.organ!r} står inte i kommunfilen")
    if upp.slag not in SLAG:
        raise ValueError(f"slaget {upp.slag!r} är varken {' eller '.join(SLAG)}")
    if not re.fullmatch(r"\d+", upp.paragraf):
        raise ValueError(f"paragrafen {upp.paragraf!r} är inget nummer")
    kontrollera_kalla(upp, sidtext)
    return upp


def kontrollera_kalla(upp: Uppfoljning, sidtext: Sidtext) -> None:
    if not upp.kalla.startswith(f"{upp.organ}/{upp.ar}/{upp.datum}/protokoll"):
        raise ValueError(f"källan {upp.kalla!r} är inte mötets protokoll")
    if not star_pa(upp.rubrik, sidtext(upp.kalla, upp.organ)):
        raise ValueError(f"rubriken står inte på {upp.kalla}")
