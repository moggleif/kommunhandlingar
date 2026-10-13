"""Krav: K5, ADR-0040. Kod: src/kommunhandlingar/konvertering/spann.py och
rubriker.py.

Samma påhittade ord som i tests/test_olinjerade.py: teckenhöjd 10. Tabellen
har fyra kolumner med högerkanterna 200, 250, 300 och 350, och etiketterna
slutar vid 100, så att kolumnernas fack är 100–200, 200–250, 250–300 och
300–350.
"""

import unittest

from kommunhandlingar.konvertering.olinjerade import tabeller
from tests.test_olinjerade import ord_, rad, sida

KANTER = (200, 250, 300, 350)
KROPP = [
    rad(top, etikett, *((str(top + i), x1) for i, x1 in enumerate(KANTER)))
    for top, etikett in ((120, "Intäkter"), (140, "Kostnader"), (160, "Netto"))
]
UNDERRUBRIK = [
    ord_("Netto", 195, 80, 25),
    ord_("Utfall", 245, 80, 25),
    ord_("Budget", 295, 80, 30),
    ord_("Plan", 340, 80, 20),
]


def linje(x: float) -> dict:
    return {"x0": x, "top": 40, "bottom": 180}


def rubriker(*ovanfor: list[dict], linjer: tuple[dict, ...] = ()) -> list:
    (tabell,) = tabeller(sida(*ovanfor, *KROPP, linjer=linjer), [])
    return tabell.rader[: len(tabell.rader) - len(KROPP)]


class TestFack(unittest.TestCase):
    def test_rubrik_som_inte_star_i_linje_men_ryms_i_facket(self):
        """Centrerade rubriker, som i driftredovisningen i #123."""
        self.assertEqual(
            rubriker(UNDERRUBRIK), [["", "Netto", "Utfall", "Budget", "Plan"]]
        )

    def test_tva_rubriker_i_samma_fack_tas_inte_med(self):
        rubrik = [ord_("Netto", 150, 80, 25), ord_("Utfall", 195, 80, 25)]
        self.assertEqual(rubriker(rubrik + UNDERRUBRIK[1:]), [])


class TestSpann(unittest.TestCase):
    def test_rubrik_over_flera_kolumner_mellan_linjer(self):
        rubrik = [ord_("Budget", 195, 60, 30), ord_("Bokslut", 270, 60, 40)]
        self.assertEqual(
            rubriker(rubrik, UNDERRUBRIK, linjer=(linje(205), linje(355)))[0],
            ["", "Budget", "Bokslut", "", ""],
        )

    def test_tabellens_kant_dar_linje_saknas(self):
        rubrik = [ord_("Utfall", 240, 60, 90), ord_("Plan", 345, 60, 80)]
        self.assertEqual(
            rubriker(rubrik, UNDERRUBRIK, linjer=(linje(255),))[0],
            ["", "Utfall", "", "Plan", ""],
        )

    def test_utan_linjer_tas_rubriken_inte_med(self):
        rubrik = [ord_("Budget", 195, 60, 30), ord_("Bokslut", 270, 60, 40)]
        self.assertEqual(rubriker(rubrik, UNDERRUBRIK), [])

    def test_linje_som_inte_star_bredvid_raden_raknas_inte(self):
        rubrik = [ord_("Budget", 195, 60, 30), ord_("Bokslut", 270, 60, 40)]
        kort = {"x0": 205, "top": 115, "bottom": 180}
        self.assertEqual(rubriker(rubrik, UNDERRUBRIK, linjer=(kort,)), [])


class TestTextrader(unittest.TestCase):
    def test_tata_textrader_ar_en_rubrikrad(self):
        """`Netto-⏎anslag` och `Budget⏎2025` med 3 punkter emellan."""
        ovre = [ord_("Netto-", 195, 80, 25), ord_("Budget", 245, 80, 30)]
        ovre += [ord_("Netto-", 295, 80, 25), ord_("Plan", 340, 80, 20)]
        undre = [ord_("anslag", 195, 93, 25), ord_("2025", 245, 93, 20)]
        undre += [ord_("kostnader", 298, 93, 40)]
        self.assertEqual(
            rubriker(ovre, undre),
            [["", "Nettoanslag", "Budget 2025", "Nettokostnader", "Plan"]],
        )

    def test_textrader_en_teckenhojd_isar_ar_tva_rubrikrader(self):
        ovre = [ord_("Budget", 240, 60, 90), ord_("Plan", 345, 60, 80)]
        self.assertEqual(len(rubriker(ovre, UNDERRUBRIK, linjer=(linje(255),))), 2)

    def test_cell_under_en_rubrik_over_flera_kolumner_tas_inte_med(self):
        ovre = [ord_("Budget", 195, 80, 30), ord_("Bokslut", 270, 80, 40)]
        undre = [ord_("2025", 295, 93, 20)]
        self.assertEqual(rubriker(ovre, undre, linjer=(linje(205),)), [])
