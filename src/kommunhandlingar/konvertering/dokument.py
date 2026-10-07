"""Krav: K4–K6, ADR-0005 och ADR-0009. Test: tests/test_konvertering.py.

Läser en PDF sida för sida och ger Markdown-texten, tabellerna som CSV och
kvaliteten per sida och för dokumentet.
"""

import sys
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

import pdfplumber
import pypdfium2 as pdfium

from kommunhandlingar.konvertering import kvalitet
from kommunhandlingar.konvertering.las_sida import Sida, las_sida

VERKTYG = ("pdfplumber", "pdfminer.six")
PDF_BORJAN = b"%PDF-"


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


def versioner() -> list[str]:
    return [f"{namn} {version(namn)}" for namn in VERKTYG]


def konvertera(pdf: Path) -> Resultat:
    with pdf.open("rb") as fil:
        borjan = fil.read(1024)
    if PDF_BORJAN not in borjan:
        return Resultat("ej-konverterad", "inte-pdf")
    try:
        sidor = las_sidor(pdf)
    except pdfium.PdfiumError as fel:
        losenord = fel.err_code == pdfium.raw.FPDF_ERR_PASSWORD
        return Resultat("ej-konverterad", "krypterad" if losenord else "trasig-pdf")
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
            sidor.append(las_sida(sida, rendering[nr - 1]))
            sida.close()
        return sidor
