"""Krav: K4, ADR-0036. Kod: src/kommunhandlingar/konvertering/mellanslag.py."""

import unittest
from pathlib import Path

import pdfplumber

from kommunhandlingar.konvertering.las_sida import textsida
from kommunhandlingar.konvertering.mellanslag import inne_i

FACIT = Path(__file__).parent / "fixtures" / "facit"


def tecken(text: str, x0: float, x1: float) -> dict:
    return {"text": text, "x0": x0, "x1": x1, "top": 100}


FYRA = tecken("4", 307.0, 310.8)


class TestInneI(unittest.TestCase):
    def test_mellanslag_som_borjar_i_siffran(self):
        self.assertTrue(inne_i(tecken(" ", 307.0, 308.9), [FYRA]))

    def test_mellanslag_som_borjar_fore_siffran_star_kvar(self):
        self.assertFalse(inne_i(tecken(" ", 306.5, 308.4), [FYRA]))

    def test_mellanslag_som_bara_nuddar_siffran_star_kvar(self):
        self.assertFalse(inne_i(tecken(" ", 310.0, 312.0), [FYRA]))

    def test_annat_tecken_an_mellanslag_star_kvar(self):
        self.assertFalse(inne_i(tecken("7", 307.0, 308.9), [FYRA]))


class TestSidan(unittest.TestCase):
    def test_tal_ur_kalkylark_delas_inte(self):
        """Budgeten för räddningstjänsten (#91)."""
        with pdfplumber.open(
            FACIT / "raddningstjanst-budget-2027" / "utdrag.pdf"
        ) as pdf:
            text = textsida(pdf.pages[0]).text
        self.assertIn("476,7", text)
        self.assertNotIn("4 76,7", text)


if __name__ == "__main__":
    unittest.main()
