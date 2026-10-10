"""Krav: K19, ADR-0024. Skapar `skarvar.pdf` för tests/test_skarvar.py.

Körs för hand med reportlab, som inte är projektets beroende:
`python tests/fixtures/pdf/skapa_skarvar.py`. Varje sida har sidhuvud och
sidfot med sidnumret.

1. En rubrik och en tabell som fortsätter på nästa sida.
2. Fortsättningen, med rubriken upprepad.
3. Fortsättningen utan rubrik, en rubrik i texten och en ny tabell.
4. En rubrik ovanför en tabell med samma kolumner: ingen fortsättning.
5. Samma rubrik på samma höjd med en annan siffra: ingen fortsättning.
   Under tabellen står ett datum.
6. En tabell direkt under sidhuvudet, men datumet på sidan 5 skiljer.
7. Samma yttermått men andra kolumner: ingen fortsättning.
"""

from collections.abc import Iterator
from pathlib import Path

from reportlab.pdfgen.canvas import Canvas

HAR = Path(__file__).parent
B, H = 595, 842
SIDOR = 7
KOLUMNER = [60, 120, 400, 535]
RUBRIK = ("Nr", "Ärende", "Delegat")


def tabell(c: Canvas, topp: float, rader: list[tuple], x: list[float]) -> float:
    botten = topp - 20 * len(rader)
    for xi in x:
        c.line(xi, topp, xi, botten)
    for i, rad in enumerate(rader):
        y = topp - 20 * i
        c.line(x[0], y, x[-1], y)
        for xi, cell in zip(x[:-1], rad, strict=True):
            c.drawString(xi + 5, y - 14, cell)
    c.line(x[0], botten, x[-1], botten)
    return botten


def arenden(avsnitt: int, antal: int) -> list[tuple]:
    return [
        (f"{avsnitt}.{i}", f"Ärende {avsnitt}.{i}", "FC") for i in range(1, antal + 1)
    ]


def ram(c: Canvas, sida: int) -> None:
    c.drawString(60, 815, f"Exempelby kommun {sida}({SIDOR})")
    c.drawString(270, 30, f"Sida {sida} av {SIDOR}")


def sidor(c: Canvas) -> Iterator[None]:
    c.drawString(60, 780, "Delegationsordning")
    tabell(c, 760, [RUBRIK, *arenden(1, 30)], KOLUMNER)
    yield
    tabell(c, 800, [RUBRIK, *arenden(2, 5)], KOLUMNER)
    yield
    botten = tabell(c, 800, arenden(3, 3), KOLUMNER)
    c.drawString(60, botten - 30, "Avsnitt 4 Ekonomi")
    tabell(c, botten - 50, [RUBRIK, *arenden(4, 2)], KOLUMNER)
    yield
    c.drawString(60, 780, "Avsnitt 5 Ekonomi")
    tabell(c, 760, [RUBRIK, *arenden(5, 2)], KOLUMNER)
    yield
    c.drawString(60, 780, "Avsnitt 6 Ekonomi")
    botten = tabell(c, 760, [RUBRIK, *arenden(6, 2)], KOLUMNER)
    c.drawString(60, botten - 20, "2026-10-10")
    yield
    tabell(c, 800, [RUBRIK, *arenden(7, 2)], KOLUMNER)
    yield
    tabell(c, 800, [RUBRIK, *arenden(8, 2)], [60, 300, 450, 535])
    yield


def skapa() -> None:
    c = Canvas(str(HAR / "skarvar.pdf"), pagesize=(B, H), invariant=True)
    for nr, _ in enumerate(sidor(c), 1):
        ram(c, nr)
        c.showPage()
    c.save()


if __name__ == "__main__":
    skapa()
