"""Krav: K5 och K6, ADR-0005. Skapar PDF-fixturerna för tests/test_konvertering.py.

Körs för hand med reportlab, pypdf och Pillow, som inte är projektets
beroenden: `python tests/fixtures/pdf/skapa.py`. Varje sida i `sidor.pdf`
är ett fall ur reglerna i docs/03-ARKITEKTUR.md#konvertering-och-kvalitet.
"""

import random
from pathlib import Path

import reportlab
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

HAR = Path(__file__).parent
B, H = 595, 842


def brus() -> ImageReader:
    slump = random.Random(1)
    bild = Image.new("L", (60, 85))
    bild.putdata([slump.randint(0, 255) for _ in range(60 * 85)])
    return ImageReader(bild)


def text(c: Canvas, rader: list[str], y: float = 780) -> None:
    for rad in rader:
        c.drawString(60, y, rad)
        y -= 16


def textsida(c: Canvas) -> None:
    text(c, ["Protokoll 2026-08-11", "Dnr KS 2023-00686", "Paragraf 12 beslutades."])
    c.line(60, 700, 300, 700)  # ett ensamt streck är ingen tabell


def rutnat(c: Canvas, x: list[float], y: list[float]) -> None:
    for xi in x:
        c.line(xi, y[0], xi, y[-1])
    for yi in y:
        c.line(x[0], yi, x[-1], yi)


def linjetabell(c: Canvas) -> None:
    c.setFillGray(0.85)
    c.rect(60, 700, 300, 20, stroke=0, fill=1)
    c.setFillGray(0)
    rutnat(c, [60, 210, 360], [740, 720, 700, 680])
    c.drawString(65, 726, "Post")
    c.drawString(215, 726, "2027")
    c.drawString(65, 706, "Intäkter")
    c.drawString(215, 706, "4 078")
    c.drawString(65, 686, "Kostnader")
    c.drawString(215, 686, "-1 845")


def olinjerad(c: Canvas) -> None:
    for i, (namn, a, b) in enumerate(
        [
            ("Intäkter", "4 078", "4 054"),
            ("Kostnader", "-1 845", "-2 001"),
            ("Netto", "2 233", "2 053"),
        ]
    ):
        y = 760 - 20 * i
        c.drawString(60, y, namn)
        c.drawRightString(260, y, a)
        c.drawRightString(360, y, b)
        c.line(60, y - 5, 360, y - 5)


def olinjerad_med_huvud(c: Canvas) -> None:
    c.drawString(60, 780, "Driftbudget")
    rader = [
        ("Belopp, tkr", "Budget 2027", "Plan 2028"),
        ("Intäkter", "4 078", "4 054"),
        ("Kostnader", "-1 845", "-2 001"),
        ("Ombudget", "500", ""),
        ("Avgifter", "-", "120"),
        ("Netto", "2 233", "2 053"),
    ]
    for i, (namn, a, b) in enumerate(rader):
        y = 760 - 20 * i
        c.drawString(60, y, namn)
        c.drawRightString(260, y, a)
        c.drawRightString(360, y, b)


def ej_i_linje(c: Canvas) -> None:
    for i, (namn, a, b) in enumerate(
        [
            ("Intäkter", "4 078", "12"),
            ("Kostnader", "-1 845", "3 001"),
            ("Netto", "7", "45"),
        ]
    ):
        y = 760 - 20 * i
        c.drawString(60, y, namn)
        c.drawString(200, y, a)
        c.drawString(300, y, b)


def linjer_med_tva_tal_i_en_cell(c: Canvas) -> None:
    rutnat(c, [60, 210, 310, 410], [775, 755, 735, 695])
    for i, (namn, a, b) in enumerate(
        [
            ("Post", "2026", "2027"),
            ("Intäkter", "4 078", "4 054"),
            ("Kostnader", "-1 845", "-2 001"),
            ("Netto", "2 233", "2 053"),
        ]
    ):
        y = 760 - 20 * i
        c.drawString(65, y, namn)
        c.drawRightString(305, y, a)
        c.drawRightString(405, y, b)


def skanning(c: Canvas, synligt: str = "", osynligt: str = "") -> None:
    c.drawImage(brus(), 0, 0, B, H)
    if synligt:
        text(c, [synligt[i : i + 60] for i in range(0, len(synligt), 60)], 400)
    if osynligt:
        objekt = c.beginText(60, 300)
        objekt.setTextRenderMode(3)
        objekt.textLine(osynligt)
        c.drawText(objekt)


def inskannad_text(c: Canvas) -> None:
    """En inskannad blankett: text som bild i 150 dpi, utan textlager."""
    bild = Image.new("L", (1240, 1754), 255)
    rita = ImageDraw.Draw(bild)
    typsnitt = ImageFont.truetype(
        str(Path(reportlab.__file__).parent / "fonts" / "Vera.ttf"), 32
    )
    for i, rad in enumerate(BLANKETT):
        rita.text((120, 150 + 60 * i), rad, fill=0, font=typsnitt)
    c.drawImage(ImageReader(bild.convert("1")), 0, 0, B, H)


BLANKETT = [
    "Ansökan om partistöd",
    "Partiets namn: Exempelpartiet",
    "Antal mandat i fullmäktige: 4",
    "Kontaktperson och telefonnummer",
    "Redovisningen bifogas enligt beslut",
    "i kommunfullmäktige.",
]


def kurvor(c: Canvas) -> None:
    sokvag = c.beginPath()
    sokvag.moveTo(60, 600)
    sokvag.curveTo(200, 800, 300, 400, 500, 600)
    sokvag.close()
    c.drawPath(sokvag, stroke=0, fill=1)


SIDOR = [
    textsida,
    linjetabell,
    olinjerad,
    lambda c: None,
    skanning,
    lambda c: skanning(c, osynligt="Tidigare OCR-lager " * 10),
    lambda c: skanning(c, synligt="Dnr 2024-001"),
    lambda c: skanning(c, synligt="Omslag med en lång rubrik och mer text " * 3),
    kurvor,
    lambda c: c.line(60, 400, 500, 400),
    inskannad_text,
    olinjerad_med_huvud,
    ej_i_linje,
    linjer_med_tva_tal_i_en_cell,
]


def skapa() -> None:
    c = Canvas(str(HAR / "sidor.pdf"), pagesize=(B, H))
    for sida in SIDOR:
        sida(c)
        c.showPage()
    c.save()
    las = PdfReader(HAR / "sidor.pdf")
    for namn, anvandare in (("krypterad.pdf", "hemligt"), ("begransad.pdf", "")):
        skriv = PdfWriter(clone_from=las)
        skriv.encrypt(anvandare, owner_password="agare")
        skriv.write(HAR / namn)
    (HAR / "trasig.pdf").write_bytes((HAR / "sidor.pdf").read_bytes()[:400])
    (HAR / "inte.pdf").write_text("<html>Inte en PDF</html>\n")


if __name__ == "__main__":
    skapa()
