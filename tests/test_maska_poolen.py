"""Krav: K17, ADR-0022. Kod: src/kommunhandlingar/maska_poolen.py och
maskningen i src/kommunhandlingar/konvertering/las_sida.py.

Alla nummer här är påhittade.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from kommunhandlingar.konvertering import las_sida
from kommunhandlingar.maska_poolen import maska_poolen

PNR = "(personnummer borttaget)"
MOBIL = "(mobilnummer borttaget)"


class Konverteringen(unittest.TestCase):
    def test_sidans_text_och_celler_maskas_i_bada_vagarna(self):
        last = las_sida.Sida(
            "ok", False, "Sökanden 121212-1212", [[["Tel", "070-123 45 67"]]]
        )
        for vag, funktion in (("text", "textsida"), ("ocr", "ocr_sida")):
            with (
                self.subTest(vag),
                mock.patch.object(las_sida, "vag", return_value=vag),
                mock.patch.object(las_sida, funktion, return_value=last),
                mock.patch.object(las_sida.figurer, "har_figur", return_value=False),
            ):
                sida = las_sida.las_sida(None, None)
                self.assertEqual(sida.text, f"Sökanden {PNR}")
                self.assertEqual(sida.tabeller, [[["Tel", MOBIL]]])


class Poolen(unittest.TestCase):
    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.data = Path(katalog.name)
        self.md = self.data / "exempelby/ks/2025/2025-04-22/handlingar.md"
        self.md.parent.mkdir(parents=True)
        self.huvud = "---\nkalla_url: https://exempelby.se/121212-1212.pdf\n---\n"
        self.md.write_text(self.huvud + "Sökanden 121212-1212\n", encoding="utf-8")
        self.katalog = self.md.with_suffix(".tabeller")
        self.katalog.mkdir()
        self.csv = self.katalog / "1-1.csv"
        self.csv.write_text('Roll,Telefon\n"Sökanden, ombud",070-123 45 67\n')

    def test_text_och_tabeller_maskas_men_inte_front_matter(self):
        self.assertEqual(maska_poolen(self.data), 2)
        self.assertEqual(self.md.read_text(), self.huvud + f"Sökanden {PNR}\n")
        self.assertEqual(
            self.csv.read_text(), f'Roll,Telefon\n"Sökanden, ombud",{MOBIL}\n'
        )

    def test_en_andra_korning_andrar_ingenting(self):
        maska_poolen(self.data)
        self.assertEqual(maska_poolen(self.data), 0)

    def test_en_csv_utan_personuppgifter_skrivs_inte_om(self):
        utan = self.katalog / "1-2.csv"
        for innehall in ('"Roll","Antal"\nLedamot,3\n', "Roll,Antal\nLedamot,3"):
            with self.subTest(innehall):
                utan.write_text(innehall)
                maska_poolen(self.data)
                self.assertEqual(utan.read_text(), innehall)


if __name__ == "__main__":
    unittest.main()
