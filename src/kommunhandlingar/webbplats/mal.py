"""Krav: K26 i docs/02-KRAV.md, ADR-0044. Test: tests/test_mal.py.

Läser `mal/<kommun>.csv` och stoppar bygget med raden när den inte går
ihop med kommunfilen och poolen (docs/03-ARKITEKTUR.md#mål-och-direktiv).
"""

import csv
import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun

KOLUMNER = ["organ", "ar", "slag", "rubrik", "formulering", "status", "kalla"]
SLAG = ("nämndmål", "direktiv")
# Ett dokument ligger på <organ>/<år>/<datum>/<namn>.md (ADR-0003).
KALLA = re.compile(
    r"(?P<dokument>(?P<organ>[^/]+)/\d{4}/[^/]+/[^/]+\.md)#sida-(?P<nr>\d+)"
)
SIDA = re.compile(r"^<!-- sida (\d+) -->$", re.MULTILINE)
ESCAPNING = re.compile(r"\\([!-/:-@\[-`{-~])")
PUNKT = re.compile(r"^[ \t]*[-•*][ \t]*", re.MULTILINE)

Sidtext = Callable[[str, str], str]


@dataclass(frozen=True)
class Mal:
    organ: str
    ar: int
    slag: str
    rubrik: str
    formulering: str
    status: str
    kalla: str

    # Samma mål är samma organ, slag och rubrik, utan hänsyn till versaler.
    @property
    def spar(self) -> tuple[str, str, str]:
        return self.organ, self.slag, self.rubrik.casefold()


def las(fil: Path, kommun: Kommun, data: Path) -> list[Mal]:
    with fil.open(encoding="utf-8", newline="") as f:
        rader = list(csv.reader(f))
    if not rader or rader[0] != KOLUMNER:
        raise Datafel(f"{fil}: rubrikerna är inte {','.join(KOLUMNER)}")
    organ = {o.id for o in kommun.organ}
    sidtext = sidlasare(data)
    malen, sedda = [], set()
    for nr, rad in enumerate(rader[1:], 2):
        try:
            mal = tolka(rad, organ, sidtext)
        except ValueError as fel:
            raise Datafel(f"{fil}, rad {nr}: {fel}") from None
        if (mal.spar, mal.kalla) in sedda:
            raise Datafel(f"{fil}, rad {nr}: målet står redan med samma källa")
        sedda.add((mal.spar, mal.kalla))
        malen.append(mal)
    return malen


def tolka(rad: list[str], organ: set[str], sidtext: Sidtext) -> Mal:
    if len(rad) != len(KOLUMNER):
        raise ValueError(f"{len(rad)} fält, inte {len(KOLUMNER)}")
    if not re.fullmatch(r"\d{4}", rad[1]):
        raise ValueError(f"året {rad[1]!r} är inte fyra siffror")
    mal = Mal(rad[0], int(rad[1]), *rad[2:])
    if mal.organ not in organ:
        raise ValueError(f"organet {mal.organ!r} står inte i kommunfilen")
    if mal.slag not in SLAG:
        raise ValueError(f"slaget {mal.slag!r} är varken {' eller '.join(SLAG)}")
    sida = sidtext(mal.kalla, mal.organ)
    for falt in ("rubrik", "formulering", "status"):
        if jamforbar(getattr(mal, falt)) not in sida:
            raise ValueError(f"{falt}en står inte på {mal.kalla}")
    return mal


def sidlasare(data: Path) -> Sidtext:
    sidor = cache(lambda dokument: las_sidor(data / dokument))

    def sidtext(kalla: str, organ: str) -> str:
        traff = KALLA.fullmatch(kalla)
        if not traff or traff["organ"] != organ:
            raise ValueError(f"källan {kalla!r} är ingen sida i organets dokument")
        if not (data / traff["dokument"]).is_file():
            raise ValueError(f"källan {kalla!r} är inget dokument i poolen")
        if traff["nr"] not in (dokumentet := sidor(traff["dokument"])):
            raise ValueError(f"källan {kalla!r} är ingen sida i dokumentet")
        return dokumentet[traff["nr"]]

    return sidtext


def las_sidor(fil: Path) -> dict[str, str]:
    delar = SIDA.split(fil.read_text(encoding="utf-8"))
    return {
        nr: jamforbar(text) for nr, text in zip(delar[1::2], delar[2::2], strict=True)
    }


# Radbrytningarna ur PDF:en, punkterna först i en rad, versalerna och
# Markdown-escapningen (ADR-0021) räknas inte.
def jamforbar(text: str) -> str:
    return " ".join(PUNKT.sub("", ESCAPNING.sub(r"\1", text)).split()).casefold()
