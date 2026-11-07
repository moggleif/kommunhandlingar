"""Krav: K6 och K41 i docs/02-KRAV.md, ADR-0005 och ADR-0064.
Test: tests/test_konvertering.py och tests/test_hogkant.py.

En sida som ska läsas med OCR renderas med pypdfium2 i 300 dpi, i gråskala,
och läses av Tesseract med svensk modell. Säkerheten är medelvärdet av
Tesseracts säkerhet för de ord den känt igen; under tröskeln, eller utan
ord, är sidan `ej-konverterad`. Det är den också när Tesseract fallerar
eller inte blir klar på fem minuter. Saknas Tesseract eller modellen
stoppas körningen innan något dokument läses (`kontrollera`).

Ord på högkant, som en stämpel i marginalen, målas vita och sidan läses
om, och de skrivs sist på sidan (K41, ADR-0064).

Två fel som Tesseract gör i protokollen rättas i texten (K34, ADR-0055):
`§` intill en siffra läses som `$`, och en innehållsförtecknings
punktutfyllnad blir punkter och bokstäver fram till sidnumret.
"""

import csv
import os
import re
import subprocess
import sys
import tempfile
from functools import cache
from importlib.metadata import version
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

from kommunhandlingar.fel import Konfigurationsfel
from kommunhandlingar.konvertering import hogkant

DPI = 300
SPRAK = "swe"
TROSKEL = 70
TIDSGRANS = 300
PARAGRAF = re.compile(r"\$+(?= ?\d)|(?<=\d )\$+|(?<=\d)\$+")
# Punkterna kan börja med brus utan mellanslag (`..ssss.....`); efter dem
# står bara brus fram till sidnumret, på samma rad.
UTFYLLNAD = re.compile(
    r"[ \t]*(?:\.\.[a-zåäö.]*?)?\.{4}[a-zåäö., >-]*?(\d+)[ \t]*$", re.MULTILINE
)


def las(rendering: pdfium.PdfPage) -> str | None:
    """Sidans OCR-text, eller None när den inte når tröskeln. Ord på
    högkant målas vita och sidan läses om; de skrivs sist (ADR-0064).
    Når omläsningen inte tröskeln gäller den första läsningen."""
    bild = rendering.render(scale=DPI / 72, grayscale=True).to_pil()
    forsta = las_bild(bild)
    if forsta is None or not over_troskeln(forsta[0]):
        return None
    stamplar = hogkant.ocr_ord(forsta[0])
    if stamplar:
        hogkant.mala_vitt(bild, stamplar)
        andra = las_bild(bild)
        if andra is not None and over_troskeln(andra[0]):
            return hogkant.sist(rensa(andra[1].strip()), hogkant.ocr_rader(stamplar))
    return rensa(forsta[1].strip())


def las_bild(bild: Image.Image) -> tuple[str, str] | None:
    """Tesseracts TSV och text för bilden, eller None när Tesseract fallerar."""
    with tempfile.TemporaryDirectory() as katalog:
        fil, ut = Path(katalog) / "sida.png", Path(katalog) / "ut"
        bild.save(fil)
        if not tesseract(fil, ut):
            return None
        tsv, txt = (
            ut.with_suffix(s).read_text(encoding="utf-8") for s in (".tsv", ".txt")
        )
        return tsv, txt


def over_troskeln(tsv: str) -> bool:
    sakerhet = medelsakerhet(tsv)
    return sakerhet is not None and sakerhet >= TROSKEL


def rensa(text: str) -> str:
    text = PARAGRAF.sub(lambda m: "§" * len(m[0]), text)
    return UTFYLLNAD.sub(r" .... \1", text)


def tesseract(bild: Path, ut: Path) -> bool:
    try:
        subprocess.run(
            ["tesseract", bild, ut, "-l", SPRAK, "--dpi", str(DPI), "txt", "tsv"],
            check=True,
            capture_output=True,
            timeout=TIDSGRANS,
            env=os.environ | {"OMP_THREAD_LIMIT": "1"},
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as fel:
        print(f"Tesseract: {fel}", file=sys.stderr)
        return False
    return True


def kontrollera() -> None:
    try:
        svar = subprocess.run(
            ["tesseract", "--list-langs"], capture_output=True, text=True
        )
    except FileNotFoundError as fel:
        raise Konfigurationsfel("Tesseract saknas (OCR, ADR-0005)") from fel
    if SPRAK not in svar.stdout.split():
        raise Konfigurationsfel(f"Tesseract saknar språkmodellen {SPRAK!r}")


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
    tesseract = svar.stdout.split()[1]
    return [
        f"pypdfium2 {version('pypdfium2')}",
        f"tesseract {tesseract} {SPRAK} {modellversion()}",
    ]


def modellversion() -> str:
    """Paketversionen av språkmodellen, utan epok och revision (1:4.1.0-2 → 4.1.0)."""
    try:
        svar = subprocess.run(
            ["dpkg-query", "-W", "-f=${Version}", f"tesseract-ocr-{SPRAK}"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:  # inte Debian eller Ubuntu
        return "okänd"
    if svar.returncode != 0:
        return "okänd"
    return svar.stdout.split(":")[-1].split("-")[0]
