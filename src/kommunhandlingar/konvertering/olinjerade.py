"""Krav: K5 i docs/02-KRAV.md, ADR-0016. Test: tests/test_olinjerade.py.

En tabell utan lodräta linjer läses ur textlagrets ord, rad för rad, och blir
säker bara när varje rad är en etikett följd av tal och talen står i linje i
kolumner som inte överlappar (docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

import re
from dataclasses import dataclass
from itertools import pairwise

from pdfplumber.page import Page
from pdfplumber.utils import cluster_objects

from kommunhandlingar.konvertering.tabeller import inom, mitt
from kommunhandlingar.konvertering.text import MINSTA_FOLJD, TAL

RADTOLERANS = 3
I_LINJE = 2
SAMMA_FALT = 0.5
NYTT_FALT = 1.0
BOKSTAV = re.compile(r"[^\W\d_]")
STRECK = re.compile(r"[-−–]")


@dataclass(frozen=True)
class Falt:
    text: str
    x0: float
    x1: float


@dataclass(frozen=True)
class Tabell:
    bbox: tuple[float, float, float, float]
    rader: list[list[str]]
    antal_ord: int


def tabeller(sida: Page) -> list[Tabell]:
    ord_ = sida.extract_words()
    rader_ = [
        sorted(r, key=lambda o: o["x0"])
        for r in cluster_objects(ord_, "top", RADTOLERANS)
    ]
    falt_ = [falt(rad) for rad in rader_]
    hittade = (tabell(rader_, falt_, foljd) for foljd in foljder(falt_, rader_))
    return [t for t in hittade if t and ensam(t, ord_)]


def falt(rad: list[dict]) -> list[Falt] | None:
    grupper = [[rad[0]]]
    for vanster, hoger in pairwise(rad):
        mellanrum = hoger["x0"] - vanster["x1"]
        hojd = max(o["bottom"] - o["top"] for o in (vanster, hoger))
        if mellanrum <= SAMMA_FALT * hojd:
            grupper[-1].append(hoger)
        elif mellanrum >= NYTT_FALT * hojd:
            grupper.append([hoger])
        else:
            return None
    return [
        Falt(" ".join(o["text"] for o in g), g[0]["x0"], g[-1]["x1"]) for g in grupper
    ]


def ar_tal(f: Falt) -> bool:
    return TAL.fullmatch(f.text) is not None


def ar_cell(f: Falt) -> bool:
    return ar_tal(f) or STRECK.fullmatch(f.text) is not None


def uppdela(falt_: list[Falt] | None) -> tuple[Falt, list[Falt]] | None:
    if not falt_ or len(falt_) < 2 or not BOKSTAV.search(falt_[0].text):
        return None
    etikett, *tal = falt_
    return (etikett, tal) if all(map(ar_cell, tal)) else None


def talrad(falt_: list[Falt]) -> bool:
    return sum(map(ar_tal, falt_)) >= 2


def har_tal(falt_: list[Falt] | None, rad: list[dict]) -> bool:
    if falt_ is None:
        return sum(1 for o in rad if TAL.fullmatch(o["text"])) >= 2
    return uppdela(falt_) is not None or talrad(falt_)


def foljder(falt_: list, rader_: list) -> list[tuple[int, int]]:
    ut, borjan = [], None
    for i, (f, rad) in enumerate(zip(falt_ + [[]], rader_ + [[]], strict=True)):
        if rad and har_tal(f, rad):
            borjan = i if borjan is None else borjan
        elif borjan is not None:
            ut.append((borjan, i))
            borjan = None
    return ut


def tabell(rader_: list, falt_: list, foljd: tuple[int, int]) -> Tabell | None:
    borjan, slut = foljd
    delar = [uppdela(f) for f in falt_[borjan:slut]]
    if None in delar or sum(talrad(d[1]) for d in delar) < MINSTA_FOLJD:
        return None
    kolumner_ = kolumner([f for _, tal in delar for f in tal])
    if kolumner_ is None:
        return None
    kropp = [kroppsrad(e, tal, kolumner_) for e, tal in delar]
    if None in kropp or not atskilda(kolumner_, max(e.x1 for e, _ in delar)):
        return None
    huvud = huvudet(list(zip(falt_[:borjan], rader_[:borjan], strict=True)), kolumner_)
    ord_ = [o for rad in rader_[borjan - len(huvud) : slut] for o in rad]
    return Tabell(ram(ord_), huvud + kropp, len(ord_))


def kolumner(tal: list[Falt]) -> list[tuple[float, float]] | None:
    """Talen grupperade efter högerkanten; None om en kolumn har ett enda tal."""
    kanter = sorted(tal, key=lambda f: f.x1)
    grupper = [[kanter[0]]]
    for f in kanter[1:]:
        if f.x1 - grupper[-1][0].x1 <= I_LINJE:
            grupper[-1].append(f)
        else:
            grupper.append([f])
    if any(len(g) < 2 for g in grupper):
        return None
    return [(min(f.x0 for f in g), max(f.x1 for f in g)) for g in grupper]


def kolumn(f: Falt, kolumner_: list[tuple[float, float]]) -> int | None:
    traffar = [i for i, (_, x1) in enumerate(kolumner_) if abs(f.x1 - x1) <= I_LINJE]
    return traffar[0] if len(traffar) == 1 else None


def kroppsrad(etikett: Falt, tal: list[Falt], kolumner_: list) -> list[str] | None:
    rad = [etikett.text] + [""] * len(kolumner_)
    for f in tal:
        i = kolumn(f, kolumner_)
        if i is None or rad[i + 1]:
            return None
        rad[i + 1] = f.text
    return rad


def atskilda(kolumner_: list[tuple[float, float]], etiketternas_slut: float) -> bool:
    granser = [etiketternas_slut] + [x1 for _, x1 in kolumner_[:-1]]
    return all(x0 > grans for (x0, _), grans in zip(kolumner_, granser, strict=True))


def huvudet(ovanfor: list, kolumner_: list) -> list[list[str]]:
    huvud: list[list[str]] = []
    for falt_, rad_ in reversed(ovanfor):
        rad = None if har_tal(falt_, rad_) else huvudrad(falt_, kolumner_)
        if rad is None:
            return huvud if bara_etikett(falt_, kolumner_) else []
        huvud.insert(0, rad)
    return huvud


def huvudrad(falt_: list[Falt] | None, kolumner_: list) -> list[str] | None:
    if not falt_:
        return None
    rad = [""] * (len(kolumner_) + 1)
    if kolumn(falt_[0], kolumner_) is None and falt_[0].x1 < kolumner_[0][0]:
        rad[0], falt_ = falt_[0].text, falt_[1:]
    granser = [float("-inf")] + [x1 for _, x1 in kolumner_]
    for f in falt_:
        i = kolumn(f, kolumner_)
        if i is None or rad[i + 1] or f.x0 <= granser[i]:
            return None
        rad[i + 1] = f.text
    return rad if any(rad[1:]) else None


def bara_etikett(falt_: list[Falt] | None, kolumner_: list) -> bool:
    return falt_ is not None and len(falt_) == 1 and falt_[0].x1 < kolumner_[0][0]


def ram(ord_: list[dict]) -> tuple[float, float, float, float]:
    return (
        min(o["x0"] for o in ord_),
        min(o["top"] for o in ord_),
        max(o["x1"] for o in ord_),
        max(o["bottom"] for o in ord_),
    )


def ensam(t: Tabell, ord_: list[dict]) -> bool:
    """Inget annat ord än tabellens får ha sin mittpunkt inom tabellens ram."""
    return sum(1 for o in ord_ if inom(mitt(o), t.bbox)) == t.antal_ord
