"""Krav: K41, ADR-0064. Skapar `hogkant.pdf` för tests/test_hogkant.py.

Körs för hand med reportlab och Pillow, som inte är projektets beroenden:
`python tests/fixtures/pdf/skapa_hogkant.py`.

1. Ett stycke i textlagret och ett diarienummer på högkant i högra
   marginalen, i höjd med styckets mitt.
2. Samma sida inskannad, som bild i 150 dpi utan textlager.
"""

from pathlib import Path

import reportlab
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

HAR = Path(__file__).parent
B, H = 595, 842
STAMPEL = "2021-103216-0024"
STYCKE = [
    "Ledningarna kommer att passera ett antal alléer som omfattas av",
    "det generella biotopskyddet. Schaktning kan ske på tillräckligt",
    "avstånd från trädstammarna så att de inte skadas. En åkerholme",
    "kommer att rundas och ett dike kommer att korsas med styrd",
    "borrning. Om schaktning genom diket behövs ska den som bygger",
    "ansöka om dispens. Inventeringen hittade två naturvärdesobjekt",
    "längs med sträckningen, och påverkan på dem bedöms bli liten.",
]


def textlager(c: Canvas) -> None:
    c.setFont("Helvetica", 11)
    for i, rad in enumerate(STYCKE):
        c.drawString(60, 700 - 13 * i, rad)
    c.saveState()
    c.translate(560, 580)
    c.rotate(90)
    c.drawString(0, 0, STAMPEL)
    c.restoreState()


def inskannad(c: Canvas) -> None:
    bild = Image.new("L", (1240, 1754), 255)
    rita = ImageDraw.Draw(bild)
    typsnitt = ImageFont.truetype(
        str(Path(reportlab.__file__).parent / "fonts" / "Vera.ttf"), 24
    )
    for i, rad in enumerate(STYCKE):
        rita.text((120, 300 + 36 * i), rad, fill=0, font=typsnitt)
    stampel = Image.new("L", (420, 40), 255)
    ImageDraw.Draw(stampel).text((0, 0), STAMPEL, fill=0, font=typsnitt)
    bild.paste(stampel.rotate(90, expand=True), (1150, 200))
    c.drawImage(ImageReader(bild.convert("1")), 0, 0, B, H)


def main() -> None:
    c = Canvas(str(HAR / "hogkant.pdf"), pagesize=(B, H), invariant=1)
    for sida in (textlager, inskannad):
        sida(c)
        c.showPage()
    c.save()


if __name__ == "__main__":
    main()
