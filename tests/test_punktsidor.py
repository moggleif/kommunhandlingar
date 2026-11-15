"""Krav: K54 i docs/02-KRAV.md, ADR-0078.
Kod: src/kommunhandlingar/webbplats/punktsidor.py."""

import unittest

from kommunhandlingar.webbplats.dagordning import Punkt
from kommunhandlingar.webbplats.punktsidor import (
    ar_punktens,
    handlingen,
    sammanfattning,
    sidor,
)

HANDLINGAR = """<!-- sida 1 -->

| 1. | Delårsrapport | 2026-00543 | Förslag |

<!-- sida 2 -->

§ 289                      Dnr KS-2026-00543
Delårsrapport

<!-- sida 3 -->

TJÄNSTESKRIVELSE
Diarienummer
KS-2026-00543

Sammanfattning av ärendet

Rapporten omfattar
kommunen.

Resultatet är 542 miljoner.
1 (2)
Kungsbacka kommun

<!-- sida 4 -->

§ 279 Dnr KS-2026-00246
Omprövning

<!-- sida 5 -->

Bilaga med Dnr KS-2026-00543 igen
"""


def punkt(nummer: int, diarienummer: str) -> Punkt:
    return Punkt(nummer, "", diarienummer, ())


class TestHandlingen(unittest.TestCase):
    def setUp(self):
        self.sidor = sidor(HANDLINGAR)

    def test_en_punkt_borjar_dar_dess_diarienummer_star_efter_dnr(self):
        omfang = handlingen(
            self.sidor, [punkt(1, "2026-00543"), punkt(5, "2026-00246")]
        )
        self.assertEqual(omfang, {1: range(2, 4), 5: range(4, 6)})

    def test_dagordningens_tabell_ar_ingen_borjan(self):
        self.assertEqual(handlingen(self.sidor, [punkt(1, "2026-00543")])[1].start, 2)

    def test_en_punkt_utan_sida_har_ingen_handling(self):
        omfang = handlingen(
            self.sidor, [punkt(2, "2026-00014"), punkt(5, "2026-00246")]
        )
        self.assertEqual(omfang, {5: range(4, 6)})

    def test_handlingarna_foljer_dagordningen(self):
        omfang = handlingen(
            self.sidor, [punkt(5, "2026-00246"), punkt(6, "2026-00543")]
        )
        self.assertEqual(omfang, {5: range(4, 5), 6: range(5, 6)})

    def test_forledet_saknas_i_kallelsen(self):
        self.assertTrue(ar_punktens("KS-2026-00543", punkt(1, "2026-00543")))
        self.assertTrue(ar_punktens("2022-00157", punkt(1, "2022-00157")))
        self.assertFalse(ar_punktens("KS-2026-005430", punkt(1, "2026-00543")))
        self.assertFalse(ar_punktens("KS-12026-00543", punkt(1, "2026-00543")))


class TestSammanfattningen(unittest.TestCase):
    def test_stycken_till_sidnumret_med_raderna_hopfogade(self):
        self.assertEqual(
            sammanfattning(sidor(HANDLINGAR), range(2, 4)),
            ("Rapporten omfattar kommunen.", "Resultatet är 542 miljoner."),
        )

    def test_utan_rubriken_ingen_sammanfattning(self):
        self.assertEqual(sammanfattning(sidor(HANDLINGAR), range(4, 6)), ())
