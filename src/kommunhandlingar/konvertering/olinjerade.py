"""Krav: K5 och K19 i docs/02-KRAV.md, ADR-0016, ADR-0024, ADR-0035 och
ADR-0037. Test: tests/test_olinjerade.py, tests/test_mellanrader.py,
tests/test_rubrikrader.py och tests/test_skarvar.py.

En tabell utan lodräta linjer läses ur textlagrets ord, rad för rad, och blir
säker bara när varje rad är en etikett följd av tal och talen står i linje i
kolumner som inte överlappar (docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

import re
from dataclasses import dataclass
from itertools import pairwise

from pdfplumber.page import Page

from kommunhandlingar.konvertering import mellanrader
from kommunhandlingar.konvertering.falt import Falt, falt, radvis
from kommunhandlingar.konvertering.ombrutna import ombruten
from kommunhandlingar.konvertering.rader import (
    I_LINJE,
    MEST_EMELLAN,
    Rad,
    ar_tal,
    artalsrad,
    delad,
    etikettrad,
    har_tal,
    kolumn,
    med_fortsattning,
    nara,
    talrad,
    till_vanster,
    uppdela,
)
from kommunhandlingar.konvertering.rubriker import ovanfor
from kommunhandlingar.konvertering.tabeller import inom, mitt
from kommunhandlingar.konvertering.text import MINSTA_FOLJD

AR_ELLER_KOD = re.compile(r"\d{4}")


@dataclass(frozen=True)
class Tabell:
    bbox: tuple[float, float, float, float]
    rader: list[list[str]]
    antal_ord: int
    # Etiketternas vänsterkant och kolumnernas högerkanter (K19).
    kanter: tuple[float, ...]


def tabeller(sida: Page, upptagna: list[tuple]) -> list[Tabell]:
    alla = sida.extract_words(extra_attrs=["size"])
    rader_ = [Rad(r, falt(r)) for r in radvis(fria(alla, upptagna))]
    utan_broar = foljder(rader_, 0)
    hittade: list[Tabell | None] = []
    for borjan, slut in foljder(rader_, MEST_EMELLAN):
        hel = tabell(rader_, (borjan, slut))
        delar = [f for f in utan_broar if borjan <= f[0] < slut]
        hittade += [hel] if hel else [tabell(rader_, d) for d in delar]
    return [t for t in hittade if t and ensam(t, alla)]


def fria(ord_: list[dict], upptagna: list[tuple]) -> list[dict]:
    return [o for o in ord_ if not any(inom(mitt(o), r) for r in upptagna)]


def foljder(rader_: list[Rad], mest: int) -> list[tuple[int, int]]:
    """Rader med tal i följd, också över högst `mest` etikettrader mellan
    två tabellrader. En rad med bara årtal börjar ingen följd, och direkt
    ovanför en rad med tal är den nästa tabells rubrikrad."""
    ut: list[tuple[int, int]] = []
    for i, r in enumerate(rader_):
        if not har_tal(r) or rubrik_till_nasta(rader_, i):
            continue
        borjan, slut = ut[-1] if ut else (i, i)
        if (
            ut
            and bro(rader_[slut - 1 : i + 1], mest)
            and till_vanster(rader_[borjan:slut], r)
        ):
            ut[-1] = (borjan, i + 1)
        elif not artalsrad(r):
            ut.append((i, i + 1))
    return ut


def rubrik_till_nasta(rader_: list[Rad], i: int) -> bool:
    nasta = rader_[i + 1] if i + 1 < len(rader_) else None
    if not artalsrad(rader_[i]) or nasta is None:
        return False
    return har_tal(nasta) and not artalsrad(nasta) and nara(rader_[i], nasta)


def bro(rader_: list[Rad], mest: int) -> bool:
    ovre, *mellan, undre = rader_
    if len(mellan) > mest or not all(map(etikettrad, mellan)):
        return False
    if mellan and not (uppdela(ovre.falt) and uppdela(undre.falt)):
        return False
    return all(nara(a, b) for a, b in pairwise(rader_))


def tabell(rader_: list[Rad], foljd: tuple[int, int]) -> Tabell | None:
    borjan, slut = foljd[0], med_fortsattning(rader_, foljd[1])
    delar = [delad(r) for r in rader_[borjan:slut]]
    if None in delar or sum(talrad(c) for _, c in delar) < MINSTA_FOLJD:
        return None
    kolumner_ = kolumner([f for _, c in delar for f in c if ar_tal(f)])
    if kolumner_ is None:
        return None
    etiketternas_slut = max(e.x1 for e, _ in delar)
    kropp = kroppen(delar, kolumner_, etiketternas_slut)
    if kropp is None:
        return None
    rubriker, huvud = ovanfor(rader_[: borjan + 1], kolumner_, etiketternas_slut)
    ovanfor_ = rader_[borjan - len(rubriker) - len(huvud) : borjan]
    return byggd(ovanfor_ + rader_[borjan:slut], huvud + rubriker + kropp, kolumner_)


def byggd(rader_: list[Rad], celler: list[list[str]], kolumner_: list) -> Tabell:
    ord_ = [o for r in rader_ for o in r.ord]
    ruta = ram(ord_)
    return Tabell(ruta, celler, len(ord_), (ruta[0], *(x1 for _, x1 in kolumner_)))


def kroppen(delar: list, kolumner_: list, etiketternas_slut: float) -> list | None:
    kropp = [kroppsrad(e, c, kolumner_) for e, c in delar]
    if None in kropp or not atskilda(kolumner_, etiketternas_slut):
        return None
    kropp = mellanrader.foga(kropp)
    if ombruten(kropp):
        return None
    if all(AR_ELLER_KOD.fullmatch(r[1]) for r in kropp if r[1]):
        return None  # en etikettkolumn, och etiketterna till vänster är annan text
    return kropp


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


def ram(ord_: list[dict]) -> tuple[float, float, float, float]:
    return (
        min(o["x0"] for o in ord_),
        min(o["top"] for o in ord_),
        max(o["x1"] for o in ord_),
        max(o["bottom"] for o in ord_),
    )


def ensam(t: Tabell, alla: list[dict]) -> bool:
    return sum(1 for o in alla if inom(mitt(o), t.bbox)) == t.antal_ord
