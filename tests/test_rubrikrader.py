"""Krav: K5, ADR-0037. Kod: src/kommunhandlingar/konvertering/olinjerade.py,
rader.py och rubriker.py.

Samma påhittade ord som i tests/test_olinjerade.py: teckenhöjd 10 och
raderna 20 punkter isär, så att fyra teckenhöjder är 40 punkter.
"""

import unittest

from kommunhandlingar.konvertering.olinjerade import tabeller
from tests.test_olinjerade import BUDGET, ord_, rad, sida

ARTAL = [ord_("2026", 200, 80, 18), ord_("2027", 300, 80, 18)]


def flyttad(rader: list[list[dict]], steg: float) -> list[list[dict]]:
    return [
        [dict(o, top=o["top"] + steg, bottom=o["bottom"] + steg) for o in r]
        for r in rader
    ]


class TestRadavstand(unittest.TestCase):
    def test_tabell_med_storre_radavstand_blir_en(self):
        sista = rad(205, "Finans", ("70", 200), ("73", 300))
        (tabell,) = tabeller(sida(*BUDGET, sista), [])
        self.assertEqual(tabell.rader[-1], ["Finans", "70", "73"])

    def test_sidnummer_under_tabellen_tas_inte_med(self):
        sidfot = [ord_("Årsredovisning 2025", 370, 185, 120), ord_("79", 400, 185, 10)]
        (tabell,) = tabeller(sida(*BUDGET, sidfot), [])
        self.assertEqual(len(tabell.rader), len(BUDGET))


class TestArtalsrader(unittest.TestCase):
    def test_rubrikrad_med_etikett_och_artal_tas_med(self):
        rubrik = [ord_("Kommunen", 100, 55, 40), *flyttad([ARTAL], -25)[0]]
        (tabell,) = tabeller(sida(rubrik, *BUDGET), [])
        self.assertEqual(tabell.rader[0], ["Kommunen", "2026", "2027"])

    def test_artal_mellan_tva_tabeller_blir_den_nedres_rubrik(self):
        mellan = flyttad([ARTAL], 100)
        hittade = tabeller(sida(*BUDGET, *mellan, *flyttad(BUDGET, 120)), [])
        self.assertEqual([len(t.rader) for t in hittade], [4, 5])
        self.assertEqual(hittade[1].rader[0], ["", "2026", "2027"])

    def test_text_ovanfor_rubriken_som_borjar_bland_etiketterna(self):
        text = [ord_("Följande tabell visar projekten", 250, 65, 190)]
        (tabell,) = tabeller(sida(text, ARTAL, *BUDGET), [])
        self.assertEqual(tabell.rader[0], ["", "2026", "2027"])
