"""Krav: K54 i docs/02-KRAV.md, ADR-0078. Test: tests/test_sammantradessida.py.

Ett sammanträde punkt för punkt: dagordningen ur kallelsen och, för varje
punkt, diarienumret, handlingens sidor, sammanfattningen, beslutet och
historiken i alla organ. Kallelsen skriver diarienumret utan organets
förled; punktens nummer är det i protokollet eller handlingen som slutar
med kallelsens, och annars kallelsens.
"""

from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from pathlib import PurePosixPath

from kommunhandlingar.kandidat import TYPORDNING
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.dagordning import Punkt, dagordning
from kommunhandlingar.webbplats.kortkoppling import Kortlank
from kommunhandlingar.webbplats.punktsidor import (
    ar_punktens,
    diarienummer,
    handlingen,
    sammanfattning,
)


# Det kommunens sammanträden delar.
@dataclass(frozen=True)
class Underlag:
    kommun: Kommun
    # Kommunens dokument, front matter med `adress` i kommunens katalog.
    dokument: list[dict]
    paragrafer: list[dict]
    per_nummer: dict[str, list[dict]]
    kort: dict[str, list[Kortlank]]


@dataclass(frozen=True)
class Mote:
    kommun: Kommun
    # Sammanträdets dokument, front matter med `adress` i kommunens katalog.
    dokument: list[dict]
    kallelse: str
    handlingar: dict[int, str]
    # Sammanträdets egna paragrafer, ur kommunens.
    egna: list[dict]

    @cached_property
    def punkter(self) -> list[Punkt]:
        return dagordning(self.kallelse)

    @cached_property
    def omfang(self) -> dict[int, range]:
        return handlingen(self.handlingar, self.punkter)


@dataclass(frozen=True)
class Arende:
    punkt: Punkt
    diarienummer: str
    handling: range | None
    sammanfattning: tuple[str, ...]
    beslut: dict | None
    historik: list[dict]
    kort: list[Kortlank]


def per_nummer(paragrafer: list[dict]) -> dict[str, list[dict]]:
    index = defaultdict(list)
    for p in paragrafer:
        for nummer in p["diarienummer"]:
            index[nummer].append(p)
    return index


def moten(underlag: Underlag) -> list[list[dict]]:
    per_mote = defaultdict(list)
    for d in underlag.dokument:
        per_mote[mappen(d)].append(d)
    return [m for m in per_mote.values() if har_sida(underlag.kommun, m)]


def mappen(dokument: dict) -> str:
    return PurePosixPath(dokument["adress"]).parent.as_posix()


def egna(underlag: Underlag, dokument: list[dict]) -> list[dict]:
    mapp = PurePosixPath("data", underlag.kommun.id, mappen(dokument[0]))
    return [p for p in underlag.paragrafer if PurePosixPath(p["fil"]).parent == mapp]


# Dokumenten i typernas ordning, och inom typen det utan namn först och
# sedan de namngivna i bokstavsordning.
def ordnade(dokument: list[dict]) -> list[dict]:
    return sorted(dokument, key=lambda d: (TYPORDNING.index(d["typ"]), namnet(d)))


def namnet(d: dict) -> tuple[bool, str]:
    return d["namn"] != "null", d["namn"]


# Sammanträdets katalog med `.html`, i kommunens katalog: `ks/2026/2026-10-20.html`.
def adress(dokument: list[dict]) -> str:
    return mappen(dokument[0]) + ".html"


def har_sida(kommun: Kommun, dokument: list[dict]) -> bool:
    forsta = dokument[0]
    organ = next(o for o in kommun.organ if o.id == forsta["organ"])
    fran = organ.sammantradessidor
    kallelse = any(d["typ"] == "kallelse" for d in dokument)
    return fran is not None and int(forsta["datum"][:4]) >= fran and kallelse


def arenden(mote: Mote, underlag: Underlag) -> list[Arende]:
    return [arende(p, mote, underlag) for p in mote.punkter]


def arende(punkt: Punkt, mote: Mote, underlag: Underlag) -> Arende:
    omfang = mote.omfang.get(punkt.nummer)
    i_handlingen = [n for s in omfang or () for n in diarienummer(mote.handlingar[s])]
    i_protokollet = [n for p in mote.egna for n in p["diarienummer"]]
    nummer = fullt(punkt, i_protokollet + i_handlingen)
    numren = dict.fromkeys([nummer, *i_handlingen])
    return Arende(
        punkt,
        nummer,
        omfang,
        sammanfattning(mote.handlingar, omfang) if omfang else (),
        next((p for p in mote.egna if nummer in p["diarienummer"]), None),
        historik(numren, mote, underlag),
        list(dict.fromkeys(k for n in numren for k in underlag.kort.get(n, []))),
    )


def fullt(punkt: Punkt, kandidater: list[str]) -> str:
    return next((n for n in kandidater if ar_punktens(n, punkt)), punkt.diarienummer)


def historik(numren: dict[str, None], mote: Mote, underlag: Underlag) -> list[dict]:
    egna = {id(p) for p in mote.egna}
    funna = {id(p): p for n in numren for p in underlag.per_nummer.get(n, [])}
    andra = [p for i, p in funna.items() if i not in egna]
    return sorted(andra, key=lambda p: (p["datum"], p["organ"], p["paragraf"]))
