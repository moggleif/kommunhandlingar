"""Krav: K11 och K15, ADR-0017.
Kod: src/kommunhandlingar/datakontroll_tolkning.py och datakontroll_tabeller.py.

Sidan 17 i fixturen är ett stapeldiagram med talen 120–150 och 90–105
ovanför staplarna och åren 2023–2026 under dem.
"""

import unittest

from kommunhandlingar.datakontroll_tolkning import (
    TALEN,
    ordagrant,
    sidans_tal,
    sidans_text,
)
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
        fel += " ett helt tal och står inte ordagrant i sidans text"
        self.assertEqual(self.fel(), [fel])

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
        self.assertEqual(
            self.fel(),
            [
                f"{DOKUMENT}: sidorna står inte en gång var och i ordning",
                f"{TABELLER}/17-1.tolkad.csv: talet '2023' står inte i sidans text",
            ],
        )

    def test_figurer_med_en_sida_som_inte_finns(self):
        self.andra(DOKUMENT, figurer="[17, 99]", tolkade="[99]")
        fel = f"{DOKUMENT}: figurer har sidor som inte finns i dokumentet"
        self.assertEqual(self.fel(), [fel])

    def test_tolkning_utan_modell_och_datum(self):
        self.tolka("År,Besök\n2023,120\n")
        md = self.md.read_text(encoding="utf-8")
        self.md.write_text(md.replace("modell, 2026-10-08", "x"), encoding="utf-8")
        fel = f"{DOKUMENT}: sidan 17 har en tolkning utan modell och datum"
        self.assertEqual(self.fel(), [fel])

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
        self.assertFalse(ordagrant("5–3", "ökning 2,5–3,5 procent"))
        self.assertFalse(ordagrant("65–79", "65–79,5"))
        for del_ in ("250–1 300", "1 250–1"):
            self.assertFalse(ordagrant(del_, "spannet 1 250–1 300 kr"))
        self.assertFalse(ordagrant("250–300", "ökning 1 250–300"))

    def test_inga_delar_av_tal_eller_ord(self):
        text = "covid-19, ADR-0017, K15, 3a, 2022/23 och spannet 1 250–1 300"
        self.assertEqual(TALEN.findall(text), [])

    def test_tal_delat_av_en_radbrytning_raknas_inte(self):
        text = "riksgenomsnittet (5\n053 kronor) och 1\u2009250"
        self.assertEqual(sidans_tal(text), set())
        self.assertFalse(ordagrant("053 kronor", text))

    def test_tal_pa_var_sin_rad_i_ett_diagram(self):
        text = "Besök\n\n150\n140\n130\n0–5\n6–15"
        self.assertEqual(sidans_tal(text), {"150", "140", "130"})
        self.assertTrue(ordagrant("0–5", text))
        self.assertFalse(sidans_tal("5\n053 kronor"))


if __name__ == "__main__":
    unittest.main()
