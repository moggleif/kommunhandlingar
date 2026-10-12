"""Krav: K5, ADR-0034. Kod: src/kommunhandlingar/konvertering/avskurna.py.

Orden är påhittade med koordinater i punkter och teckenhöjd 10. Tabellens
ruta går från x 100 till 300 och från y 100 till 160.
"""

import unittest
from pathlib import Path

import pdfplumber

from kommunhandlingar.konvertering.avskurna import avskuren
from kommunhandlingar.konvertering.las_sida import textsida

HOJD = 10
RUTA = (100, 100, 300, 160)
FACIT = Path(__file__).parent / "fixtures" / "facit"


def ord_(text: str, x0: float, top: float = 120) -> dict:
    bredd = 6 * len(text)
    return {"text": text, "x0": x0, "x1": x0 + bredd, "top": top, "bottom": top + HOJD}


def mening(x0: float, *orden: str) -> list[dict]:
    """Orden med ett vanligt mellanslag, 2 punkter, emellan."""
    ut = []
    for text in orden:
        ut.append(ord_(text, x0))
        x0 = ut[-1]["x1"] + 2
    return ut


class TestAvskuren(unittest.TestCase):
    def test_tal_till_hoger_pa_samma_hojd(self):
        self.assertTrue(avskuren(RUTA, [ord_("8", 320)], [RUTA]))

    def test_tal_till_vanster_pa_samma_hojd(self):
        self.assertTrue(avskuren(RUTA, [ord_("Starka", 20), ord_("18", 80)], [RUTA]))

    def test_tal_ovanfor_eller_under_raknas_inte(self):
        ovanfor, under = ord_("8", 320, 80), ord_("8", 320, 170)
        self.assertFalse(avskuren(RUTA, [ovanfor, under], [RUTA]))

    def test_tal_i_en_mening_raknas_inte(self):
        ord_i_meningen = mening(320, "För", "typ", "3", "begäran")
        self.assertFalse(avskuren(RUTA, ord_i_meningen, [RUTA]))

    def test_artal_raknas_inte(self):
        self.assertFalse(avskuren(RUTA, [ord_("2025", 320)], [RUTA]))

    def test_etiketter_utanfor_raknas_inte(self):
        self.assertFalse(avskuren(RUTA, [ord_("Starka", 20)], [RUTA]))

    def test_tal_i_en_annan_tabell_raknas_inte(self):
        bredvid = (310, 100, 400, 160)
        self.assertFalse(avskuren(RUTA, [ord_("8", 320)], [RUTA, bredvid]))


class TestSidan(unittest.TestCase):
    def test_tabell_som_linjerna_bara_ramar_in_till_en_del_marker_sidan(self):
        """Tabellen över stråken i trafikförsörjningsprogrammet (#90)."""
        pdf_ = FACIT / "trafikforsorjningsprogram" / "utdrag.pdf"
        with pdfplumber.open(pdf_) as pdf:
            sida = textsida(pdf.pages[0])
        self.assertEqual(sida.kvalitet, "tabell-osaker")
        self.assertNotIn([["24", "12"], ["18", "12"], ["54", "36"]], sida.tabeller)


if __name__ == "__main__":
    unittest.main()
