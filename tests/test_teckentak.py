"""Krav: K55, ADR-0079. Kod: src/kommunhandlingar/konvertering/dokument.py."""

import unittest
from pathlib import Path
from unittest import mock

import pypdfium2 as pdfium

from kommunhandlingar.konvertering import dokument
from kommunhandlingar.konvertering.dokument import konvertera, tecken

SIDOR = Path(__file__).parent / "fixtures" / "pdf" / "sidor.pdf"


def med_tak(tak: int) -> dokument.Resultat:
    with mock.patch.object(dokument, "TECKENTAK", tak):
        return konvertera(SIDOR)


def forsta_sidans_tecken() -> int:
    with pdfium.PdfDocument(SIDOR) as pdf:
        return tecken(pdf[0])


class TestTeckentaket(unittest.TestCase):
    def test_taket_ar_en_halv_miljon_tecken(self):
        self.assertEqual(dokument.TECKENTAK, 500_000)

    def test_sida_over_taket_blir_ej_konverterad_figur(self):
        resultat = med_tak(0)
        self.assertEqual(resultat.kvalitet_per_sida[0], "ej-konverterad")
        self.assertEqual(resultat.sidor[0].text, "")
        self.assertIn(1, resultat.figurer)
        self.assertIn(1, resultat.tal_obekraftade)
        self.assertEqual(resultat.kvalitet_per_sida[3], "tom")

    def test_sida_pa_taket_lases(self):
        resultat = med_tak(forsta_sidans_tecken())
        self.assertEqual(resultat.kvalitet_per_sida[0], "ok")
        self.assertIn("Paragraf 12", resultat.sidor[0].text)

    def test_ovriga_sidor_lases_som_vanligt(self):
        resultat = med_tak(forsta_sidans_tecken() - 1)
        self.assertEqual(resultat.kvalitet_per_sida[0], "ej-konverterad")
        self.assertEqual(resultat.kvalitet_per_sida[1], "ok")
        self.assertEqual(resultat.kvalitet, "delvis")
