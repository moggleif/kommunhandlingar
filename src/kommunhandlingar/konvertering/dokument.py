"""Krav: K4–K6, K52 och K55, ADR-0005, ADR-0009, ADR-0075 och ADR-0079.
Test: tests/test_konvertering.py och tests/test_tidsbudget.py.

Läser en PDF sida för sida och ger Markdown-texten, tabellerna som CSV och
kvaliteten per sida och för dokumentet. En sida med fler tecken än taket
läses inte: den blir `ej-konverterad` och märks som figur. Blir läsningen
inte klar inom dokumentets tidsgräns är dokumentet `ej-konverterad` med
`fel: tidsgrans`.
"""

import sys
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

import pdfplumber
import pypdfium2 as pdfium

from kommunhandlingar import tidsbudget
from kommunhandlingar.konvertering import kvalitet, ocr
from kommunhandlingar.konvertering.las_sida import Sida, las_sida

VERKTYG = ("pdfplumber", "pdfminer.six")
PDF_BORJAN = b"%PDF-"
TECKENTAK = 500_000
TUNG_SIDA = Sida("ej-konverterad", True, figur=True)


@dataclass(frozen=True)
class Resultat:
    kvalitet: str
    fel: str | None = None
    sidor: list[Sida] | None = None

    @property
    def kvalitet_per_sida(self) -> list[str] | None:
        return None if self.sidor is None else [s.kvalitet for s in self.sidor]

    @property
    def tal_obekraftade(self) -> list[int] | None:
        if self.sidor is None:
            return None
        return [nr for nr, s in enumerate(self.sidor, 1) if s.tal_obekraftade]

    @property
    def figurer(self) -> list[int] | None:
        if self.sidor is None:
            return None
        return [nr for nr, s in enumerate(self.sidor, 1) if s.figur]


def kvalitetsfalt(poolens_version: str, resultat: Resultat) -> dict:
    return {
        "sidor": len(resultat.sidor) if resultat.sidor else None,
        "pipeline": " / ".join([poolens_version, *versioner(resultat)]),
        "kvalitet": resultat.kvalitet,
        "fel": resultat.fel,
        "kvalitet_per_sida": resultat.kvalitet_per_sida,
        "tal_obekraftade": resultat.tal_obekraftade,
        "figurer": resultat.figurer,
        "tolkade": None if resultat.figurer is None else [],
    }


def versioner(resultat: Resultat) -> list[str]:
    lasta = [f"{namn} {version(namn)}" for namn in VERKTYG]
    kvaliteter = set(resultat.kvalitet_per_sida or [])
    lasta_med_ocr = kvaliteter & {"ocr", "bild", "ej-konverterad"}
    return lasta + (ocr.verktyg() if lasta_med_ocr else [])


def oppningsfel(fel: pdfium.PdfiumError) -> str:
    losenord = fel.err_code == pdfium.raw.FPDF_ERR_PASSWORD
    return "krypterad" if losenord else "trasig-pdf"


def konvertera(pdf: Path) -> Resultat:
    with pdf.open("rb") as fil:
        borjan = fil.read(1024)
    if PDF_BORJAN not in borjan:
        return Resultat("ej-konverterad", "inte-pdf")
    try:
        with tidsbudget.hogst(tidsbudget.DOKUMENT):
            sidor = las_sidor(pdf)
    except tidsbudget.Dokumentgrans:
        return Resultat("ej-konverterad", tidsbudget.FEL)
    except pdfium.PdfiumError as fel:
        return Resultat("ej-konverterad", oppningsfel(fel))
    except Exception as fel:
        # pdfminer kastar godtyckliga undantag (TypeError, IndexError, …) för
        # trasiga filer. En fil får inte stoppa körningen; orsaken syns i loggen.
        print(f"{pdf.name}: {type(fel).__name__}: {fel}", file=sys.stderr)
        return Resultat("ej-konverterad", "trasig-pdf")
    if not sidor:
        return Resultat("ej-konverterad", "trasig-pdf")
    return Resultat(kvalitet.dokumentets([s.kvalitet for s in sidor]), sidor=sidor)


def las_sidor(pdf: Path) -> list[Sida]:
    with pdfium.PdfDocument(pdf) as rendering, pdfplumber.open(pdf) as dokument:
        sidor = []
        for nr, sida in enumerate(dokument.pages, 1):
            sidor.append(las_under_taket(sida, rendering[nr - 1]))
            sida.close()
        return sidor


def las_under_taket(sida: pdfplumber.page.Page, rendering: pdfium.PdfPage) -> Sida:
    if tecken(rendering) > TECKENTAK:
        return TUNG_SIDA
    return las_sida(sida, rendering)


def tecken(rendering: pdfium.PdfPage) -> int:
    textsida = rendering.get_textpage()
    antal = textsida.count_chars()
    textsida.close()
    return antal
