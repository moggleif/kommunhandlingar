"""Krav: K5, ADR-0035. Kod: src/kommunhandlingar/konvertering/mellanrader.py,
olinjerade.py och rubriker.py.

Samma påhittade ord som i tests/test_olinjerade.py: teckenhöjd 10 och
raderna 20 punkter isär.
"""

import unittest

from kommunhandlingar.konvertering.mellanrader import foga
from kommunhandlingar.konvertering.olinjerade import tabeller
from tests.test_olinjerade import BUDGET, ord_, rad, sida

SKULDER = [
    rad(200, "Lån", ("300", 200), ("310", 300)),
    rad(220, "Leverantörer", ("40", 200), ("45", 300)),
]


def avsnitt(top: float, text: str) -> list[dict]:
    return [ord_(text, 100, top, 40)]


class TestFoga(unittest.TestCase):
    def test_fortsattning_fogas_till_etiketten_ovanfor(self):
        kropp = [["Avskrivningar på", "1", "2"], ["byggnader", "", ""]]
        self.assertEqual(foga(kropp), [["Avskrivningar på byggnader", "1", "2"]])

    def test_etikettrad_ovanfor_ar_borjan_pa_etiketten(self):
        kropp = [["Antal", "", ""], ["medarbetare per chef", "10,2", "10,3"]]
        self.assertEqual(foga(kropp), [["Antal medarbetare per chef", "10,2", "10,3"]])

    def test_tva_rader_med_tal_fogas_inte(self):
        kropp = [["Netto", "1", "2"], ["varav lån", "3", "4"]]
        self.assertEqual(foga(kropp), kropp)

    def test_rubrik_med_kolon_fogas_inte(self):
        kropp = [["Varav:", "", ""], ["lån", "300", "310"]]
        self.assertEqual(foga(kropp), kropp)

    def test_avsnittsrubrik_med_stor_bokstav_blir_egen_rad(self):
        kropp = [["Netto", "1", "2"], ["Skulder", "", ""]]
        self.assertEqual(foga(kropp), kropp)


class TestBroar(unittest.TestCase):
    def test_avsnittsrubrik_mellan_raderna_blir_en_rad_i_tabellen(self):
        (tabell,) = tabeller(sida(*BUDGET, avsnitt(180, "Skulder"), *SKULDER), [])
        self.assertEqual(tabell.rader[4], ["Skulder", "", ""])
        self.assertEqual(len(tabell.rader), 7)

    def test_fortsattning_mellan_raderna_fogas_till_etiketten(self):
        (tabell,) = tabeller(sida(*BUDGET, avsnitt(180, "verksamhet"), *SKULDER), [])
        self.assertEqual(tabell.rader[3], ["Netto verksamhet", "2 233", "2 053"])

    def test_fortsattning_efter_sista_raden_fogas_till_etiketten(self):
        (tabell,) = tabeller(sida(*BUDGET, avsnitt(180, "per enhet")), [])
        self.assertEqual(tabell.rader[-1], ["Netto per enhet", "2 233", "2 053"])

    def test_tre_etikettrader_emellan_bryter_tabellen(self):
        mellan = [avsnitt(top, "Skulder") for top in (180, 200, 220)]
        nedflyttade = [
            [dict(o, top=o["top"] + 60, bottom=o["bottom"] + 60) for o in r]
            for r in SKULDER
        ]
        hittade = tabeller(sida(*BUDGET, *mellan, *nedflyttade), [])
        self.assertEqual([len(t.rader) for t in hittade], [4])


class TestRubrikerOvanfor(unittest.TestCase):
    def test_rubrikrad_med_bara_artal_tas_med(self):
        artal = [ord_("2026", 200, 80, 18), ord_("2027", 300, 80, 18)]
        (tabell,) = tabeller(sida(artal, *BUDGET), [])
        self.assertEqual(tabell.rader[0], ["", "2026", "2027"])

    def test_avsnittsrubrik_mellan_rubriken_och_talen_tas_med(self):
        artal = [ord_("2026", 200, 65, 18), ord_("2027", 300, 65, 18)]
        (tabell,) = tabeller(sida(artal, avsnitt(80, "Intäkter"), *BUDGET), [])
        self.assertEqual(tabell.rader[:2], [["", "2026", "2027"], ["Intäkter", "", ""]])

    def test_avsnittsrubrik_utan_rubrik_ovanfor_tas_inte_med(self):
        (tabell,) = tabeller(sida(avsnitt(80, "Intäkter"), *BUDGET), [])
        self.assertEqual(len(tabell.rader), len(BUDGET))
