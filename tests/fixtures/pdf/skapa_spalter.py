"""Krav: K41, ADR-0062. Skapar `spalter.pdf` för tests/test_spalter.py.

Körs för hand med reportlab, som inte är projektets beroende:
`python tests/fixtures/pdf/skapa_spalter.py`.

1. En rubrik över hela bredden och två spalter med löptext. Meningen i
   slutet av vänster spalt fortsätter överst i höger spalt, och i vänster
   spalt står en bild med en bildtext mitt emellan två stycken.
2. En spalt med ett brevhuvud i två fält och tre talrader, som ska läsas
   som förut.
3. En ärendelista utan linjer med text i två kolumner på tre rader, som
   inte är löptext i spalter.
"""

from pathlib import Path

from reportlab.pdfgen.canvas import Canvas

HAR = Path(__file__).parent
B, H = 595, 842
RAD = 13
VANSTER = [
    "Nämnden följer upp verksamheten varje kvartal",
    "och redovisar resultatet för fullmäktige i",
    "en rapport som beskriver utvecklingen under",
    "perioden och de åtgärder som har vidtagits.",
]
VANSTER_EFTER = [
    "Antalet elever har ökat sedan förra året och",
    "fler har valt de yrkesinriktade programmen,",
    "vilket ställer krav på lokaler och lärare som",
    "förvaltningen ska redovisa i nästa rapport",
]
HOGER = [
    "till nämnden under hösten, tillsammans med",
    "en plan för hur behoven ska mötas och vad de",
    "kommer att kosta under de kommande åren när",
    "verksamheten fortsätter att växa i kommunen.",
    "Planen ska också beskriva hur samverkan med",
    "andra kommuner i regionen kan utvecklas och",
    "vilka utbildningar som kan erbjudas där.",
    "Nämnden beslutar om planen i december.",
]


def rader(c: Canvas, x: float, y: float, text: list[str]) -> float:
    for rad in text:
        c.drawString(x, y, rad)
        y -= RAD
    return y


def spalter(c: Canvas) -> None:
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 790, "Uppföljning av verksamheten")
    c.setFont("Helvetica", 10)
    y = rader(c, 50, 760, VANSTER)
    c.setFillGray(0.6)
    c.rect(50, y - 80, 200, 80, stroke=0, fill=1)
    c.setFillGray(0)
    c.drawString(50, y - 94, "Bild: Elever på skolan")
    rader(c, 50, y - 114, VANSTER_EFTER)
    rader(c, 310, 760, HOGER)
    c.drawString(290, 40, "3")


def talrader(c: Canvas) -> None:
    c.drawString(50, 790, "Förvaltningen för Exempel")
    c.drawString(400, 790, "Exempelby kommun")
    c.drawString(50, 776, "Avdelningen")
    c.drawString(400, 776, "123 45 Exempelby")
    for i, (post, belopp) in enumerate([("Intäkter", "1 200"), ("Kostnader", "-900")]):
        y = 740 - RAD * i
        c.drawString(50, y, post)
        c.drawRightString(300, y, belopp)
        c.drawRightString(400, y, f"{i + 3}00")
    c.drawString(50, 714, "Resultat")
    c.drawRightString(300, 714, "300")
    c.drawRightString(400, 714, "500")


def arendelista(c: Canvas) -> None:
    arenden = [
        ("1. Val av justerare för dagens sammanträde", "Nämnden väljer en justerare"),
        ("2. Information om verksamhetens ekonomi", "Nämnden noterar informationen"),
        ("3. Uppföljning av den interna kontrollen", "Nämnden godkänner uppföljningen"),
    ]
    for i, (arende, forslag) in enumerate(arenden):
        c.drawString(50, 780 - 20 * i, arende)
        c.drawString(330, 780 - 20 * i, forslag)


def main() -> None:
    c = Canvas(str(HAR / "spalter.pdf"), pagesize=(B, H), invariant=1)
    for sida in (spalter, talrader, arendelista):
        c.setFont("Helvetica", 10)
        sida(c)
        c.showPage()
    c.save()


if __name__ == "__main__":
    main()
