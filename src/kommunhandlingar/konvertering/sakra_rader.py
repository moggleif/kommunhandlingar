"""Krav: K73 i docs/02-KRAV.md, ADR-0100. Test: tests/test_sakra_rader.py.

En inskannad sida som inte når OCR-tröskeln läses rad för rad: en rad där
Tesseract i medel är säker på minst 80 och som har ett ord med minst tre
bokstäver behålls. Punktutfyllnad räknas inte in i radens säkerhet. Sidan
läses också vriden 90° åt båda hållen, för text på högkant som i en
plankarta, och den läsning som ger flest ord i säkra rader gäller. Ger den
färre än 30 ord har sidan ingen text att lagra
(docs/03-ARKITEKTUR.md#inskannade-sidor-som-inte-blir-text). Fallerar
Tesseract i en vriden läsning är sidan inte läst (`Fallerade`).
"""

import re

from PIL import Image

from kommunhandlingar.konvertering import ocr

RADSAKERHET = 80
MINSTA_ORD = 30
VRIDNINGAR = (90, 270)
# Ett ord ur en innehållsförtecknings punktutfyllnad, som Tesseract läser
# osäkert; `ocr.UTFYLLNAD` rättar hela utfyllnaden i texten.
PUNKTORD = re.compile(r"\.{3,}|^[.,:;…s]{4,}$")
BOKSTAVER = re.compile(r"[^\W\d_]{3,}")


class Fallerade(Exception):
    """Tesseract fallerade eller blev inte klar i en vriden läsning."""


def las(gra: Image.Image, tsv: str) -> str | None:
    """De säkra raderna i den bästa läsningen; `tsv` är den raka sidans."""
    lasningar = [rader(tsv)] + [rader(vriden(gra, g)) for g in VRIDNINGAR]
    basta = max(lasningar, key=antal_ord)
    if antal_ord(basta) < MINSTA_ORD:
        return None
    return ocr.rensa("\n".join(basta))


def vriden(gra: Image.Image, grader: int) -> str:
    lasning = ocr.las_bild(gra.rotate(-grader, expand=True, fillcolor=255))
    if lasning is None:
        raise Fallerade
    return lasning[0]


def rader(tsv: str) -> list[str]:
    grupper: dict[tuple, list[dict]] = {}
    for ord_ in ocr.ordrader(tsv):
        nyckel = (ord_["block_num"], ord_["par_num"], ord_["line_num"])
        grupper.setdefault(nyckel, []).append(ord_)
    return [" ".join(o["text"] for o in rad) for rad in grupper.values() if saker(rad)]


def saker(rad: list[dict]) -> bool:
    ord_ = [o for o in rad if not PUNKTORD.search(o["text"])]
    if not any(BOKSTAVER.search(o["text"]) for o in ord_):
        return False
    return sum(float(o["conf"]) for o in ord_) / len(ord_) >= RADSAKERHET


def antal_ord(rader_: list[str]) -> int:
    return sum(len(rad.split()) for rad in rader_)
