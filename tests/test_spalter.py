"""Krav: K41, ADR-0062. Kod: src/kommunhandlingar/konvertering/spalter.py.

Sidorna i spalter.pdf beskrivs i tests/fixtures/pdf/skapa_spalter.py.
Radstyckena är påhittade efter en månadsrapport med tre spalter.
"""

import unittest
from pathlib import Path

import pdfplumber

from kommunhandlingar.konvertering import spalter
from kommunhandlingar.konvertering.las_sida import textsida
from kommunhandlingar.konvertering.spalter import Radstycke, ordna

PDF = Path(__file__).parent / "fixtures" / "pdf" / "spalter.pdf"
LOPTEXT = "ord som bildar en rad med löptext i spalten"


def spalt(x0: float, rader: int, text: str = LOPTEXT) -> list[Radstycke]:
    return [
        Radstycke(x0, 100 + 12 * i, x0 + 150, 109 + 12 * i, text) for i in range(rader)
    ]


class TestOrdna(unittest.TestCase):
    def test_spalterna_fran_vanster(self):
        vanster, hoger = spalt(50, 8), spalt(220, 8)
        self.assertEqual(ordna(hoger + vanster), [vanster, hoger])

    def test_rubrik_over_hela_bredden_forst(self):
        rubrik = [Radstycke(50, 60, 370, 70, "En rubrik över båda spalterna")]
        vanster, hoger = spalt(50, 8), spalt(220, 8)
        self.assertEqual(ordna(vanster + hoger + rubrik), [rubrik, vanster, hoger])

    def test_en_spalt_ar_en_ruta(self):
        stycken = spalt(50, 8)
        self.assertEqual(ordna(stycken), [stycken])

    def test_korta_rader_bredvid_varandra_delas_inte(self):
        """Ett brevhuvud eller en ärendelista är ingen löptext."""
        vanster = spalt(50, 8, "Avdelningen")
        self.assertEqual(len(ordna(vanster + spalt(220, 8))), 1)

    def test_tal_bredvid_varandra_delas_inte(self):
        tal = spalt(220, 8, "1 200 300 400 500 600 700 800 900")
        self.assertEqual(len(ordna(spalt(50, 8) + tal)), 1)

    def test_farre_an_sex_rader_delas_inte(self):
        self.assertEqual(len(ordna(spalt(50, 5) + spalt(220, 5))), 1)


class TestSpalterPdf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf = pdfplumber.open(PDF)
        cls.addClassCleanup(cls.pdf.close)

    def test_meningen_fortsatter_i_nasta_spalt(self):
        text = textsida(self.pdf.pages[0]).text
        self.assertIn("i nästa rapport\n\ntill nämnden under hösten", text)

    def test_bildtexten_star_i_sin_spalt(self):
        text = textsida(self.pdf.pages[0]).text
        self.assertIn("vidtagits.\n\nBild: Elever på skolan\nAntalet elever", text)
        self.assertLess(text.index("Uppföljning"), text.index("Nämnden följer"))

    def test_sidor_utan_spalter_lases_som_forut(self):
        for sida in self.pdf.pages[1:]:
            with self.subTest(sida=sida.page_number):
                self.assertEqual(spalter.text(sida), sida.extract_text(layout=True))


if __name__ == "__main__":
    unittest.main()
