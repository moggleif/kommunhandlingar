"""Krav: K5 och K6 i docs/02-KRAV.md, ADR-0005. Test: tests/test_konvertering.py.

En sida blir `tom`, läses ur textlagret, eller läses med OCR. En OCR-sida
får inga tabeller, och dess tal är aldrig bekräftade.
"""

from dataclasses import dataclass, field

import pypdfium2 as pdfium
from pdfplumber.page import Page

from kommunhandlingar.konvertering import ocr, tabeller
from kommunhandlingar.konvertering.text import komprimera, stycken
from kommunhandlingar.konvertering.vag import olasliga, vag

RENDERING_72_DPI = 1


@dataclass(frozen=True)
class Sida:
    kvalitet: str
    tal_obekraftade: bool
    text: str = ""
    tabeller: list[list[list[str]]] = field(default_factory=list)


def las_sida(sida: Page, rendering: pdfium.PdfPage) -> Sida:
    match vag(sida, lambda: ej_vita(rendering)):
        case "tom":
            return Sida("tom", False)
        case "ocr":
            return ocr_sida(rendering)
    return textsida(sida)


def ocr_sida(rendering: pdfium.PdfPage) -> Sida:
    text = ocr.las(rendering)
    if text is None:
        return Sida("ej-konverterad", True)
    return Sida("ocr", True, komprimera(text.splitlines()))


def ej_vita(rendering: pdfium.PdfPage) -> float:
    bild = rendering.render(scale=RENDERING_72_DPI).to_pil().convert("L")
    staplar = bild.histogram()
    return 1 - staplar[255] / sum(staplar)


def textsida(sida: Page) -> Sida:
    sakra = tabeller.sakra(sida)
    rutor = [t.bbox for t in sakra]
    utanfor = sida.filter(lambda o: not i_tabell(o, rutor))
    text, osaker = stycken(utanfor.extract_text(layout=True))
    return Sida(
        "tabell-osaker" if osaker else "ok",
        olasliga(sida) > 0,
        text,
        [tabeller.rader(t) for t in sakra],
    )


def i_tabell(objekt: dict, rutor: list[tuple]) -> bool:
    if objekt.get("object_type") != "char":
        return False
    return any(tabeller.inom(tabeller.mitt(objekt), ruta) for ruta in rutor)
