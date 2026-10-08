"""Krav: K11 och K15, ADR-0017.
Kod: src/kommunhandlingar/datakontroll_tolkning.py och datakontroll_tabeller.py.

Sidan 17 i fixturen är ett stapeldiagram med talen 120–150 och 90–105
ovanför staplarna och åren 2023–2026 under dem.
"""

import unittest

from kommunhandlingar.datakontroll_tolkning import TALEN, ordagrant, sidans_text
from tests.test_datakontroll import DOKUMENT, Pool

TABELLER = DOKUMENT.replace(".md", ".tabeller")


class TestTolkning(Pool):
    def setUp(self):
        super().setUp()
        self.md = self.data / DOKUMENT
        self.katalog = self.md.with_suffix(".tabeller")

    def tolka(self, csv: str, tolkade: str = "[17]", tolkning: str = "") -> None:
        text = self.md.read_text(encoding="utf-8")
        text += f"\n<!-- tolkning: modell, 2026-10-08 -->\n\n{tolkning}\n"
        self.md.write_text(text, encoding="utf-8")
        self.andra(DOKUMENT, tolkade=tolkade)
        (self.katalog / "17-1.tolkad.csv").write_text(csv)

    def test_tolkad_csv_med_talen_ur_sidans_text(self):
        self.tolka("År,Besök\n2023,120\n2024,130\n")
        self.assertEqual(self.fel(), [])

    def test_ett_tal_som_bara_star_i_tolkningen(self):
        self.tolka("År,Besök\n2023,999 st\n", tolkning="Staplarna visar 999.")
        fel = f"{TABELLER}/17-1.tolkad.csv: talet '999' står inte i sidans text"
        self.assertEqual(self.fel(), [fel])

    def test_siffror_som_inte_ar_ett_helt_tal(self):
        self.tolka("År,Besök\n2023,120.5\n")
        fel = f"{TABELLER}/17-1.tolkad.csv: cellen '120.5' har siffror som inte är"
        self.assertEqual(self.fel(), [fel + " ett helt tal"])

    def test_tolkad_csv_pa_en_sida_som_inte_ar_tolkad(self):
        self.tolka("År,Besök\n2023,120\n", tolkade="[]")
        self.assertEqual(
            self.fel(),
            [
                f"{DOKUMENT}: sidan 17 har 1 tolkningar men ska ha 0",
                f"{TABELLER}/17-1.tolkad.csv: sidan 17 står inte i tolkade",
            ],
        )

    def test_tolkad_sida_utan_tolkning(self):
        self.andra(DOKUMENT, tolkade="[17]")
        fel = f"{DOKUMENT}: sidan 17 har 0 tolkningar men ska ha 1"
        self.assertEqual(self.fel(), [fel])

    def test_tva_tolkningar_pa_en_sida(self):
        self.tolka("År,Besök\n2023,120\n", tolkning="<!-- tolkning: m, d -->")
        fel = f"{DOKUMENT}: sidan 17 har 2 tolkningar men ska ha 1"
        self.assertEqual(self.fel(), [fel])

    def test_en_sida_till_i_tolkningen(self):
        self.tolka("År,Besök\n2023,999\n", tolkning="<!-- sida 17 -->\n999")
        fel = f"{DOKUMENT}: sidorna står inte en gång var och i ordning"
        self.assertEqual(self.fel()[0], fel)

    def test_tolkade_utanfor_figurer(self):
        self.andra(DOKUMENT, tolkade="[3]")
        fel = f"{DOKUMENT}: tolkade är inte sidor ur figurer, i ordning"
        self.assertEqual(self.fel(), [fel])

    def test_tolkade_utan_figurer(self):
        self.andra(DOKUMENT, figurer="null")
        fel = f"{DOKUMENT}: figurer och tolkade är inte null samtidigt"
        self.assertEqual(self.fel(), [fel])

    def test_lucka_i_de_tolkade_numren(self):
        self.tolka("År,Besök\n2023,120\n")
        (self.katalog / "17-1.tolkad.csv").rename(self.katalog / "17-2.tolkad.csv")
        fel = f"{TABELLER}/17-2.tolkad.csv: 17-1.tolkad.csv saknas"
        self.assertEqual(self.fel(), [fel])


class TestSidansTal(unittest.TestCase):
    def test_lankar_klockslag_datum_och_tolkningen_ger_inga_tal(self):
        md = "---\nf: 1\n---\n<!-- sida 1 -->\nKl 13.30 den 2025-10-08\n"
        md += "[Tabell 1-1](p-76.tabeller/1-1.csv)\n<!-- tolkning: m -->\n99\n"
        self.assertEqual(TALEN.findall(sidans_text(md, 1)), [])

    def test_hela_tal(self):
        text = "Antal 1 120 och -45 % samt 3,5."
        self.assertEqual(TALEN.findall(text), ["1 120", "-45 %", "3,5"])

    def test_en_etikett_som_star_ordagrant(self):
        self.assertTrue(ordagrant("65–79 år", "Åldrar 65–79 år och 80–"))
        self.assertFalse(ordagrant("5–79", "Åldrar 65–79 år"))


if __name__ == "__main__":
    unittest.main()
