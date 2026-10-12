"""Krav: K5, ADR-0029. Kod: src/kommunhandlingar/konvertering/talkolumner.py.

Kolumngränser mellan tal som står i linje utan lodrät linje emellan
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

import unittest
from types import SimpleNamespace

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.talkolumner import etiketterade, granser

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


LINJER = (0, 100, 300)


def tabell(*rader: list[tuple[str, float]]) -> tuple[SimpleNamespace, list[dict]]:
    """En tabell med en rad per lista av ord, tio punkter hög."""
    ord_ = [
        {
            "text": text,
            "x0": x0,
            "x1": x0 + 20,
            "top": 10 * nr + 2,
            "bottom": 10 * nr + 8,
        }
        for nr, rad in enumerate(rader)
        for text, x0 in rad
    ]
    radrutor = [
        SimpleNamespace(bbox=(0, 10 * nr, 300, 10 * nr + 10))
        for nr in range(len(rader))
    ]
    return SimpleNamespace(rows=radrutor), ord_


class TestEtiketterade(unittest.TestCase):
    def test_varje_rad_med_tal_har_en_etikett(self):
        t, ord_ = tabell(
            [("Namn", 5)], [("Heltid", 5), ("94,3", 120)], [("Män", 5), ("98,6", 120)]
        )
        self.assertTrue(etiketterade(t, ord_, LINJER))

    def test_rubrik_i_tva_rader_ar_inga_etiketter(self):
        t, ord_ = tabell(
            [("Utfall", 5)], [("helår", 5)], [("4 078", 5), ("4 054", 120)]
        )
        self.assertFalse(etiketterade(t, ord_, LINJER))

    def test_kallrad_ar_ingen_etikett_for_talen(self):
        t, ord_ = tabell(
            [("Utfall", 5)], [("4 078", 5), ("4 054", 120)], [("Källa:", 5)]
        )
        self.assertFalse(etiketterade(t, ord_, LINJER))

    def test_streck_ar_ingen_etikett(self):
        t, ord_ = tabell([("Utfall", 5)], [("–", 5), ("4 054", 120)])
        self.assertFalse(etiketterade(t, ord_, LINJER))

    def test_etikett_i_en_annan_kolumn_raknas_inte(self):
        t, ord_ = tabell([("Namn", 5)], [("4 078", 5), ("Heltid", 120)])
        self.assertFalse(etiketterade(t, ord_, LINJER))

    def test_etiketten_star_i_forsta_kolumnen_med_text(self):
        t, ord_ = tabell([("Namn", 120)], [("Heltid", 120), ("94,3", 200)])
        self.assertTrue(etiketterade(t, ord_, (0, 100, 180, 300)))


if __name__ == "__main__":
    unittest.main()
