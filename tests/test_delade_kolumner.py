"""Krav: K5, ADR-0028. Kod: src/kommunhandlingar/konvertering/delade.py.

Hur en tabell med linjer delas i kolumner: kolumngränserna, ord över en
linje och slaget hos en cell som går över flera kolumner
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

import unittest
from types import SimpleNamespace

from kommunhandlingar.konvertering.delade import (
    Textrad,
    faltets,
    kolumngranser,
    over_linje,
    slaget,
)
from kommunhandlingar.konvertering.falt import Falt

GRANSER = (0, 100, 150, 200)


def tecken(x0: float, x1: float) -> dict:
    return {"x0": x0, "x1": x1, "top": 0, "bottom": 10}


class TestOverLinje(unittest.TestCase):
    CELLER = [(0, 0, 100, 10), (100, 0, 200, 10)]

    def test_ord_med_tecken_i_tva_celler_gar_over_linjen(self):
        ord_ = {"chars": [tecken(90, 96), tecken(98, 106)]}
        self.assertTrue(over_linje(ord_, self.CELLER))

    def test_tecken_pa_linjen_raknas_till_en_cell(self):
        ord_ = {"chars": [tecken(90, 96), tecken(96, 104)]}
        self.assertFalse(over_linje(ord_, self.CELLER))

    def test_ord_i_en_cell_gar_inte_over_linjen(self):
        ord_ = {"chars": [tecken(90, 95), tecken(95, 99)]}
        self.assertFalse(over_linje(ord_, self.CELLER))


class TestKolumngranser(unittest.TestCase):
    def test_kanter_inom_en_linje_slas_ihop(self):
        t = SimpleNamespace(cells=[(0, 0, 100, 10), (101.5, 0, 200, 10)])
        self.assertEqual(kolumngranser(t), (0, 100, 200))


class TestFaltets(unittest.TestCase):
    def test_text_over_en_grans_star_i_den_forsta_kolumnen(self):
        self.assertEqual(faltets(Falt("Andel av volymen", 90, 140), GRANSER), 0)

    def test_tal_over_en_grans_star_ingenstans(self):
        self.assertIsNone(faltets(Falt("8 132", 90, 140), GRANSER))


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

    def test_tal_med_fotnotsstjarna_ar_tal(self):
        ut = [(1, Textrad(0, ("4 078*",))), (2, Textrad(0, ("4 054*",)))]
        self.assertEqual(slaget((100, 0, 200, 10), ut, GRANSER)[0], "tal")

    def test_rubrik_med_text_och_varde_under_ar_rubrik(self):
        ut = [
            (1, Textrad(0, ("Andel av volymen",))),
            (1, Textrad(10, ("Bokslut 2024",))),
            (2, Textrad(10, ("Bokslut 2025",))),
            (1, Textrad(20, ("22,6",))),
            (2, Textrad(20, ("23,7",))),
        ]
        self.assertEqual(slaget((100, 0, 200, 30), ut, GRANSER)[0], "rubrik")

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
