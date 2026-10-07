"""Krav: K6 i docs/02-KRAV.md, ADR-0005. Test: tests/test_konvertering.py.

En sida som ska läsas med OCR renderas med pypdfium2 i 300 dpi, i gråskala,
och läses av Tesseract med svensk modell. Säkerheten är medelvärdet av
Tesseracts säkerhet för de ord den känt igen; under tröskeln, eller utan
ord, är sidan `ej-konverterad`.
"""

import csv
import subprocess
import tempfile
from functools import cache
from importlib.metadata import version
from pathlib import Path

import pypdfium2 as pdfium

DPI = 300
SPRAK = "swe"
TROSKEL = 70


def las(rendering: pdfium.PdfPage) -> str | None:
    """Sidans OCR-text, eller None när den inte når tröskeln."""
    with tempfile.TemporaryDirectory() as katalog:
        bild = Path(katalog) / "sida.png"
        rendering.render(scale=DPI / 72, grayscale=True).to_pil().save(bild)
        ut = Path(katalog) / "ut"
        subprocess.run(
            ["tesseract", bild, ut, "-l", SPRAK, "--dpi", str(DPI), "txt", "tsv"],
            check=True,
            capture_output=True,
        )
        sakerhet = medelsakerhet(ut.with_suffix(".tsv").read_text(encoding="utf-8"))
        if sakerhet is None or sakerhet < TROSKEL:
            return None
        return ut.with_suffix(".txt").read_text(encoding="utf-8").strip()


def medelsakerhet(tsv: str) -> float | None:
    rader = csv.DictReader(tsv.splitlines(), delimiter="\t", quoting=csv.QUOTE_NONE)
    varden = [
        float(r["conf"]) for r in rader if r["text"].strip() and r["conf"] != "-1"
    ]
    return sum(varden) / len(varden) if varden else None


@cache
def verktyg() -> list[str]:
    """pypdfium2, Tesseract och språkmodellen, med version, för `pipeline`."""
    svar = subprocess.run(
        ["tesseract", "--version"], check=True, capture_output=True, text=True
    )
    tesseract = (svar.stdout or svar.stderr).split()[1]
    return [
        f"pypdfium2 {version('pypdfium2')}",
        f"tesseract {tesseract} {SPRAK} {modellversion()}",
    ]


def modellversion() -> str:
    """Paketversionen av språkmodellen, utan epok och revision (1:4.1.0-2 → 4.1.0)."""
    svar = subprocess.run(
        ["dpkg-query", "-W", "-f=${Version}", f"tesseract-ocr-{SPRAK}"],
        capture_output=True,
        text=True,
    )
    if svar.returncode != 0:
        return "okänd"
    return svar.stdout.split(":")[-1].split("-")[0]
