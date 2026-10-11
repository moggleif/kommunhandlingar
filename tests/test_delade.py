"""Krav: K5, ADR-0028. Kod: src/kommunhandlingar/konvertering/delade.py.

En tabell med linjer där en cell rymmer mer än ett tal delas efter de
lodräta linjer som finns i andra rader och efter rutornas textrader
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
Sidorna i delade.pdf beskrivs i tests/fixtures/pdf/skapa_delade.py.
"""

import unittest
from pathlib import Path

import pdfplumber

from kommunhandlingar.konvertering import delade, tabeller
from kommunhandlingar.konvertering.delade import Textrad, dela
from kommunhandlingar.konvertering.dokument import konvertera

PDF = Path(__file__).parent / "fixtures" / "pdf" / "delade.pdf"
INTAKTER = ["Intäkter", "4 078", "4 054"]
KOSTNADER = ["Kostnader", "-1 845", "-2 001"]


class TestDeladeSidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resultat = konvertera(PDF)

    def tabell(self, sida: int) -> list[list[str]]:
        (tabell,) = self.resultat.sidor[sida].tabeller
        return tabell

    def test_kvalitet_per_sida(self):
        self.assertEqual(
            self.resultat.kvalitet_per_sida,
            [
                "ok",  # rubrikraden utan lodräta linjer
                "ok",  # tre rader i varje ruta
                "ok",  # rubrik och värde i samma ruta
                "tabell-osaker",  # etiketten mitt emellan talen
                "ok",  # läses i stället som tabell utan lodräta linjer
            ],
        )

    def test_rubrikraden_delas_efter_linjerna_under(self):
        self.assertEqual(
            self.tabell(0), [["Belopp, tkr", "2026", "2027"], INTAKTER, KOSTNADER]
        )

    def test_raderna_i_rutan_blir_egna_rader(self):
        netto = ["Netto", "2 233", "2 053"]
        self.assertEqual(
            self.tabell(1), [["Post", "2026", "2027"], INTAKTER, KOSTNADER, netto]
        )

    def test_rubrik_och_varde_i_samma_ruta(self):
        self.assertEqual(
            self.tabell(2),
            [
                ["", "Bokslut\n2025", "Budget\n2026"],
                ["Nämnden", "-1,3", "-1,7"],
                ["Kostnader", "-48,6", "-53,8"],
            ],
        )

    def test_etikett_mitt_emellan_blir_ingen_tabell(self):
        sida = self.resultat.sidor[3]
        self.assertEqual(sida.tabeller, [])
        self.assertIn("4 078", sida.text)

    def test_etikett_over_linjen_delas_inte(self):
        with pdfplumber.open(PDF) as pdf:
            sida = pdf.pages[4]
            _, (fallen,) = tabeller.sakra(sida)
            self.assertIsNone(delade.tabell(fallen, sida.extract_words()))


def rutor(*kolumner: list[tuple[float, str]]) -> list[list[Textrad]]:
    return [
        [Textrad(topp, tuple(text.split("|"))) for topp, text in k] for k in kolumner
    ]


class TestDela(unittest.TestCase):
    def test_ett_tal_per_cell_delas_inte(self):
        platser = rutor([(0, "Prognos"), (10, "2024")], [(0, "4 078")])
        self.assertEqual(dela(platser), [["Prognos\n2024", "4 078"]])

    def test_textraderna_pa_samma_hojd_blir_rader(self):
        platser = rutor(
            [(0, "Intäkter"), (10, "Kostnader")], [(0, "4 078"), (10, "-1 845")]
        )
        self.assertEqual(
            dela(platser), [["Intäkter", "4 078"], ["Kostnader", "-1 845"]]
        )

    def test_nedersta_raden_skiljs_fran_rubriken(self):
        platser = rutor([(20, "Nämnden")], [(0, "Bokslut"), (10, "2025"), (20, "-1,3")])
        self.assertEqual(dela(platser), [["", "Bokslut\n2025"], ["Nämnden", "-1,3"]])

    def test_olika_hojd_ger_ingen_delning(self):
        platser = rutor([(5, "Intäkter")], [(0, "4 078"), (10, "4 054")])
        self.assertIsNone(dela(platser))

    def test_tva_tal_pa_samma_textrad_ger_ingen_delning(self):
        platser = rutor([(0, "Lunch")], [(0, "1 200 kr|1 300 kr")])
        self.assertIsNone(dela(platser))

    def test_tom_rad_ger_inga_rader(self):
        self.assertEqual(dela(rutor([], [])), [])


if __name__ == "__main__":
    unittest.main()
