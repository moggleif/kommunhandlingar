"""Krav: K6, ADR-0038. Kod: src/kommunhandlingar/konvertering/ordning.py.

Tecknen är påhittade efter sidorna i #119: datumet `2025-05-21` som ritats
ovanpå slutet av `stöd` i cellen till vänster.
"""

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pdfplumber

from kommunhandlingar.konvertering import las_sida
from kommunhandlingar.konvertering.las_sida import textsida
from kommunhandlingar.konvertering.ordning import i_oordning

PDF = Path(__file__).parent / "fixtures" / "pdf"


def tecken(text: str, x0: float, bredd: float = 5.6, upright: bool = True) -> dict:
    return {"text": text, "x0": x0, "x1": x0 + bredd, "top": 134, "upright": upright}


def sida(*tecken_: dict) -> SimpleNamespace:
    return SimpleNamespace(chars=list(tecken_))


STOD = [tecken("ö", 421.6), tecken("d", 427.2), tecken(" ", 432.8, 2.1)]


class TestOrdning(unittest.TestCase):
    def test_text_i_ordning(self):
        self.assertFalse(i_oordning(sida(*STOD, tecken("2", 434.8))))

    def test_text_ritad_ovanpa_annan_text(self):
        """Som i textlagret: en tvåa efter `stöd`, sedan datumet ovanpå."""
        datum = [tecken("2", 434.8), tecken("2", 425.8), tecken("0", 431.4)]
        self.assertTrue(i_oordning(sida(*STOD, *datum)))

    def test_grannar_som_overlappar_raknas_inte(self):
        """Kursiv stil: tecknens rutor är bredare än tecknen."""
        kursiv = [tecken("r", 139.9, 6.6), tecken("i", 143.3), tecken("g", 146.1)]
        self.assertFalse(i_oordning(sida(*kursiv)))

    def test_samma_tecken_tva_ganger_raknas_inte(self):
        """Fetstil som ritats två gånger, något förskjuten."""
        fet = [tecken("A", 100), tecken("B", 106), tecken("A", 100.3)]
        self.assertFalse(i_oordning(sida(*fet)))

    def test_roterad_text(self):
        self.assertTrue(i_oordning(sida(*STOD, tecken("N", 50, upright=False))))


class TestRader(unittest.TestCase):
    def test_kursiv_over_ett_mellanrum_raknas_inte(self):
        """Mellanslaget mellan grannarna räknas inte."""
        kursiv = [tecken("f", 100, 7), tecken(" ", 105, 2), tecken("a", 103)]
        self.assertFalse(i_oordning(sida(*kursiv)))

    def test_tecken_pa_olika_rader_overlappar_inte(self):
        under = dict(tecken("2", 425.8), top=148)
        self.assertFalse(i_oordning(sida(*STOD, tecken("0", 440), under)))


class TestSidan(unittest.TestCase):
    def test_sidan_i_oordning_far_obekraftade_tal(self):
        with pdfplumber.open(PDF / "sidor.pdf") as pdf:
            sida = pdf.pages[0]
            self.assertFalse(textsida(sida).tal_obekraftade)
            with patch.object(las_sida, "i_oordning", return_value=True):
                self.assertTrue(textsida(sida).tal_obekraftade)
