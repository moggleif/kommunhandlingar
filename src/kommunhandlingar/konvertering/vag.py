"""Krav: K6 i docs/02-KRAV.md, ADR-0005. Test: tests/test_konvertering.py.

Vilken väg en sida tar enligt "Konvertering och kvalitet" i
docs/03-ARKITEKTUR.md: `tom`, `ocr` eller `text`. Den första regeln som
stämmer gäller.
"""

import unicodedata
from collections.abc import Callable

from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfplumber.page import Page

TOM_ANDEL = 0.005
SKANNING_TACKNING = 0.9
SKANNING_TECKEN = 50
OLASLIGT_ANDEL = 0.01
OSYNLIG = 3


def vag(sida: Page, ej_vita: Callable[[], float]) -> str:
    if not sida.chars:
        return "tom" if ej_vita() <= TOM_ANDEL else "ocr"
    if ar_skanning(sida) or olasliga(sida) > OLASLIGT_ANDEL * len(sida.chars):
        return "ocr"
    return "text"


def ar_skanning(sida: Page) -> bool:
    yta = sida.width * sida.height
    tacker = tackt_yta([ruta(b, sida) for b in sida.images]) >= SKANNING_TACKNING * yta
    return tacker and synliga_tecken(sida) < SKANNING_TECKEN


def ruta(bild: dict, sida: Page) -> tuple[float, float, float, float]:
    return (
        max(bild["x0"], 0),
        max(bild["top"], 0),
        min(bild["x1"], sida.width),
        min(bild["bottom"], sida.height),
    )


def tackt_yta(rutor: list[tuple[float, float, float, float]]) -> float:
    xs = sorted({x for r in rutor for x in (r[0], r[2])})
    yta = 0.0
    for vanster, hoger in zip(xs, xs[1:], strict=False):
        spann = sorted((r[1], r[3]) for r in rutor if r[0] <= vanster and r[2] >= hoger)
        yta += (hoger - vanster) * langd_av(spann)
    return yta


def langd_av(spann: list[tuple[float, float]]) -> float:
    langd, slut = 0.0, float("-inf")
    for borjan, stopp in spann:
        langd += max(0.0, stopp - max(borjan, slut))
        slut = max(slut, stopp)
    return langd


def olasliga(sida: Page) -> int:
    return sum(1 for tecken in sida.chars if ar_olasligt(tecken["text"]))


def ar_olasligt(text: str) -> bool:
    return (
        text.startswith("(cid:")
        or "�" in text
        or any(unicodedata.category(t) == "Cc" for t in text)
    )


class Raknare(PDFDevice):
    """Räknar tecknen som ritas synligt; renderingsläge 3 är osynlig text."""

    antal = 0

    def render_string(self, textstate, seq, ncs, graphicstate):
        if textstate.render == OSYNLIG:
            return
        for del_ in seq:
            if isinstance(del_, bytes):
                self.antal += len(list(textstate.font.decode(del_)))


def synliga_tecken(sida: Page) -> int:
    resurser = PDFResourceManager()
    raknare = Raknare(resurser)
    PDFPageInterpreter(resurser, raknare).process_page(sida.page_obj)
    return raknare.antal
