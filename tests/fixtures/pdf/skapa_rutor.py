"""Krav: K61 och ADR-0087. Skapar `rutor.pdf` för tests/test_rutkanter.py.

Körs för hand med reportlab, som inte är projektets beroende:
`python tests/fixtures/pdf/skapa_rutor.py`.

1. En tabell som Word ritar den: en vit ruta per cell, streck runt om och
   mellan raderna, men inget streck mellan Uppdrag och Kommentar.
2. En tabell med streck överallt, där en rad har en färgad bakgrund över
   nästan hela bredden, 4 punkter innanför strecken.
3. Två färgade rutor med text som inte möts.
"""

from itertools import pairwise
from pathlib import Path

from reportlab.pdfgen.canvas import Canvas

HAR = Path(__file__).parent
X = [60, 160, 260, 500]
Y = [780, 760, 700, 640]
BLA = (0.64, 0.85, 0.91)
VIT = (1, 1, 1)
RADER = [
    ("Mål", "Uppdrag", "Kommentar"),
    ("Digital vardag", "Stärka digital", "Uppfylls"),
    ("Hållbarhet", "Minska plast", "Uppfylls inte"),
]


def cellrutor(c: Canvas) -> None:
    c.setStrokeColorRGB(1, 1, 1)
    for i, (topp, botten) in enumerate(pairwise(Y)):
        c.setFillColorRGB(*(BLA if i == 0 else VIT))
        for vanster, hoger in pairwise(X):
            c.rect(vanster, botten, hoger - vanster, topp - botten, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    c.setStrokeColorRGB(0, 0, 0)


def text(c: Canvas) -> None:
    for (topp, _), rad in zip(pairwise(Y), RADER, strict=True):
        for vanster, cell in zip(X[:-1], rad, strict=True):
            c.drawString(vanster + 5, topp - 14, cell)


def word_tabell(c: Canvas) -> None:
    cellrutor(c)
    for y in Y:
        c.line(X[0], y, X[-1], y)
    for x in X[:2] + X[-1:]:
        c.line(x, Y[0], x, Y[-1])
    text(c)


def farjad_rad(c: Canvas) -> None:
    c.setFillColorRGB(0.98, 0.85, 0.88)
    c.rect(X[0] + 4, Y[2] + 4, X[-1] - X[0] - 8, Y[1] - Y[2] - 8, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    for y in Y:
        c.line(X[0], y, X[-1], y)
    for x in X:
        c.line(x, Y[0], x, Y[-1])
    text(c)


def rutor_isar(c: Canvas) -> None:
    c.setFillColorRGB(*BLA)
    c.rect(60, 700, 150, 60, stroke=0, fill=1)
    c.rect(230, 700, 150, 60, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(65, 740, "Vänster ruta")
    c.drawString(235, 740, "Höger ruta")


def main() -> None:
    c = Canvas(str(HAR / "rutor.pdf"), pagesize=(595, 842))
    for sida in (word_tabell, farjad_rad, rutor_isar):
        sida(c)
        c.showPage()
    c.save()


if __name__ == "__main__":
    main()
