"""Krav: K5, ADR-0028. Kod: src/kommunhandlingar/konvertering/delade.py.

En tabell med linjer där en cell rymmer mer än ett tal delas efter de
lodräta linjer som finns i andra rader och efter rutornas textrader
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
Sidorna i delade.pdf beskrivs i tests/fixtures/pdf/skapa_delade.py.
"""

import unittest
from pathlib import Path
from types import SimpleNamespace

import pdfplumber

from kommunhandlingar.konvertering import delade, tabeller
from kommunhandlingar.konvertering.delade import Textrad, dela, kolumngranser, slaget
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
                "tabell-osaker",  # ett tal i en cell över två kolumner
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
            ord_ = sida.extract_words()
            _, (fallen,) = tabeller.sakra(sida, ord_)
            self.assertIsNone(delade.tabell(fallen, ord_))

    def test_tal_over_tva_kolumner_blir_ingen_tabell(self):
        sida = self.resultat.sidor[5]
        self.assertEqual(sida.tabeller, [])
        self.assertIn("8 132", sida.text)


def rutor(*kolumner: list[tuple[float, str]]) -> list[list[Textrad]]:
    return [
        [Textrad(topp, tuple(text.split("|"))) for topp, text in k] for k in kolumner
    ]


class TestDela(unittest.TestCase):
    def test_ett_tal_per_cell_delas_inte(self):
        platser = rutor([(0, "Prognos"), (10, "2024")], [(0, "4 078")])
        self.assertEqual(dela(platser, {"egen"}, False), [["Prognos\n2024", "4 078"]])

    def test_textraderna_pa_samma_hojd_blir_rader(self):
        platser = rutor(
            [(0, "Intäkter"), (10, "Kostnader")], [(0, "4 078"), (10, "-1 845")]
        )
        self.assertEqual(
            dela(platser, {"egen"}, False),
            [["Intäkter", "4 078"], ["Kostnader", "-1 845"]],
        )

    def test_nedersta_raden_skiljs_fran_rubriken(self):
        platser = rutor([(20, "Nämnden")], [(0, "Bokslut"), (10, "2025"), (20, "-1,3")])
        self.assertEqual(
            dela(platser, {"egen"}, False), [["", "Bokslut\n2025"], ["Nämnden", "-1,3"]]
        )

    def test_olika_hojd_ger_ingen_delning(self):
        platser = rutor([(5, "Intäkter")], [(0, "4 078"), (10, "4 054")])
        self.assertIsNone(dela(platser, {"egen"}, False))

    def test_tva_tal_pa_samma_textrad_ger_ingen_delning(self):
        platser = rutor([(0, "Lunch")], [(0, "1 200 kr|1 300 kr")])
        self.assertIsNone(dela(platser, {"egen"}, False))

    def test_tom_rad_star_kvar(self):
        self.assertEqual(dela(rutor([], []), {"egen"}, False), [["", ""]])

    def test_rader_ovanfor_pa_olika_hojd_ger_ingen_delning(self):
        platser = rutor(
            [(0, "Intäkter"), (10, "Kostnader"), (20, "Netto")],
            [(0, "4 078"), (20, "2 233")],
            [(10, "-2 001"), (20, "2 053")],
        )
        self.assertIsNone(dela(platser, {"egen"}, False))

    def test_etikett_under_talen_ger_ingen_delning(self):
        platser = rutor(
            [(10, "Intäkter"), (20, "Kostnader")],
            [(0, "4 078"), (20, "-1 845")],
        )
        self.assertIsNone(dela(platser, {"egen"}, False))

    def test_tal_med_ord_framfor_provas_ocksa_pa_hojd(self):
        platser = rutor(
            [(0, "Intäkter"), (10, "Kostnader"), (20, "Netto")],
            [(0, "ca 4 078"), (20, "2 233")],
            [(10, "ca -2 001"), (20, "2 053")],
        )
        self.assertIsNone(dela(platser, {"egen"}, False))

    def test_tal_i_delad_cell_pa_olika_hojd_ger_ingen_rad(self):
        platser = rutor([(0, "Övrigt")], [(10, "2 233")], [(0, "-2 001")])
        self.assertIsNone(dela(platser, {"hel"}, False))
        self.assertEqual(dela(platser, {"hel"}, True), [["Övrigt", "2 233", "-2 001"]])

    def test_forsta_raden_med_tva_etiketter_ger_ingen_rad(self):
        platser = rutor(
            [(0, "Intäkter"), (10, "Övrigt")], [(0, "4 078")], [(10, "-2 001")]
        )
        self.assertIsNone(dela(platser, {"hel"}, True))

    def test_rubrik_med_tom_horna_i_flera_rader(self):
        platser = rutor([], [(0, "Bokslut"), (10, "2025")], [(0, "Budget")])
        self.assertEqual(
            dela(platser, {"egen"}, True), [["", "Bokslut\n2025", "Budget"]]
        )

    def test_tva_tal_i_skilda_falt_ger_ingen_delning(self):
        platser = rutor([(0, "Lunch")], [(0, "12|345")])
        self.assertIsNone(dela(platser, {"egen"}, False))

    def test_rubrikcell_under_forsta_raden_ger_ingen_rad(self):
        platser = rutor([(0, "Summa")], [(0, "2026-27:")], [(0, "8 132")])
        self.assertIsNone(dela(platser, {"egen", "rubrik"}, False))


