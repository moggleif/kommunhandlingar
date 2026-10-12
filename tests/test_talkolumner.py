"""Krav: K5, ADR-0029. Kod: src/kommunhandlingar/konvertering/talkolumner.py.

Kolumngränser mellan tal som står i linje utan lodrät linje emellan
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

import unittest

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.talkolumner import (
    etiketter_utanfor,
    etiketterade,
    granser,
)

RUBRIK = [
    Falt("Namn", 0, 30),
    Falt("Bokslut 2024", 90, 150),
    Falt("Bokslut 2025", 170, 230),
]


def talrad(etikett: str, *tal: str) -> list[Falt]:
    x1 = [140, 220, 300]
    return [Falt(etikett, 0, 50)] + [
        Falt(t, x - 30, x) for t, x in zip(tal, x1, strict=False)
    ]


class TestGranser(unittest.TestCase):
    def test_tal_i_linje_ger_en_grans_per_kolumn(self):
        rader = [
            RUBRIK,
            talrad("Heltid", "94,3 %", "96,9 %"),
            talrad("Män", "98,6 %", "99,2 %"),
        ]
        self.assertEqual(granser([rader]), [70, 160])

    def test_en_kolumn_med_ett_enda_tal_ger_ingen_grans(self):
        rader = [talrad("Heltid", "94,3 %", "96,9 %"), talrad("Män", "98,6 %")]
        self.assertEqual(granser([rader]), [])

    def test_utan_rad_med_tva_tal_ges_ingen_grans(self):
        rader = [
            talrad("Heltid", "94,3 %"),
            [Falt("Män", 0, 30), Falt("98,6 %", 190, 220)],
            talrad("Deltid", "5,7 %"),
            [Falt("Kvinnor", 0, 30), Falt("1,4 %", 190, 220)],
        ]
        self.assertEqual(granser([rader]), [])

    def test_tva_tal_i_samma_grupp_ger_ingen_grans(self):
        rader = [
            talrad("Heltid", "94,3 %", "96,9 %"),
            [
                Falt("Män", 0, 30),
                Falt("1", 110, 120),
                Falt("2", 125, 140),
                Falt("3", 190, 220),
            ],
        ]
        self.assertEqual(granser([rader]), [])

    def test_rubrik_over_en_tom_kolumn_far_en_grans(self):
        rubrik = [*RUBRIK, Falt("Bokslut 2026", 250, 310)]
        rader = [
            rubrik,
            talrad("Heltid", "94,3 %", "96,9 %"),
            talrad("Män", "98,6 %", "99,2 %"),
        ]
        self.assertEqual(granser([rader]), [70, 160, 240])

    def test_forsta_kolumnen_utan_etiketter_ger_ingen_grans(self):
        rader = [
            [Falt("12,0", 0, 30), Falt("94,3", 110, 140), Falt("96,9", 190, 220)],
            [Falt("13,0", 0, 30), Falt("98,6", 110, 140), Falt("99,2", 190, 220)],
        ]
        self.assertEqual(granser([rader]), [])

    def test_etiketter_som_inte_star_fore_talen_ger_ingen_grans(self):
        rader = [
            [Falt("Heltid", 200, 240)],
            [Falt("Deltid", 200, 240)],
            [Falt("94,3", 0, 30), Falt("96,9", 60, 90)],
            [Falt("98,6", 0, 30), Falt("99,2", 60, 90)],
        ]
        self.assertEqual(granser([rader]), [])

    def test_etikett_med_siffra_fore_talen_ar_ingen_kolumn(self):
        rader = [
            RUBRIK,
            talrad("Heltid", "94,3 %", "96,9 %"),
            talrad("Klass 1", "98,6 %", "99,2 %"),
            talrad("Män", "97,0 %", "98,1 %"),
        ]
        self.assertEqual(granser([rader]), [70, 160])

    def test_etiketterna_i_en_egen_kolumn_raknas(self):
        etiketter = [[Falt("Heltid", 0, 50)], [Falt("Män", 0, 30)]]
        tal = [
            [Falt("94,3 %", 110, 140), Falt("96,9 %", 190, 220)],
            [Falt("98,6 %", 110, 140), Falt("99,2 %", 190, 220)],
        ]
        self.assertEqual(granser([etiketter, tal]), [165])


class TestEtiketterade(unittest.TestCase):
    def test_varje_rad_med_tal_har_en_etikett(self):
        rader = [["", "Namn", "2024"], ["", "Andel\nheltid", "94,3 %"]]
        self.assertTrue(etiketterade(rader))

    def test_rubrik_i_tva_rader_ar_ingen_etikett(self):
        rader = [["Utfall", "Budget"], ["helår\n4 078", "4 054"], ["-1 845", "-2 001"]]
        self.assertFalse(etiketterade(rader))

    def test_rad_utan_tal_behover_ingen_etikett(self):
        rader = [["Namn", "2024"], ["Heltid", "94,3"], ["", ""], ["Källa: HR", ""]]
        self.assertTrue(etiketterade(rader))

    def test_tal_med_enhet_ar_ingen_etikett(self):
        rader = [["Utfall", "Budget"], ["94,3 %", "96,9 %"], ["4 078 tkr", "1 tkr"]]
        self.assertFalse(etiketterade(rader))

    def test_enhet_eller_notmarke_pa_egen_rad_ar_ingen_etikett(self):
        for markning in ("tkr", "%", "a)", "(tkr)", "tkr.", "kr/st"):
            with self.subTest(markning):
                rader = [["", "Utfall"], [markning, "4 078"], ["Män", "94,3"]]
                self.assertFalse(etiketterade(rader))

    def test_streck_ar_ingen_etikett(self):
        self.assertFalse(etiketterade([["Utfall", "Budget"], ["–", "4 054"]]))


def ord_vid(x0: float, x1: float, topp: float) -> list[dict]:
    return [{"text": "Intäkter", "x0": x0, "x1": x1, "top": topp, "bottom": topp + 8}]


class TestEtiketterUtanfor(unittest.TestCase):
    BBOX = (100, 0, 300, 40)

    def test_text_till_vanster_i_hojd_med_tabellen(self):
        self.assertTrue(etiketter_utanfor(self.BBOX, ord_vid(10, 60, 22)))

    def test_etikett_med_punktledare_in_over_kanten(self):
        self.assertTrue(etiketter_utanfor(self.BBOX, ord_vid(30, 113, 22)))

    def test_text_till_vanster_ovanfor_tabellen_raknas_inte(self):
        self.assertFalse(etiketter_utanfor(self.BBOX, ord_vid(10, 60, -20)))


if __name__ == "__main__":
    unittest.main()
