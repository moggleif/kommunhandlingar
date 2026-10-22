"""Krav: K36 och K37 i docs/02-KRAV.md, ADR-0057 och ADR-0058.
Test: tests/test_lokalbehov.py, tests/test_initiativ.py.

Läser en spårfil, `<slag>/<kommun>.csv`: en rad per steg en sak tar över
tid – ett lokalbehov, ett initiativärende – med en sida i ett dokument i
poolen som källa. Källan får vara vilket organs dokument som helst. Vad
som skiljer slagen åt – kolumnens namn, faserna, värdena och sidans text –
står i `sparslag.py`. Bygget stoppas med raden när den inte går ihop med
kommunfilen och poolen (docs/03-ARKITEKTUR.md#lokalbehov och
#initiativärenden).
"""

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mal import Sidtext, provbar, sidlasare


@dataclass(frozen=True)
class Slag:
    id: str
    kolumn: str
    rubrik: str
    sak: str
    saker: str
    antal: str
    # Fasens ikon och vad den betyder, i fasernas ordning.
    faser: dict[str, tuple[str, str]]
    inledning: str
    metod: str
    adr: str
    # Faser vars värde måste passa mönstret, och vad det då är.
    varden: dict[str, tuple[str, str]] = field(default_factory=dict)
    # Fasen vars värde står som siffra i ikonen.
    siffra: str = ""
    # Fasen vars senaste år ger urvalet "I <rubrik> <år>".
    aktuell: str = ""
    # Fasen vars värde säger vem som står bakom saken.
    avsandare: str = ""

    @property
    def kolumner(self) -> list[str]:
        return ["organ", self.kolumn, "ar", "fas", "varde", "text", "kalla", "tolkad"]


@dataclass(frozen=True)
class Steg:
    organ: str
    namn: str
    ar: int
    fas: str
    varde: str
    text: str
    kalla: str
    tolkad: str

    @property
    def kallans_organ(self) -> str:
        return self.kalla.split("/", 1)[0]


def las(fil: Path, kommun: Kommun, data: Path, slag: Slag) -> list[Steg]:
    with fil.open(encoding="utf-8", newline="") as f:
        rader = list(csv.reader(f))
    if not rader or rader[0] != slag.kolumner:
        raise Datafel(f"{fil}: rubrikerna är inte {','.join(slag.kolumner)}")
    organ = {o.id for o in kommun.organ}
    sidtext = sidlasare(data)
    stegen, sedda = [], set()
    for nr, rad in enumerate(rader[1:], 2):
        try:
            steg = tolka(rad, slag, organ, sidtext)
        except ValueError as fel:
            raise Datafel(f"{fil}, rad {nr}: {fel}") from None
        nyckel = (steg.organ, steg.namn, steg.fas, steg.kalla)
        if nyckel in sedda:
            raise Datafel(f"{fil}, rad {nr}: steget står redan med samma källa")
        sedda.add(nyckel)
        stegen.append(steg)
    return stegen


def tolka(rad: list[str], slag: Slag, organ: set[str], sidtext: Sidtext) -> Steg:
    if len(rad) != len(slag.kolumner):
        raise ValueError(f"{len(rad)} fält, inte {len(slag.kolumner)}")
    if not re.fullmatch(r"\d{4}", rad[2]):
        raise ValueError(f"året {rad[2]!r} är inte fyra siffror")
    steg = Steg(rad[0], rad[1], int(rad[2]), *rad[3:])
    if steg.organ not in organ:
        raise ValueError(f"organet {steg.organ!r} står inte i kommunfilen")
    if not steg.namn or not steg.text:
        raise ValueError(f"{slag.kolumn} och texten får inte vara tomma")
    if steg.fas not in slag.faser:
        raise ValueError(f"fasen {steg.fas!r} är inte en av {', '.join(slag.faser)}")
    kontrollera_varde(steg, slag)
    if steg.tolkad not in ("", "ja"):
        raise ValueError(f"tolkad {steg.tolkad!r} är varken tom eller ja")
    kontrollera_kalla(steg, organ, sidtext)
    return steg


def kontrollera_kalla(steg: Steg, organ: set[str], sidtext: Sidtext) -> None:
    if steg.kallans_organ not in organ:
        raise ValueError(f"källan {steg.kalla!r} är inget organs dokument")
    sidan = sidtext(steg.kalla, steg.kallans_organ)
    for falt, varde in (("texten", steg.text), ("värdet", steg.varde)):
        if provbar(varde) not in sidan:
            raise ValueError(f"{falt} står inte på {steg.kalla}")


def kontrollera_varde(steg: Steg, slag: Slag) -> None:
    if steg.fas not in slag.varden:
        return
    monster, ar = slag.varden[steg.fas]
    if not re.fullmatch(monster, steg.varde):
        raise ValueError(f"värdet {steg.varde!r} för {steg.fas} är inte {ar}")
