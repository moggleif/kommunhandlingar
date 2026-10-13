"""Krav: K6 i docs/02-KRAV.md, ADR-0038. Test: tests/test_ordning.py.

Text som inte går att läsa i ordning: roterade tecken, eller tecken på
samma rad som ritats ovanpå varandra, som en kolumn som flyter in i
nästa. pdfplumber blandar ihop dem till rader som
`aktivitetsstö2d0225-05-21`, och sidans tal räknas då inte som
bekräftade (docs/03-ARKITEKTUR.md#konvertering-och-kvalitet).
"""

from collections import defaultdict
from itertools import pairwise

from pdfplumber.page import Page


def i_oordning(sida: Page) -> bool:
    tecken = [(i, c) for i, c in enumerate(sida.chars) if not c["text"].isspace()]
    if not all(c["upright"] for _, c in tecken):
        return True
    rader = defaultdict(list)
    for i, c in tecken:
        rader[round(c["top"])].append((i, c))
    return any(map(ovanpa, rader.values()))


def ovanpa(rad: list[tuple[int, dict]]) -> bool:
    """Två tecken som täcker mer än halva det smalare av dem och inte står
    intill varandra i textlagret. Grannar som överlappar, som kursiv stil
    och tät spärrning, räknas inte, och inte heller samma tecken två gånger,
    som en fetstil som ritats två gånger."""
    i_lage = sorted(rad, key=lambda t: t[1]["x0"])
    return any(tacker(a, b) for a, b in pairwise(i_lage))


def tacker(vanster: tuple[int, dict], hoger: tuple[int, dict]) -> bool:
    (i, a), (j, b) = vanster, hoger
    smalast = min(a["x1"] - a["x0"], b["x1"] - b["x0"])
    grannar = abs(i - j) == 1
    return not grannar and a["text"] != b["text"] and a["x1"] - b["x0"] > smalast / 2
