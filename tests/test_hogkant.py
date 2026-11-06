"""Krav: K41, ADR-0064. Kod: src/kommunhandlingar/konvertering/hogkant.py
och ocr.py.

Sidorna i hogkant.pdf beskrivs i tests/fixtures/pdf/skapa_hogkant.py. Orden
i TSV:n är påhittade efter en skannad sida med en stämpel i marginalen.
"""

import unittest
from pathlib import Path
from types import SimpleNamespace

import pdfplumber
import pypdfium2 as pdfium
from PIL import Image

from kommunhandlingar.konvertering import hogkant
from kommunhandlingar.konvertering.las_sida import las_sida, textsida

PDF = Path(__file__).parent / "fixtures" / "pdf" / "hogkant.pdf"
STAMPEL = "2021-103216-0024"
KOLUMNER = (
    "page_num\tblock_num\tpar_num\tline_num\tleft\ttop\twidth\theight\tconf\ttext"
)


def tsv(*ord_: tuple) -> str:
    return "\n".join([KOLUMNER, *("\t".join(map(str, (1, *o))) for o in ord_)])


def tecken(text: str, x0: float, top: float, uppat: bool = True) -> dict:
    b = 9 if uppat else -9
    return {
        "text": text,
        "x0": x0,
        "x1": x0 + 9,
        "top": top,
        "bottom": top + 6,
        "upright": False,
        "matrix": (0, b, -b, 0, 0, 0),
    }


class TestTextlagret(unittest.TestCase):
    def test_vriden_moturs_lases_uppat(self):
        tecknen = [tecken(t, 40, 80 - 6 * i) for i, t in enumerate("OKTOBER")]
        sida = SimpleNamespace(chars=tecknen[::-1])
        self.assertEqual(hogkant.textlagret(sida), ["OKTOBER"])

    def test_vriden_medurs_lases_nedat(self):
        tecknen = [tecken(t, 40, 40 + 6 * i, uppat=False) for i, t in enumerate("DNR")]
        sida = SimpleNamespace(chars=tecknen)
        self.assertEqual(hogkant.textlagret(sida), ["DNR"])

    def test_rader_fran_vanster(self):
        tecknen = [tecken("B", 60, 50), tecken("A", 40, 50)]
        sida = SimpleNamespace(chars=tecknen)
        self.assertEqual(hogkant.textlagret(sida), ["A", "B"])

    def test_ord_utan_mellanslag_halls_isar(self):
        ord_ = [tecken(t, 40, 200 - 6 * i) for i, t in enumerate("Dnr")]
        ord_ += [tecken(t, 40, 180 - 6 * i) for i, t in enumerate("KS")]
        self.assertEqual(hogkant.textlagret(SimpleNamespace(chars=ord_)), ["Dnr KS"])

    def test_tva_stamplar_i_samma_marginal(self):
        nedre = [tecken(t, 30, 700 - 6 * i) for i, t in enumerate("NEDRE")]
        ovre = [tecken(t, 30, 100 - 6 * i) for i, t in enumerate("OVRE")]
        sida = SimpleNamespace(chars=nedre + ovre)
        self.assertEqual(hogkant.textlagret(sida), ["NEDRE", "OVRE"])

    def test_medurs_lases_fran_hoger(self):
        ett = [tecken(t, 60, 40 + 6 * i, uppat=False) for i, t in enumerate("ETT")]
        tva = [tecken(t, 40, 40 + 6 * i, uppat=False) for i, t in enumerate("TVA")]
        sida = SimpleNamespace(chars=tva + ett)
        self.assertEqual(hogkant.textlagret(sida), ["ETT", "TVA"])


class TestOcr(unittest.TestCase):
    def test_ord_pa_hogkant_kanns_igen(self):
        ord_ = hogkant.ocr_ord(
            tsv(
                (1, 1, 1, 450, 900, 1400, 40, 95, "Ledningarna"),
                (2, 1, 1, 2250, 480, 38, 344, 94, "2023-01-02"),
                (3, 1, 1, 2250, 1016, 39, 559, 90, STAMPEL),
                (4, 1, 1, 100, 100, 20, 60, 90, "I"),
            )
        )
        self.assertEqual([o["text"] for o in ord_], ["2023-01-02", STAMPEL])
        self.assertEqual(hogkant.ocr_rader(ord_), ["2023-01-02", STAMPEL])

    def test_korta_ord_pa_samma_rad_som_stampeln_kommer_med(self):
        ord_ = hogkant.ocr_ord(
            tsv(
                (2, 1, 1, 2250, 300, 38, 60, 94, "Dnr"),
                (2, 1, 1, 2250, 380, 38, 300, 94, "2021/123"),
            )
        )
        self.assertEqual(hogkant.ocr_rader(ord_), ["Dnr 2021/123"])

    def test_malas_vita(self):
        bild = Image.new("L", (10, 10), 0)
        hogkant.mala_vitt(
            bild, [{"left": "2", "top": "2", "width": "3", "height": "6"}]
        )
        self.assertEqual(bild.getpixel((3, 5)), 255)
        self.assertEqual(bild.getpixel((7, 5)), 0)

    def test_inget_pa_hogkant_ger_texten_som_den_ar(self):
        self.assertEqual(hogkant.sist("Text", []), "Text")


class TestHogkantPdf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf = pdfplumber.open(PDF)
        cls.addClassCleanup(cls.pdf.close)

    def test_textlagret_skriver_stampeln_sist_i_lasriktningen(self):
        text = textsida(self.pdf.pages[0]).text
        self.assertTrue(text.endswith(f"bli liten.\n\n{STAMPEL}"))

    def test_hogkant_i_en_tabell_star_kvar_i_tabellen(self):
        sida = textsida(self.pdf.pages[2])
        self.assertEqual(sida.text, "")
        rubrik = sida.tabeller[0][0]
        self.assertEqual(rubrik[0], "Post")
        self.assertEqual(sorted(rubrik[1]), sorted("Belopp"))

    def test_skannad_sida_skriver_stampeln_sist(self):
        rendering = pdfium.PdfDocument(PDF)[1]
        sida = las_sida(self.pdf.pages[1], rendering)
        self.assertEqual(sida.kvalitet, "ocr")
        self.assertTrue(sida.text.endswith(f"bli liten.\n\n{STAMPEL}"))
        self.assertEqual(sida.text.count(STAMPEL), 1)


if __name__ == "__main__":
    unittest.main()
