"""Krav: K5, ADR-0028 och ADR-0029. Kod:
src/kommunhandlingar/konvertering/delade.py.

Hur en rad i en tabell med linjer delas efter rutornas textrader
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

import unittest

from kommunhandlingar.konvertering.delade import dela
from kommunhandlingar.konvertering.sammanslagna import Textrad


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

    def test_tva_tal_med_fotnotsstjarna_ger_ingen_delning(self):
        platser = rutor([(0, "Lunch")], [(0, "12*|345*")])
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

    def test_etikett_runt_sitt_tal_ger_en_rad(self):
        platser = rutor([(0, "Andel kvinnor"), (12, "som har heltid")], [(6, "94,3 %")])
        self.assertEqual(
            dela(platser, {"hel"}, False), [["Andel kvinnor\nsom har heltid", "94,3 %"]]
        )

    def test_tal_i_delad_cell_pa_olika_hojd_ger_ingen_rad(self):
        platser = rutor([(0, "Övrigt")], [(10, "2 233")], [(0, "-2 001")])
        self.assertIsNone(dela(platser, {"hel"}, False))
        self.assertEqual(dela(platser, {"hel"}, True), [["Övrigt", "2 233", "-2 001"]])

    def test_streck_provas_pa_hojd_som_tal(self):
        platser = rutor([(0, "Intäkter"), (10, "Kostnader")], [(0, "-")], [(10, "-")])
        self.assertIsNone(dela(platser, {"hel"}, False))

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

    def test_forsta_raden_provas_i_forsta_kolumnen_med_text(self):
        platser = rutor(
            [], [(0, "Intäkter"), (26, "Kostnader")], [(6, "4 078")], [(20, "-1 845")]
        )
        self.assertIsNone(dela(platser, {"hel"}, True))

    def test_tal_strax_under_en_etikett_ger_ingen_rad(self):
        platser = rutor(
            [(0, "Intäkter"), (22, "Kostnader")], [(5, "4 078")], [(5, "4 054")]
        )
        self.assertIsNone(dela(platser, {"hel"}, False))

    def test_tal_nara_en_etikett_i_tat_radavstand_ger_ingen_rad(self):
        platser = rutor(
            [(0, "Intäkter"), (14, "Kostnader")], [(4, "4 078")], [(4, "4 054")]
        )
        self.assertIsNone(dela(platser, {"hel"}, False))

    def test_text_over_en_grans_bara_i_forsta_raden(self):
        platser = rutor([(0, "Grundskola")], [(0, "Uppgift saknas")], [])
        self.assertIsNone(dela(platser, {"egen", "over"}, False))
        self.assertIsNotNone(dela(platser, {"egen", "over"}, True))


if __name__ == "__main__":
    unittest.main()
