"""Krav: K36 i docs/02-KRAV.md, ADR-0057. Test: tests/test_lokalbehov.py.

Läser `lokalbehov/<kommun>.csv`: en rad per steg ett av organets
lokalbehov tar, från nämndens lokalbehov till utfört, med en sida i ett
dokument i poolen som källa. Källan får vara vilket organs dokument som
helst. Bygget stoppas med raden när den inte går ihop med kommunfilen och
poolen (docs/03-ARKITEKTUR.md#lokalbehov).
"""

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mal import Sidtext, provbar, sidlasare

KOLUMNER = ["organ", "behov", "ar", "fas", "varde", "text", "kalla", "tolkad"]
FASER = (
    *("forslag", "lokalbehov", "prioritet"),
    *("lokalplan", "startbeslut", "pagar", "utfort"),
)


@dataclass(frozen=True)
class Steg:
    organ: str
    behov: str
    ar: int
    fas: str
    varde: str
    text: str
    kalla: str
    tolkad: str

    @property
    def kallans_organ(self) -> str:
        return self.kalla.split("/", 1)[0]


def las(fil: Path, kommun: Kommun, data: Path) -> list[Steg]:
    with fil.open(encoding="utf-8", newline="") as f:
        rader = list(csv.reader(f))
    if not rader or rader[0] != KOLUMNER:
        raise Datafel(f"{fil}: rubrikerna är inte {','.join(KOLUMNER)}")
    organ = {o.id for o in kommun.organ}
    sidtext = sidlasare(data)
    stegen, sedda = [], set()
    for nr, rad in enumerate(rader[1:], 2):
        try:
            steg = tolka(rad, organ, sidtext)
        except ValueError as fel:
            raise Datafel(f"{fil}, rad {nr}: {fel}") from None
        nyckel = (steg.organ, steg.behov, steg.fas, steg.kalla)
        if nyckel in sedda:
            raise Datafel(f"{fil}, rad {nr}: steget står redan med samma källa")
        sedda.add(nyckel)
        stegen.append(steg)
    return stegen


def tolka(rad: list[str], organ: set[str], sidtext: Sidtext) -> Steg:
    if len(rad) != len(KOLUMNER):
        raise ValueError(f"{len(rad)} fält, inte {len(KOLUMNER)}")
    if not re.fullmatch(r"\d{4}", rad[2]):
        raise ValueError(f"året {rad[2]!r} är inte fyra siffror")
    steg = Steg(rad[0], rad[1], int(rad[2]), *rad[3:])
    if steg.organ not in organ:
        raise ValueError(f"organet {steg.organ!r} står inte i kommunfilen")
    if not steg.behov or not steg.text:
        raise ValueError("behovet och texten får inte vara tomma")
    if steg.fas not in FASER:
        raise ValueError(f"fasen {steg.fas!r} är inte en av {', '.join(FASER)}")
    kontrollera_varde(steg)
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


# En prioritet har ett värde, en siffra eller källans ord, och en
# lokalplan har lokalplanens löpnummer.
def kontrollera_varde(steg: Steg) -> None:
    if steg.fas == "prioritet" and not steg.varde:
        raise ValueError("prioriteten saknar värde")
    if steg.fas == "lokalplan" and not re.fullmatch(r"\d+", steg.varde):
        raise ValueError(f"löpnumret {steg.varde!r} är inget nummer")
