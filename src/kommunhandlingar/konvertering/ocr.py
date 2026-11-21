"""Krav: K6, K41 och K73 i docs/02-KRAV.md, ADR-0005, ADR-0064 och ADR-0100.
Test: tests/test_konvertering.py och tests/test_hogkant.py.

En sida som ska läsas med OCR renderas med pypdfium2 i 300 dpi, i gråskala,
och läses av Tesseract med svensk modell. Säkerheten är medelvärdet av
Tesseracts säkerhet för de ord den känt igen; under tröskeln, eller utan
ord, ger läsningen ingen text men sin TSV, som de säkra raderna läses ur
(K73). Fallerar Tesseract eller blir den inte klar på fem minuter ger
läsningen ingenting. Saknas Tesseract eller modellen
stoppas körningen innan något dokument läses (`kontrollera`).

Ord på högkant, som en stämpel i marginalen, målas vita och sidan läses
om, och de skrivs sist på sidan (K41, ADR-0064). Läsningen ger också
rutorna kring de ord som lästs säkert, som bildytan räknas utan (K72,
ADR-0099).

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
from dataclasses import dataclass, field
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
SAKERT_ORD = 50
PARAGRAF = re.compile(r"\$+(?= ?\d)|(?<=\d )\$+|(?<=\d)\$+")
# Punkterna kan börja med brus utan mellanslag (`..ssss.....`); efter dem
# står bara brus fram till sidnumret, på samma rad.
UTFYLLNAD = re.compile(
    r"[ \t]*(?:\.\.[a-zåäö.]*?)?\.{4}[a-zåäö., >-]*?(\d+)[ \t]*$", re.MULTILINE
)


@dataclass(frozen=True)
class Lasning:
    text: str | None
    ord: list[tuple[int, int, int, int]] = field(default_factory=list)
    ordantal: int | None = None  # None: Tesseract fallerade
    tsv: str = ""


def rendera(rendering: pdfium.PdfPage) -> Image.Image:
    return rendering.render(scale=DPI / 72, grayscale=True).to_pil()


def las(bild: Image.Image) -> Lasning:
    """Bildens OCR-text, None när den inte når tröskeln, och rutorna kring
    de säkra orden. Ord på högkant målas vita och sidan läses om; de skrivs
    sist (ADR-0064). Når omläsningen inte tröskeln gäller den första."""
    forsta = las_bild(bild)
    if forsta is None:
        return Lasning(None)
    ord_, antal = sakra_ord(forsta[0]), len(ordrader(forsta[0]))
    if not over_troskeln(forsta[0]):
        return Lasning(None, ord_, antal, forsta[0])
    return Lasning(text_utan_stamplar(bild, forsta), ord_, antal)


def text_utan_stamplar(bild: Image.Image, forsta: tuple[str, str]) -> str:
    stamplar = hogkant.ocr_ord(forsta[0])
    if stamplar:
        bild = bild.copy()
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
    for modell in (SPRAK, "osd"):
        if modell not in svar.stdout.split():
            raise Konfigurationsfel(f"Tesseract saknar modellen {modell!r}")


def medelsakerhet(tsv: str) -> float | None:
    varden = [float(r["conf"]) for r in ordrader(tsv)]
    return sum(varden) / len(varden) if varden else None


def sakra_ord(tsv: str) -> list[tuple[int, int, int, int]]:
    """Rutorna kring ord med minst två tecken och säkerhet minst 50."""
    return [
        (
            int(r["left"]),
            int(r["top"]),
            int(r["left"]) + int(r["width"]),
            int(r["top"]) + int(r["height"]),
        )
        for r in ordrader(tsv)
        if float(r["conf"]) >= SAKERT_ORD and len(r["text"].strip()) >= 2
    ]


def ordrader(tsv: str) -> list[dict[str, str]]:
    rader = csv.DictReader(tsv.splitlines(), delimiter="\t", quoting=csv.QUOTE_NONE)
    return [r for r in rader if r["text"].strip() and r["conf"] != "-1"]


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
