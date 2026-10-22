"""Krav: K26, K27 och K35 i docs/02-KRAV.md, ADR-0044, ADR-0045 och ADR-0056.
Test: tests/test_mal.py och tests/test_fokusomraden.py.

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
from kommunhandlingar.webbplats.malkontroll import Kontroll

KOLUMNER = [
    *("organ", "ar", "slag", "rubrik", "formulering", "status"),
    *("uppfoljning", "bedomning", "kalla", "grupp", "tolkad", "huvudmal"),
]
# Ett fokusområde hör till ett kommunmål och visas under det (ADR-0056).
SLAG = ("nämndmål", "kommunmål", "fokusområde", "direktiv")
FALTEN = (
    ("rubrik", "rubriken"),
    ("formulering", "formuleringen"),
    ("status", "statusen"),
    ("huvudmal", "huvudmålet"),
)
# Ett dokument ligger på <organ>/<år>/<datum>/<namn>.md (ADR-0003). Ett
# mål som fortsätter på nästa sida har sidorna, till exempel `#sida-14-15`.
KALLA = re.compile(
    r"(?P<dokument>(?P<organ>[^/]+)/\d{4}/[^/]+/[^/]+\.md)"
    r"#sida-(?P<forsta>\d+)(?:-(?P<sista>\d+))?"
)
SIDA = re.compile(r"^<!-- sida (\d+) -->$", re.MULTILINE)
ESCAPNING = re.compile(r"\\([!-/:-@\[-`{-~])")
PUNKT = re.compile(r"^[ \t]*[-•*][ \t]*", re.MULTILINE)
# Mellanrum, mjuka bindestreck, ett ord delat i en tabellcell och
# trendkolumnens pilar och tankstreck, som hamnar mitt i texten (ADR-0056).
UTFYLLNAD = re.compile(r"-<br>|<br>|[\s\u00ad\u2013\u2014\u2190-\u21ff\ue000-\uf8ff]")

Sidtext = Callable[[str, str], str]


@dataclass(frozen=True)
class Mal:
    organ: str
    ar: int
    slag: str
    rubrik: str
    formulering: str
    status: str
    uppfoljning: str
    bedomning: str
    kalla: str
    grupp: str
    tolkad: str
    huvudmal: str

    @property
    def namn(self) -> tuple[str, str, str]:
        return self.organ, self.slag, self.rubrik.casefold()

    @property
    def spar(self) -> tuple[str, str]:
        return self.organ, (self.grupp or self.rubrik).casefold()

    @property
    def dokument(self) -> str:
        return self.kalla.split("#")[0]

    @property
    def mote(self) -> str:
        return self.kalla.rsplit("/", 1)[0]

    @property
    def fran_protokoll(self) -> bool:
        return self.kalla.rsplit("/", 1)[1].startswith("protokoll")

    @property
    def prognos(self) -> bool:
        return self.uppfoljning == "prognos"


def las(fil: Path, kommun: Kommun, data: Path) -> list[Mal]:
    with fil.open(encoding="utf-8", newline="") as f:
        rader = list(csv.reader(f))
    if not rader or rader[0] != KOLUMNER:
        raise Datafel(f"{fil}: rubrikerna är inte {','.join(KOLUMNER)}")
    organ = {o.id for o in kommun.organ}
    sidtext = sidlasare(data)
    malen, kontroll = [], Kontroll()
    for nr, rad in enumerate(rader[1:], 2):
        try:
            mal = tolka(rad, organ, sidtext)
            kontroll.prova(mal)
        except ValueError as fel:
            raise Datafel(f"{fil}, rad {nr}: {fel}") from None
        malen.append(mal)
    try:
        kontroll.grupperna()
    except ValueError as fel:
        raise Datafel(f"{fil}: {fel}") from None
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
    if (mal.slag == "fokusområde") != bool(mal.huvudmal):
        raise ValueError("ett fokusområde, och bara det, har ett huvudmål")
    sida = sidtext(mal.kalla, mal.organ)
    for falt, namn in FALTEN:
        if not star_pa(getattr(mal, falt), sida):
            raise ValueError(f"{namn} står inte på {mal.kalla}")
    return mal


# Versalerna räknas, utom när källan sätter hela texten i versaler.
def star_pa(text: str, sida: str) -> bool:
    provad = provbar(text)
    return provad in sida or provad.upper() in sida


def sidlasare(data: Path) -> Sidtext:
    sidor = cache(lambda dokument: las_sidor(data / dokument))

    def sidtext(kalla: str, organ: str) -> str:
        traff = KALLA.fullmatch(kalla)
        if not traff or traff["organ"] != organ:
            raise ValueError(f"källan {kalla!r} är ingen sida i organets dokument")
        if not (data / traff["dokument"]).is_file():
            raise ValueError(f"källan {kalla!r} är inget dokument i poolen")
        dokumentet = sidor(traff["dokument"])
        nr = sidnummer(traff)
        if not nr or any(n not in dokumentet for n in nr):
            raise ValueError(f"källan {kalla!r} är ingen sida i dokumentet")
        return "".join(dokumentet[n] for n in nr)

    return sidtext


def sidnummer(traff: re.Match) -> list[str]:
    forsta = int(traff["forsta"])
    sista = int(traff["sista"] or forsta)
    return [str(n) for n in range(forsta, sista + 1)]


def las_sidor(fil: Path) -> dict[str, str]:
    delar = SIDA.split(fil.read_text(encoding="utf-8"))
    return {
        nr: provbar(text) for nr, text in zip(delar[1::2], delar[2::2], strict=True)
    }


# Radbrytningarna ur PDF:en, punkterna först i en rad och
# Markdown-escapningen (ADR-0021) räknas inte.
def jamforbar(text: str) -> str:
    return " ".join(PUNKT.sub("", ESCAPNING.sub(r"\1", text)).split())


def provbar(text: str) -> str:
    return UTFYLLNAD.sub("", jamforbar(text))
