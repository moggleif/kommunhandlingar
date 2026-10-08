"""Krav: K5, ADR-0016. Kod: src/kommunhandlingar/konvertering/tabeller.py.

När en cell i en tabell med linjer rymmer mer än ett tal, och därför inte
är säker (docs/03-ARKITEKTUR.md#konvertering-och-kvalitet).
"""

import unittest

from kommunhandlingar.konvertering.tabeller import flera_falt, flera_tal

FLERA = [
    "4 078\n4 054",
    "2025\n14",
    "65,0 70,0 75,0",
    "1 2",
    "65 %\n70 %",
    "4 078\n-",
    "4 078\n4 054 tkr",
    "+5,0\n-2,0",
    "4.078 4.054",
    "65,0 70,0\nBudget",
    "Budget 2027\n65,0 70,0",
    "(2 100)\n1 978",
    "1 234 (1 150)",
    "4 078 / 4 054",
    "1 200 kr 1 300 kr",
    "74 984 kr 80%",
    "4 078 -",
    "- -2 001",
    "– –",
    "Intäkter\n4 078\n4 054",
]
ETT = [
    "4 078",
    "-2 313,1",
    "Budget\n2027",
    "2025-12-23",
    "1384 2025-00400",
    "(2 100)",
    "dnr\n2022/4901",
    "start läsår\n26/27",
    "kommunbudget\n2026\nFöredragande\n10 min",
    "2.2.18",
    "-2 108.1",
    "4 078 kr",
    "10 kap 1 och 2",
    "5 år (dag 5,15 och\n25 bevaras)",
]


def ord_(text: str, x0: float, x1: float) -> dict:
    return {"text": text, "x0": x0, "x1": x1, "top": 0, "bottom": 10}


class TestCeller(unittest.TestCase):
    def test_cellens_text_med_flera_tal(self):
        for cell in FLERA:
            self.assertTrue(flera_tal(cell), cell)

    def test_cellens_text_med_ett_tal(self):
        for cell in ETT:
            self.assertFalse(flera_tal(cell), cell)

    def test_tusentalsmellanrum_ar_ett_falt(self):
        tusental = [ord_("142", 0, 15), ord_("217", 17, 32), ord_("956", 34, 49)]
        self.assertFalse(flera_falt(tusental))

    def test_tva_falt_med_siffror_eller_streck_ar_flera_tal(self):
        self.assertTrue(flera_falt([ord_("120", 0, 15), ord_("135", 25, 40)]))
        kr = [ord_("1", 0, 5), ord_("200", 7, 22), ord_("kr", 24, 34)]
        self.assertTrue(flera_falt([*kr, ord_("-", 50, 54)]))

    def test_etikett_och_tal_ar_ett_tal(self):
        self.assertFalse(flera_falt([ord_("Antal", 0, 25), ord_("135", 45, 60)]))

    def test_tva_falt_med_text_och_siffror_ar_inte_flera_tal(self):
        lagrum = [ord_("LAS", 0, 15), ord_("7,", 17, 25), ord_("AB", 40, 50)]
        self.assertFalse(flera_falt([*lagrum, ord_("33-35", 52, 75)]))


if __name__ == "__main__":
    unittest.main()
