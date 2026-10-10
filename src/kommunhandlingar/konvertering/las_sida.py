"""Krav: K5, K6, K15 och K17 i docs/02-KRAV.md, ADR-0005, ADR-0016,
ADR-0017 och ADR-0022. Test: tests/test_konvertering.py, tests/test_maskning.py.

En sida blir `tom`, läses ur textlagret, eller läses med OCR. En OCR-sida
får inga tabeller, och dess tal är aldrig bekräftade. En sida som inte är
tom prövas för figurer. Personuppgifterna maskas i text och celler innan
sidan lämnas vidare.
"""

from dataclasses import dataclass, field, replace

import pypdfium2 as pdfium
from pdfplumber.page import Page

from kommunhandlingar.konvertering import figurer, markdown, ocr, olinjerade, tabeller
from kommunhandlingar.konvertering.personuppgifter import maska
from kommunhandlingar.konvertering.text import komprimera, stycken
from kommunhandlingar.konvertering.vag import olasliga, vag

RENDERING_72_DPI = 1


@dataclass(frozen=True)
class Sida:
    kvalitet: str
    tal_obekraftade: bool
    text: str = ""
    tabeller: list[list[list[str]]] = field(default_factory=list)
    figur: bool = False


def las_sida(sida: Page, rendering: pdfium.PdfPage) -> Sida:
    match vag(sida, lambda: ej_vita(rendering)):
        case "tom":
            return Sida("tom", False)
        case "ocr":
            return maskad(ocr_sida(rendering, figurer.har_figur(sida, [])))
    return maskad(textsida(sida))


def maskad(sida: Sida) -> Sida:
    tabeller_ = [[[maska(c) for c in rad] for rad in t] for t in sida.tabeller]
    return replace(sida, text=maska(sida.text), tabeller=tabeller_)


def ocr_sida(rendering: pdfium.PdfPage, figur: bool) -> Sida:
    text = ocr.las(rendering)
    if text is None:
        return Sida("ej-konverterad", True, figur=figur)
    rader = [markdown.rad(r) for r in text.splitlines()]
    return Sida("ocr", True, komprimera(rader), figur=figur)


def ej_vita(rendering: pdfium.PdfPage) -> float:
    bild = rendering.render(scale=RENDERING_72_DPI).to_pil().convert("L")
    staplar = bild.histogram()
    return 1 - staplar[255] / sum(staplar)


def textsida(sida: Page) -> Sida:
    linjerade, fallda = tabeller.sakra(sida)
    rutor = [t.bbox for t in linjerade]
    utan_linjer = olinjerade.tabeller(sida, rutor)
    rutor += [t.bbox for t in utan_linjer]
    utanfor = sida.filter(lambda o: not i_tabell(o, rutor))
    text, osaker = stycken(utanfor.extract_text(layout=True))
    osaker = osaker or any(olast_siffra(c, fallda, rutor) for c in sida.chars)
    hittade = [(t.bbox, tabeller.rader(t)) for t in linjerade]
    hittade += [(t.bbox, t.rader) for t in utan_linjer]
    hittade.sort(key=lambda t: (round(t[0][1]), t[0][0]))
    return Sida(
        "tabell-osaker" if osaker else "ok",
        olasliga(sida) > 0,
        text,
        [rader for _, rader in hittade],
        figurer.har_figur(sida, rutor),
    )


def olast_siffra(tecken: dict, fallda: list[tuple], rutor: list[tuple]) -> bool:
    """En siffra i en fälld tabell med linjer som inte lästs i någon tabell."""
    i_fallda = any(tabeller.inom(tabeller.mitt(tecken), f) for f in fallda)
    return tecken["text"].isdigit() and i_fallda and not i_tabell(tecken, rutor)


def i_tabell(objekt: dict, rutor: list[tuple]) -> bool:
    if objekt.get("object_type") != "char":
        return False
    return any(tabeller.inom(tabeller.mitt(objekt), ruta) for ruta in rutor)
