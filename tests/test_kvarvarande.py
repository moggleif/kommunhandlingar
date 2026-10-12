"""Krav: K5, ADR-0033. Kod: src/kommunhandlingar/konvertering/kvarvarande.py.

Orden är påhittade med koordinater i punkter och teckenhöjd 10. Löptexten i
den vänstra spalten står på samma textrad som tabellen i den högra, så
raderna blir ingen tabell utan lodräta linjer.
"""

import unittest
from pathlib import Path
from types import SimpleNamespace

import pdfplumber

from kommunhandlingar.konvertering.kvarvarande import har_talrader
from kommunhandlingar.konvertering.las_sida import textsida

HOJD = 10
FACIT = Path(__file__).parent / "fixtures" / "facit"


def ord_(text: str, x1: float, top: float, bredd: float = 15) -> dict:
    return {"text": text, "x0": x1 - bredd, "x1": x1, "top": top, "bottom": top + HOJD}


def rad(top: float, etikett: str, *tal: tuple[str, float]) -> list[dict]:
    ut = [ord_("löptext", 150, top, 140), ord_(etikett, 220, top, 40)]
    return ut + [ord_(text, x1, top) for text, x1 in tal]


def sida(*rader: list[dict]) -> SimpleNamespace:
    alla = [o for r in rader for o in r]
    return SimpleNamespace(extract_words=lambda **_: alla)


INKOMSTER = rad(100, "Inkomster", ("0,0", 300), ("1,5", 350))
UTGIFTER = rad(120, "Utgifter", ("-2,0", 300), ("-14,8", 350))
NETTO = rad(140, "Netto", ("-2,0", 300), ("-13,3", 350))


class TestKvarvarande(unittest.TestCase):
    def test_tre_talrader_i_linje_finns(self):
        self.assertTrue(har_talrader(sida(INKOMSTER, UTGIFTER, NETTO), []))

    def test_tva_talrader_racker_inte(self):
        self.assertFalse(har_talrader(sida(INKOMSTER, UTGIFTER), []))

    def test_rader_i_en_last_tabell_raknas_inte(self):
        self.assertFalse(
            har_talrader(sida(INKOMSTER, UTGIFTER, NETTO), [(0, 90, 400, 160)])
        )

    def test_tal_som_inte_star_i_linje_raknas_inte(self):
        forskjuten = rad(140, "Netto", ("-2,0", 280), ("-13,3", 330))
        self.assertFalse(har_talrader(sida(INKOMSTER, UTGIFTER, forskjuten), []))

    def test_artal_ar_inga_varden(self):
        ar = [rad(100 + 20 * i, "År", ("2024", 300), ("2025", 350)) for i in range(3)]
        self.assertFalse(har_talrader(sida(*ar), []))

    def test_fyrsiffriga_belopp_ar_varden(self):
        belopp = [
            rad(100 + 20 * i, "Post", ("1250", 300), ("2300", 350)) for i in range(3)
        ]
        self.assertTrue(har_talrader(sida(*belopp), []))

    def test_tvetydigt_mellanrum_skiljer_falten(self):
        """7 punkter mellan talen är varken samma fält eller ett nytt."""
        tata = [rad(100 + 20 * i, "Post", ("1,5", 300), ("2,5", 322)) for i in range(3)]
        self.assertTrue(har_talrader(sida(*tata), []))


class TestSidan(unittest.TestCase):
    def test_tabell_i_spalt_bredvid_loptext_marker_sidan(self):
        """Tabellen Avfall & Återvinning i årsredovisningen (#92)."""
        with pdfplumber.open(FACIT / "arsredovisning-2025" / "utdrag.pdf") as pdf:
            self.assertEqual(textsida(pdf.pages[3]).kvalitet, "tabell-osaker")


if __name__ == "__main__":
    unittest.main()
