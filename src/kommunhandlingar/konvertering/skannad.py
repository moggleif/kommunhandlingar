"""Krav: K6, K15 och K72 i docs/02-KRAV.md, ADR-0005 och ADR-0099.
Test: tests/test_skannad.py och tests/test_konvertering.py.

En sida som läses med OCR. Når den inte tröskeln maskas bildytan och
sidan läses om, sedan vänds den om Tesseract säger att den ligger fel.
Ger inget text blir sidan `bild` när den till största delen är en jämn
bildyta, `tom` när nästan inget är mörkt, och annars `ej-konverterad`
(docs/03-ARKITEKTUR.md#inskannade-sidor-som-inte-blir-text).
"""

from dataclasses import dataclass

import pypdfium2 as pdfium
from PIL import Image, ImageDraw

from kommunhandlingar.konvertering import bildyta, ocr, riktning

FARG_DPI = 100
FIGUR = 0.04
BILD = 0.6
NASTAN_TOM = 0.005


@dataclass(frozen=True)
class Skannad:
    kvalitet: str
    text: str = ""
    figur: bool = False


def las(rendering: pdfium.PdfPage) -> Skannad:
    gra = ocr.rendera(rendering)
    farg = rendering.render(scale=FARG_DPI / 72).to_pil()
    forsta = ocr.las(gra)
    skala = FARG_DPI / ocr.DPI
    yta = bildyta.storsta(farg, [skalad(r, skala) for r in forsta.ord])
    figur = yta.andel >= FIGUR and yta.jamn
    text = forsta.text
    if text is None:
        text = omlast(gra, skalad(yta.ruta, 1 / skala) if figur else None)
    if text is not None:
        return Skannad("ocr", text, figur)
    if yta.andel >= BILD and yta.jamn:
        return Skannad("bild", figur=True)
    if bildyta.mork_andel(farg) <= NASTAN_TOM:
        return Skannad("tom")
    return Skannad("ej-konverterad", figur=figur)


def omlast(gra: Image.Image, bildruta: tuple | None) -> str | None:
    """Sidan med bildytan vit, och sedan vänd, tills en läsning når tröskeln."""
    if bildruta is not None:
        text = ocr.las(maskad(gra, bildruta)).text
        if text is not None:
            return text
    grader = riktning.grader(gra)
    if not grader:
        return None
    return ocr.las(gra.rotate(-grader, expand=True, fillcolor=255)).text


def maskad(bild: Image.Image, ruta: tuple) -> Image.Image:
    kopia = bild.copy()
    ImageDraw.Draw(kopia).rectangle(ruta, fill=255)
    return kopia


def skalad(ruta: tuple, skala: float) -> tuple[int, int, int, int]:
    return tuple(int(v * skala) for v in ruta)
