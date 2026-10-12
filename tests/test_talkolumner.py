"""Krav: K5, ADR-0029. Kod: src/kommunhandlingar/konvertering/talkolumner.py.

Kolumngränser mellan tal som står i linje utan lodrät linje emellan
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
"""

import unittest

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.talkolumner import granser

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
        rader = [talrad("Heltid", "94,3 %"), talrad("Män", "98,6 %")]
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

    def test_etiketterna_i_en_egen_kolumn_raknas(self):
        etiketter = [[Falt("Heltid", 0, 50)], [Falt("Män", 0, 30)]]
        tal = [
            [Falt("94,3 %", 110, 140), Falt("96,9 %", 190, 220)],
            [Falt("98,6 %", 110, 140), Falt("99,2 %", 190, 220)],
        ]
        self.assertEqual(granser([etiketter, tal]), [165])


if __name__ == "__main__":
    unittest.main()
