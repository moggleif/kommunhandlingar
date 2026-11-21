"""Skapar `kort.pdf` och `kort-begransad.pdf` för testerna av hämtningen.

Körs för hand med reportlab och pypdf, som inte är projektets beroenden:
`python tests/fixtures/pdf/skapa_kort.py`.

Fyra av sidorna i `sidor.pdf`, ritade på nytt och utan någon inskannad
sida, så att konverteringen går fort utan OCR: en textsida, en tabell,
en tabell vars tal inte står i linje och ett diagram. Det ger kvaliteten
`text-utan-tabeller`, som inte är `full` och därför konverteras om (K72),
och en figur.
`kort-begransad.pdf` har samma innehåll men en annan sha256.
"""

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas
from skapa import HAR, B, H, ej_i_linje, linjetabell, stapeldiagram, textsida


def main() -> None:
    c = Canvas(str(HAR / "kort.pdf"), pagesize=(B, H))
    for sida in (textsida, linjetabell, ej_i_linje, stapeldiagram):
        sida(c)
        c.showPage()
    c.save()
    skriv = PdfWriter(clone_from=PdfReader(HAR / "kort.pdf"))
    skriv.encrypt("", owner_password="agare")
    skriv.write(HAR / "kort-begransad.pdf")


if __name__ == "__main__":
    main()
