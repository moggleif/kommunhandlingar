"""Krav: K72 i docs/02-KRAV.md, ADR-0099. Testar
src/kommunhandlingar/konvertering/skannad.py och riktning.py med ritade
sidor som läses av Tesseract, och maskningen med en läsning som byts ut."""

import io
import random
import unittest
from unittest import mock

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont

from kommunhandlingar.konvertering import ocr, riktning, skannad

B, H = 1240, 1754  # A4 i 150 dpi
# Utan å, ä och ö: Pillows inbyggda typsnitt saknar dem.
RADER = [
    "Kommunstyrelsen beslutar att anta planen",
    "vid stationen i enlighet med det",
    "underlag som namnden tog fram i maj.",
    "Beslutet galler till och med 2030.",
]


def text(bild: Image.Image, antal: int = 12) -> None:
    typsnitt = ImageFont.load_default(size=40)
    rita = ImageDraw.Draw(bild)
    for i in range(antal):
        rita.text((120, 120 + 70 * i), RADER[i % 4], fill=0, font=typsnitt)


def karta(bild: Image.Image, ruta: tuple[int, int, int, int]) -> None:
    """Färgade ytor med små etiketter i alla riktningar, som en karta."""
    slump, (x0, y0, x1, y1) = random.Random(5), ruta
    rita, liten = ImageDraw.Draw(bild), ImageFont.load_default(size=16)
    rita.rectangle(ruta, fill=(120, 180, 110))
    for _ in range(80):
        x, y, r = slump.randint(x0, x1), slump.randint(y0, y1), slump.randint(10, 60)
        farg = (slump.randint(150, 250), 150, 60)
        rita.ellipse((x - r, y - r, x + r, y + r), fill=farg)
    for _ in range(300):
        ord_ = "".join(slump.choice("abcdefghijk0123456789") for _ in range(5))
        etikett = Image.new("RGBA", (120, 24))
        ImageDraw.Draw(etikett).text((0, 0), ord_, fill=(30, 30, 30), font=liten)
        etikett = etikett.rotate(slump.randint(-60, 60), expand=True)
        plats = (slump.randint(x0, x1 - 120), slump.randint(y0, y1 - 120))
        bild.paste(etikett, plats, etikett)


def sida(bild: Image.Image) -> pdfium.PdfPage:
    pdf = io.BytesIO()
    bild.save(pdf, "PDF", resolution=150)
    return pdfium.PdfDocument(pdf.getvalue())[0]


def vit() -> Image.Image:
    return Image.new("RGB", (B, H), "white")


class TestSkannad(unittest.TestCase):
    def test_textsida_lases_som_forut(self):
        bild = vit()
        text(bild)
        resultat = skannad.las(sida(bild))
        self.assertEqual((resultat.kvalitet, resultat.figur), ("ocr", False))
        self.assertIn("underlag som namnden tog fram", resultat.text)

    def test_karta_over_hela_sidan_blir_bild(self):
        bild = vit()
        karta(bild, (0, 0, B, H))
        self.assertEqual(skannad.las(sida(bild)), skannad.Skannad("bild", figur=True))

    def test_text_med_bild_star_i_figurer(self):
        bild = vit()
        text(bild, 4)
        karta(bild, (60, 500, B - 60, H - 60))
        resultat = skannad.las(sida(bild))
        self.assertEqual((resultat.kvalitet, resultat.figur), ("ocr", True))
        self.assertIn("Kommunstyrelsen beslutar", resultat.text)

    def test_liggande_sida_vands_och_lases(self):
        bild = vit()
        text(bild)
        resultat = skannad.las(sida(bild.rotate(90, expand=True)))
        self.assertEqual(resultat.kvalitet, "ocr")
        self.assertIn("underlag som namnden tog fram", resultat.text)

    def test_fargad_baksida_med_liten_logga_blir_tom(self):
        bild = Image.new("RGB", (B, H), (225, 238, 246))
        ImageDraw.Draw(bild).ellipse((100, 100, 160, 160), fill=(20, 60, 120))
        self.assertEqual(skannad.las(sida(bild)), skannad.Skannad("tom"))

    def test_bildytan_maskas_nar_sidan_inte_nar_troskeln(self):
        """Läsningen byts ut: bara den med kartan vit når tröskeln."""
        bild = vit()
        text(bild, 4)
        karta(bild, (60, 500, B - 60, H - 60))

        def las(gra: Image.Image) -> ocr.Lasning:
            vitt = gra.getpixel((gra.width // 2, gra.height * 3 // 4)) == 255
            return ocr.Lasning("Kommunstyrelsen" if vitt else None)

        with mock.patch.object(ocr, "las", side_effect=las):
            resultat = skannad.las(sida(bild))
        self.assertEqual(resultat, skannad.Skannad("ocr", "Kommunstyrelsen", True))


class TestRiktning(unittest.TestCase):
    def test_saker_riktning(self):
        svar = "Rotate: 270\nOrientation confidence: 12.5\n"
        with mock.patch.object(riktning, "detektera", return_value=svar):
            self.assertEqual(riktning.grader(Image.new("L", (10, 10))), 270)

    def test_osaker_eller_ingen_riktning_ger_noll(self):
        for svar in ("Rotate: 90\nOrientation confidence: 1.2\n", ""):
            with mock.patch.object(riktning, "detektera", return_value=svar):
                self.assertEqual(riktning.grader(Image.new("L", (10, 10))), 0)

    def test_sida_utan_text_har_ingen_riktning(self):
        self.assertEqual(riktning.grader(Image.new("L", (800, 1000), 255)), 0)
