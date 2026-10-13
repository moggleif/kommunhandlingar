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
UNDERRUBRIK_CELLER = ["", "Netto", "Utfall", "Budget", "Plan"]


def linje(x: float) -> dict:
    return {"x0": x, "top": 40, "bottom": 180}


def rubriker(*ovanfor: list[dict], linjer: tuple[dict, ...] = ()) -> list:
    (tabell,) = tabeller(sida(*ovanfor, *KROPP, linjer=linjer), [])
    return tabell.rader[: len(tabell.rader) - len(KROPP)]


class TestFack(unittest.TestCase):
    def test_rubrik_som_inte_star_i_linje_men_ryms_i_facket(self):
        """Centrerade rubriker, som i driftredovisningen i #123."""
        self.assertEqual(rubriker(UNDERRUBRIK), [UNDERRUBRIK_CELLER])

    def test_tva_rubriker_i_samma_fack_tas_inte_med(self):
        rubrik = [ord_("Netto", 150, 80, 25), ord_("Utfall", 195, 80, 25)]
        self.assertEqual(rubriker(rubrik + UNDERRUBRIK[1:]), [])


LINJER = (linje(205), linje(355))
OVER_TRE = [ord_("Budget", 195, 60, 30), ord_("Bokslut", 310, 60, 60)]


class TestSpann(unittest.TestCase):
    def test_rubrik_over_flera_kolumner_mitt_emellan_linjer(self):
        self.assertEqual(
            rubriker(OVER_TRE, UNDERRUBRIK, linjer=LINJER),
            [["", "Budget", "Bokslut", "", ""], UNDERRUBRIK_CELLER],
        )

    def test_rubrik_som_inte_star_mitt_emellan_linjerna_tas_inte_med(self):
        """Två rubriker så tätt att de blev ett fält, som i ett stickprov."""
        rubrik = [ord_("Budget", 195, 60, 30), ord_("Antal tim", 275, 60, 60)]
        self.assertEqual(rubriker(rubrik, UNDERRUBRIK, linjer=LINJER), [])

    def test_utan_linjer_tas_rubriken_inte_med(self):
        self.assertEqual(rubriker(OVER_TRE, UNDERRUBRIK), [])

    def test_linje_bara_pa_ena_sidan_tas_inte_med(self):
        self.assertEqual(rubriker(OVER_TRE, UNDERRUBRIK, linjer=LINJER[:1]), [])

    def test_linjer_som_inte_star_mellan_kolumnerna_raknas_inte(self):
        """En sidram eller en sidstor ruta, och en centrerad sidrubrik."""
        rubrik = [ord_("Driftredovisning 2025", 310, 60, 60)]
        ram = (linje(250 - 220), linje(250 + 280))
        self.assertEqual(rubriker(rubrik, UNDERRUBRIK, linjer=ram), [])

    def test_linje_som_inte_star_bredvid_raden_raknas_inte(self):
        kort = {"x0": 205, "top": 115, "bottom": 180}
        linjer = (kort, linje(355))
        self.assertEqual(rubriker(OVER_TRE, UNDERRUBRIK, linjer=linjer), [])


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
        ovre = [ord_("Plan", 195, 60, 20), ord_("Plan", 245, 60, 20)]
        ovre += [ord_("Plan", 295, 60, 20), ord_("Plan", 345, 60, 20)]
        self.assertEqual(len(rubriker(ovre, UNDERRUBRIK)), 2)

    def test_ofullstandig_textrad_tatt_ovanfor_rubriken(self):
        """`tkr` tätt ovanför: den översta textraden står inte över varje
        kolumn, så rubriken blir inte halv."""
        tkr = [ord_("tkr", 345, 67, 15)]
        self.assertEqual(rubriker(tkr, UNDERRUBRIK), [])

    def test_streck_for_ett_utelamnat_ordled_star_kvar(self):
        ovre = [ord_("Kultur-", 195, 80, 25), ord_("Budget", 245, 80, 30)]
        ovre += [ord_("Utfall", 295, 80, 25), ord_("Plan", 340, 80, 20)]
        undre = [ord_("och fritid", 198, 93, 40), ord_("2025", 245, 93, 20)]
        undre += [ord_("text", 298, 93, 20)]
        self.assertEqual(rubriker(ovre, undre)[0][1], "Kultur- och fritid")

    def test_cell_under_en_rubrik_over_flera_kolumner_tas_inte_med(self):
        ovre = [ord_("Budget", 195, 80, 30), ord_("Bokslut", 310, 80, 60)]
        undre = [ord_("2025", 295, 93, 20)]
        self.assertEqual(rubriker(ovre, undre, linjer=LINJER), [])
