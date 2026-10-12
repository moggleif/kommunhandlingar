"""Krav: K5, ADR-0028 och ADR-0029. Kod:
src/kommunhandlingar/konvertering/sammanslagna.py.

Slaget hos en cell som går över flera kolumner
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

import unittest

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.sammanslagna import (
    Textrad,
    cellens,
    faltets,
    fylld,
    slaget,
)

GRANSER = (0, 100, 150, 200)


def ord_(text: str, x0: float, x1: float) -> dict:
    return {"text": text, "x0": x0, "x1": x1, "top": 2, "bottom": 8}


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


class TestFylld(unittest.TestCase):
    def test_etikett_och_talrad_ar_tal(self):
        rader = [Textrad(0, ("Andel",)), Textrad(10, ("94,3 %", "96,9 %"))]
        self.assertEqual(fylld(rader), "tal")

    def test_blandad_rad_med_en_talrad_gar_inte(self):
        rader = [Textrad(0, ("2026-27:", "8 132")), Textrad(10, ("100", "200"))]
        self.assertEqual(fylld(rader), "")


class TestCellens(unittest.TestCase):
    def test_text_over_en_grans_ar_over(self):
        ord_lista = [ord_("Uppgift", 110, 140), ord_("saknas", 143, 170)]
        slag, ut = cellens((100, 0, 200, 10), ord_lista, GRANSER)
        self.assertEqual((slag, ut), ("over", [(1, Textrad(2, ("Uppgift saknas",)))]))


if __name__ == "__main__":
    unittest.main()
