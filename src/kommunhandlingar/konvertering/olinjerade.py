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
RADMELLANRUM = 3
BOKSTAV = re.compile(r"[^\W\d_]")
STRECK = re.compile(r"[-−–]")


@dataclass(frozen=True)
class Falt:
    text: str
    x0: float
    x1: float


@dataclass(frozen=True)
class Rad:
    ord: list[dict]
    falt: list[Falt] | None

    @property
    def hojd(self) -> float:
        return max(o["bottom"] - o["top"] for o in self.ord)


@dataclass(frozen=True)
class Tabell:
    bbox: tuple[float, float, float, float]
    rader: list[list[str]]
    antal_ord: int


def tabeller(sida: Page, upptagna: list[tuple]) -> list[Tabell]:
    alla = sida.extract_words(extra_attrs=["size"])
    fria = [o for o in alla if not any(inom(mitt(o), r) for r in upptagna)]
    rader_ = [rad(r) for r in cluster_objects(fria, "top", RADTOLERANS)]
    hittade = (tabell(rader_, foljd) for foljd in foljder(rader_))
    return [t for t in hittade if t and ensam(t, alla)]


def rad(ord_: list[dict]) -> Rad:
    ord_ = sorted(ord_, key=lambda o: o["x0"])
    return Rad(ord_, falt(ord_))


def falt(ord_: list[dict]) -> list[Falt] | None:
    grupper = [[ord_[0]]]
    for vanster, hoger in pairwise(ord_):
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


def uppdela(falt_: list[Falt] | None) -> tuple[Falt, list[Falt]] | None:
    if not falt_ or len(falt_) < 2 or not BOKSTAV.search(falt_[0].text):
        return None
    etikett, *celler = falt_
    ok = all(ar_tal(f) or STRECK.fullmatch(f.text) for f in celler)
    return (etikett, celler) if ok else None


def talrad(falt_: list[Falt]) -> bool:
    return sum(map(ar_tal, falt_)) >= 2


def har_tal(r: Rad) -> bool:
    if r.falt is None:
        return sum(1 for o in r.ord if TAL.fullmatch(o["text"])) >= 2
    return uppdela(r.falt) is not None or talrad(r.falt)


def nara(ovre: Rad, undre: Rad) -> bool:
    mellanrum = min(o["top"] for o in undre.ord) - max(o["bottom"] for o in ovre.ord)
    return mellanrum <= RADMELLANRUM * max(ovre.hojd, undre.hojd)


def foljder(rader_: list[Rad]) -> list[tuple[int, int]]:
    ut: list[tuple[int, int]] = []
    for i, r in enumerate(rader_):
        if not har_tal(r):
            continue
        if ut and ut[-1][1] == i and nara(rader_[i - 1], r):
            ut[-1] = (ut[-1][0], i + 1)
        else:
            ut.append((i, i + 1))
    return ut


def tabell(rader_: list[Rad], foljd: tuple[int, int]) -> Tabell | None:
    borjan, slut = foljd
    delar = [uppdela(r.falt) for r in rader_[borjan:slut]]
    if None in delar or sum(talrad(c) for _, c in delar) < MINSTA_FOLJD:
        return None
    kolumner_ = kolumner([f for _, c in delar for f in c if ar_tal(f)])
    if kolumner_ is None:
        return None
    etiketternas_slut = max(e.x1 for e, _ in delar)
    kropp = [kroppsrad(e, c, kolumner_) for e, c in delar]
    if None in kropp or not atskilda(kolumner_, etiketternas_slut):
        return None
    huvud = huvudet(rader_[: borjan + 1], kolumner_, etiketternas_slut)
    ord_ = [o for r in rader_[borjan - len(huvud) : slut] for o in r.ord]
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


def kroppsrad(etikett: Falt, celler: list[Falt], kolumner_: list) -> list[str] | None:
    rad_ = [etikett.text] + [""] * len(kolumner_)
    for f in celler:
        i = kolumn(f, kolumner_)
        if i is None:
            return None
        rad_[i + 1] = f.text
    return rad_


def atskilda(kolumner_: list[tuple[float, float]], etiketternas_slut: float) -> bool:
    granser = [etiketternas_slut] + [x1 for _, x1 in kolumner_[:-1]]
    return all(x0 > grans for (x0, _), grans in zip(kolumner_, granser, strict=True))


def huvudet(rader_: list[Rad], kolumner_: list, etiketternas_slut: float) -> list:
    huvud: list[list[str]] = []
    for ovre, undre in reversed(list(pairwise(rader_))):
        if not nara(ovre, undre):
            break
        rubrik = (
            None if har_tal(ovre) else huvudrad(ovre.falt, kolumner_, etiketternas_slut)
        )
        if rubrik is None:
            if not bara_etikett(ovre.falt, kolumner_):
                return []
            break
        huvud.insert(0, rubrik)
    return huvud if not huvud or all(huvud[0][1:]) else []


def huvudrad(falt_: list[Falt] | None, kolumner_: list, etiketternas_slut: float):
    if not falt_:
        return None
    rubrik = [""] * (len(kolumner_) + 1)
    if kolumn(falt_[0], kolumner_) is None and falt_[0].x1 < kolumner_[0][0]:
        rubrik[0], falt_ = falt_[0].text, falt_[1:]
    granser = [etiketternas_slut] + [x1 for _, x1 in kolumner_]
    for f in falt_:
        i = kolumn(f, kolumner_)
        if i is None or f.x0 <= granser[i]:
            return None
        rubrik[i + 1] = f.text
    return rubrik if any(rubrik[1:]) else None


def bara_etikett(falt_: list[Falt] | None, kolumner_: list) -> bool:
    return falt_ is not None and len(falt_) == 1 and falt_[0].x1 < kolumner_[0][0]


def ram(ord_: list[dict]) -> tuple[float, float, float, float]:
    return (
        min(o["x0"] for o in ord_),
        min(o["top"] for o in ord_),
        max(o["x1"] for o in ord_),
        max(o["bottom"] for o in ord_),
    )


def ensam(t: Tabell, alla: list[dict]) -> bool:
    return sum(1 for o in alla if inom(mitt(o), t.bbox)) == t.antal_ord