GRANSER = (0, 100, 150, 200)


class TestKolumngranser(unittest.TestCase):
    def test_kanter_inom_en_linje_slas_ihop(self):
        t = SimpleNamespace(cells=[(0, 0, 100, 10), (101.5, 0, 200, 10)])
        self.assertEqual(kolumngranser(t), (0, 100, 200))


class TestSlaget(unittest.TestCase):
    def test_tal_i_sammanslagen_cell_delas_inte(self):
        ut = [(2, Textrad(0, ("8 132",)))]
        self.assertIsNone(slaget((100, 0, 200, 10), ut, GRANSER)[1])

    def test_tal_med_ord_i_sammanslagen_cell_delas_inte(self):
        ut = [(2, Textrad(0, ("ca 8 132",)))]
        self.assertIsNone(slaget((100, 0, 200, 10), ut, GRANSER)[1])

    def test_etikett_och_tal_i_sammanslagen_cell_delas_inte(self):
        ut = [(1, Textrad(0, ("Båda åren",))), (2, Textrad(0, ("8 132",)))]
        self.assertIsNone(slaget((100, 0, 200, 10), ut, GRANSER)[1])

    def test_tal_i_varje_tackt_kolumn_ar_tal(self):
        ut = [(1, Textrad(0, ("1,0",))), (2, Textrad(0, ("0,0",)))]
        self.assertEqual(slaget((100, 0, 200, 10), ut, GRANSER)[0], "tal")

    def test_etiketter_med_artal_ar_rubrik(self):
        ut = [(1, Textrad(0, ("Bokslut 2025",))), (2, Textrad(0, ("Budget 2026",)))]
        self.assertEqual(slaget((100, 0, 200, 10), ut, GRANSER)[0], "rubrik")

    def test_etikett_och_tal_ar_ingen_rubrik(self):
        ut = [(1, Textrad(0, ("2026-27:",))), (2, Textrad(0, ("8 132",)))]
        self.assertIsNone(slaget((100, 0, 200, 10), ut, GRANSER)[1])

    def test_falt_utanfor_kolumnerna_delas_inte(self):
        ut = [(None, Textrad(0, ("8 132",)))]
        self.assertIsNone(slaget((100, 0, 200, 10), ut, GRANSER)[1])

    def test_ett_tal_per_tackt_kolumn_delas(self):
        ut = [(1, Textrad(0, ("2026",))), (2, Textrad(0, ("2027",)))]
        self.assertIsNotNone(slaget((100, 0, 200, 10), ut, GRANSER)[1])

    def test_rad_over_hela_bredden_delas(self):
        ut = [(0, Textrad(0, ("Lunch",))), (1, Textrad(0, ("10",)))]
        self.assertIsNotNone(slaget((0, 0, 200, 10), ut, GRANSER)[1])

    def test_text_i_sammanslagen_cell_delas(self):
        ut = [(1, Textrad(0, ("Summa",)))]
        self.assertIsNotNone(slaget((100, 0, 200, 10), ut, GRANSER)[1])


if __name__ == "__main__":
    unittest.main()
