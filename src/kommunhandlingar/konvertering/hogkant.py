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

from pdfplumber.page import Page
from PIL import Image, ImageDraw

MINSTA_ORD = 4
HOJD_MOT_BREDD = 2


def staende(sida: Page) -> Page:
    return sida.filter(lambda o: o.get("object_type") != "char" or o["upright"])


def textlagret(sida: Page) -> list[str]:
    """Raderna på högkant, från vänster, med tecknen i läsriktningen."""
    rader: list[list[dict]] = []
    for c in sorted((c for c in sida.chars if not c["upright"]), key=lambda c: c["x0"]):
        if rader and c["x0"] - rader[-1][0]["x0"] < c["x1"] - c["x0"]:
            rader[-1].append(c)
        else:
            rader.append([c])
    return [t for t in map(rad, rader) if t]


def rad(tecken: list[dict]) -> str:
    uppat = tecken[0]["matrix"][1] > 0
    i_ordning = sorted(tecken, key=lambda c: c["top"], reverse=uppat)
    return " ".join("".join(c["text"] for c in i_ordning).split())


def ocr_ord(tsv: str) -> list[dict]:
    """Tesseracts ord på högkant, i Tesseracts ordning."""
    rader = csv.DictReader(tsv.splitlines(), delimiter="\t", quoting=csv.QUOTE_NONE)
    return [r for r in rader if pa_hogkant(r)]


def pa_hogkant(ord_: dict) -> bool:
    text = ord_["text"].strip()
    hog = int(ord_["height"]) >= HOJD_MOT_BREDD * int(ord_["width"])
    return len(text) >= MINSTA_ORD and hog


def ocr_rader(ord_: list[dict]) -> list[str]:
    rader: dict[tuple, list[str]] = {}
    for o in ord_:
        rader.setdefault((o["block_num"], o["par_num"], o["line_num"]), []).append(
            o["text"]
        )
    return [" ".join(r) for r in rader.values()]


def mala_vitt(bild: Image.Image, ord_: Iterable[dict]) -> None:
    rita = ImageDraw.Draw(bild)
    for o in ord_:
        x, y = int(o["left"]), int(o["top"])
        rita.rectangle((x, y, x + int(o["width"]), y + int(o["height"])), fill=255)


def sist(text: str, rader: list[str]) -> str:
    return "\n\n".join([text, *rader]) if rader else text
