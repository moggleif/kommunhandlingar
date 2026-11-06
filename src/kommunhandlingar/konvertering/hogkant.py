"""Krav: K41 i docs/02-KRAV.md, ADR-0064. Test: tests/test_hogkant.py.

Text på högkant, som en stämpel eller ett diarienummer i marginalen, tas
ur sidans flöde och skrivs sist på sidan, en rad per rad på högkant
(docs/03-ARKITEKTUR.md#text-på-högkant). I textlagret är det tecknen som
inte står upprätt, och raden läses i sin riktning: uppåt när texten är
vriden moturs. I OCR-texten är det de ord som är minst dubbelt så höga
som breda och har minst fyra tecken; de målas vita och sidan läses om.
"""

import csv
from collections.abc import Iterable
from itertools import pairwise

from pdfplumber.page import Page
from PIL import Image, ImageDraw

MINSTA_ORD = 4
HOJD_MOT_BREDD = 2
ORDLUCKA = 0.2
STYCKESLUCKA = 2


def staende(sida: Page) -> Page:
    return sida.filter(lambda o: o["object_type"] != "char" or o["upright"])


def textlagret(sida: Page) -> list[str]:
    """Raderna på högkant i läsordning, med tecknen i läsriktningen."""
    rader: list[list[dict]] = []
    for c in sorted((c for c in sida.chars if not c["upright"]), key=lambda c: c["x0"]):
        if rader and c["x0"] - rader[-1][0]["x0"] < storlek(c):
            rader[-1].append(c)
        else:
            rader.append([c])
    rader.sort(key=lasordning)
    return [" ".join(t.split()) for r in rader for t in stycken(r) if t.strip()]


def stycken(tecken: list[dict]) -> list[str]:
    """Radens text i läsriktningen, delad där ett stort mellanrum skiljer
    två stämplar åt. Ett mellanrum större än ett mellanslag blir ett."""
    i_ordning = sorted(tecken, key=lambda c: c["top"], reverse=uppat(tecken[0]))
    delar = [i_ordning[0]["text"]]
    for fore, c in pairwise(i_ordning):
        lucka = abs(c["top"] - fore["top"]) - (c["bottom"] - c["top"])
        if lucka > STYCKESLUCKA * storlek(c):
            delar.append("")
        elif lucka > ORDLUCKA * storlek(c):
            delar[-1] += " "
        delar[-1] += c["text"]
    return delar


def lasordning(rad: list[dict]) -> tuple[bool, float]:
    """Moturs från vänster, medurs från höger: radens överkant pekar dit."""
    forsta = rad[0]
    return (not uppat(forsta), forsta["x0"] if uppat(forsta) else -forsta["x0"])


def uppat(tecken: dict) -> bool:
    """Vriden moturs: texten läses nerifrån och upp."""
    return tecken["matrix"][1] > 0


def storlek(tecken: dict) -> float:
    return tecken["x1"] - tecken["x0"]


def ocr_ord(tsv: str) -> list[dict]:
    """Tesseracts ord på de rader som har ett ord på högkant, i Tesseracts
    ordning, så att också korta ord i en stämpel kommer med."""
    ord_ = list(
        csv.DictReader(tsv.splitlines(), delimiter="\t", quoting=csv.QUOTE_NONE)
    )
    rader = {radnyckel(o) for o in ord_ if pa_hogkant(o)}
    return [o for o in ord_ if o["text"].strip() and radnyckel(o) in rader]


def radnyckel(ord_: dict) -> tuple[str, str, str, str]:
    return (ord_["page_num"], ord_["block_num"], ord_["par_num"], ord_["line_num"])


def pa_hogkant(ord_: dict) -> bool:
    text = ord_["text"].strip()
    hog = int(ord_["height"]) >= HOJD_MOT_BREDD * int(ord_["width"])
    return len(text) >= MINSTA_ORD and hog


def ocr_rader(ord_: list[dict]) -> list[str]:
    rader: dict[tuple, list[str]] = {}
    for o in ord_:
        rader.setdefault(radnyckel(o), []).append(o["text"])
    return [" ".join(r) for r in rader.values()]


def mala_vitt(bild: Image.Image, ord_: Iterable[dict]) -> None:
    rita = ImageDraw.Draw(bild)
    for o in ord_:
        x, y = int(o["left"]), int(o["top"])
        rita.rectangle((x, y, x + int(o["width"]), y + int(o["height"])), fill=255)


def sist(text: str, rader: list[str]) -> str:
    return "\n\n".join([text, *rader]) if rader else text
