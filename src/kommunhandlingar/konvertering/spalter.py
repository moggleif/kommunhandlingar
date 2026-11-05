"""Krav: K41 i docs/02-KRAV.md, ADR-0062. Test: tests/test_spalter.py.

Sidans text i läsordning när löptext står i spalter bredvid varandra. Orden
fogas till radstycken, som bryts där luckan till nästa ord är minst en
radhöjd. Stycket delas sedan rekursivt (XY-snitt): lodrätt där inget
radstycke korsar och båda sidor är löptext, annars vågrätt vid den största
luckan. Ger snitten bara en ruta läses sidan som förut
(docs/03-ARKITEKTUR.md#spalter).
"""

from dataclasses import dataclass
from itertools import pairwise
from statistics import median

from pdfplumber.page import Page

MINSTA_RADER = 6
MINSTA_TECKEN = 25
MINSTA_BOKSTAVER = 0.7


@dataclass(frozen=True)
class Radstycke:
    x0: float
    top: float
    x1: float
    bottom: float
    text: str


def text(sida: Page) -> str:
    """Sidans text med uppställningen kvar, en spalt i taget."""
    delar = ordna(radstycken(sida.extract_words()))
    if len(delar) < 2:
        return sida.extract_text(layout=True)
    rutor = [sida.within_bbox(ruta(d), strict=False) for d in delar]
    return "\n\n".join(r.extract_text(layout=True) for r in rutor)


def radstycken(ord_: list[dict]) -> list[Radstycke]:
    return [stycke(delar) for rad in rader(ord_) for delar in delad(rad)]


def delad(rad: list[dict]) -> list[list[dict]]:
    """Raden delad vid varje lucka på minst en radhöjd."""
    delar = [[rad[0]]]
    for vanster, hoger in pairwise(rad):
        if lucka(vanster, hoger):
            delar.append([])
        delar[-1].append(hoger)
    return delar


def rader(ord_: list[dict]) -> list[list[dict]]:
    """Orden rad för rad: ett ord hör till raden om det börjar inom halva
    radhöjden från radens första ord."""
    rader_: list[list[dict]] = []
    for o in sorted(ord_, key=lambda o: o["top"]):
        if rader_ and o["top"] - rader_[-1][0]["top"] < hojd(rader_[-1][0]) / 2:
            rader_[-1].append(o)
        else:
            rader_.append([o])
    return [sorted(r, key=lambda o: o["x0"]) for r in rader_]


def lucka(vanster: dict, hoger: dict) -> bool:
    return hoger["x0"] - vanster["x1"] >= hojd(vanster)


def hojd(o: dict) -> float:
    return o["bottom"] - o["top"]


def stycke(ord_: list[dict]) -> Radstycke:
    return Radstycke(
        ord_[0]["x0"],
        min(o["top"] for o in ord_),
        ord_[-1]["x1"],
        max(o["bottom"] for o in ord_),
        " ".join(o["text"] for o in ord_),
    )


def ordna(stycken: list[Radstycke]) -> list[list[Radstycke]]:
    """Rutorna i läsordning: spalterna från vänster, banden uppifrån."""
    if delar := lodratt(stycken):
        return ordna(delar[0]) + ordna(delar[1])
    if not (delar := vagratt(stycken)):
        return [stycken]
    over, under = ordna(delar[0]), ordna(delar[1])
    return [stycken] if len(over) == len(under) == 1 else over + under


def lodratt(stycken: list[Radstycke]) -> tuple[list, list] | None:
    for x in luckor([(s.x0, s.x1) for s in stycken]):
        vanster = [s for s in stycken if s.x1 <= x]
        hoger = [s for s in stycken if s.x0 >= x]
        if loptext(vanster) and loptext(hoger):
            return vanster, hoger
    return None


def vagratt(stycken: list[Radstycke]) -> tuple[list, list] | None:
    kandidater = luckor([(s.top, s.bottom) for s in stycken])
    if not kandidater:
        return None
    y = max(kandidater, key=kandidater.get)
    return [s for s in stycken if s.bottom <= y], [s for s in stycken if s.top >= y]


def luckor(spann: list[tuple[float, float]]) -> dict[float, float]:
    """Mitten på varje lucka mellan spannen, med luckans storlek."""
    ut: dict[float, float] = {}
    slut = None
    for a, b in sorted(spann):
        if slut is not None and a > slut:
            ut[(slut + a) / 2] = a - slut
        slut = b if slut is None else max(slut, b)
    return ut


def loptext(stycken: list[Radstycke]) -> bool:
    """Tillräckligt många rader, tillräckligt långa, med mest bokstäver."""
    tecken = "".join(s.text for s in stycken).replace(" ", "")
    bokstaver = sum(c.isalpha() for c in tecken)
    return (
        len({round(s.top) for s in stycken}) >= MINSTA_RADER
        and median(len(s.text) for s in stycken) >= MINSTA_TECKEN
        and bokstaver >= MINSTA_BOKSTAVER * len(tecken)
    )


def ruta(stycken: list[Radstycke]) -> tuple[float, float, float, float]:
    return (
        min(s.x0 for s in stycken),
        min(s.top for s in stycken),
        max(s.x1 for s in stycken),
        max(s.bottom for s in stycken),
    )
