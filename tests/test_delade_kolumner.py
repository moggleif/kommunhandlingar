"""Krav: K5, ADR-0028. Kod: src/kommunhandlingar/konvertering/delade.py.

Hur en tabell med linjer delas i kolumner: kolumngränserna och ord över
en linje
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

import unittest
from types import SimpleNamespace

from kommunhandlingar.konvertering.delade import kolumngranser, over_linje


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


if __name__ == "__main__":
    unittest.main()
