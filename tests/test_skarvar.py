"""Krav: K19, ADR-0024. Kod: src/kommunhandlingar/konvertering/skarv.py,
konvertering/flersidiga.py och skrivning.py."""

import csv
import io
import unittest
from pathlib import Path

from kommunhandlingar import skrivning
from kommunhandlingar.konvertering.dokument import konvertera
from kommunhandlingar.konvertering.flersidiga import (
    Sammanslagen,
    forlangd,
    fortsatter,
)
from kommunhandlingar.konvertering.skarv import Skarv

PDF = Path(__file__).parent / "fixtures" / "pdf" / "skarvar.pdf"
RUBRIK = ["Nr", "Ärende", "Delegat"]


def rader(innehall: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(innehall)))


class TestSkarvar(unittest.TestCase):
    """Sidorna i skarvar.pdf; se tests/fixtures/pdf/skapa_skarvar.py."""

    @classmethod
    def setUpClass(cls):
        cls.sidor = konvertera(PDF).sidor
        cls.filer = skrivning.tabellfiler(cls.sidor)

    def test_filerna(self):
        self.assertEqual(
            sorted(self.filer),
            ["1-3-1.csv", "3-1.csv", "4-1.csv", "5-1.csv", "6-1.csv", "7-1.csv"],
        )

    def test_sammanslagen_tabell_har_rubriken_en_gang(self):
        tabell = rader(self.filer["1-3-1.csv"])
        self.assertEqual(tabell[0], RUBRIK)
        self.assertNotIn(RUBRIK, tabell[1:])
        avsnitt = ((1, 30), (2, 5), (3, 3))
        forvantat = [f"{a}.{i}" for a, n in avsnitt for i in range(1, n + 1)]
        self.assertEqual([rad[0] for rad in tabell[1:]], forvantat)

    def test_text_emellan_eller_andra_kolumner_skiljer(self):
        """Rubrik (3, 4), rubrik med en annan siffra på samma höjd (5), ett
        datum under tabellen (6) och andra kolumner (7)."""
        for sida, avsnitt in ((3, 4), (4, 5), (5, 6), (6, 7), (7, 8)):
            with self.subTest(sida):
                tabell = rader(self.filer[f"{sida}-1.csv"])
                self.assertEqual(tabell[1][0], f"{avsnitt}.1")

    def test_tabellen_star_efter_forsta_sidans_text(self):
        text = skrivning.brodtext(self.sidor, "skarvar.tabeller")
        sida1, resten = text.split("<!-- sida 2 -->")
        self.assertIn("[Tabell 1-3-1](skarvar.tabeller/1-3-1.csv)", sida1)
        self.assertNotIn("1-3-1", resten)
        self.assertIn("[Tabell 3-1](skarvar.tabeller/3-1.csv)", resten)


class TestRegler(unittest.TestCase):
    def test_ocr_sida_slas_aldrig_ihop(self):
        tabell = Skarv(frozenset(), (60.0, 535.0), (60.0, 535.0))
        self.assertTrue(fortsatter(tabell, tabell, set()))
        self.assertFalse(fortsatter(tabell, None, set()))
        self.assertFalse(fortsatter(None, tabell, set()))

    def test_bruten_rad_star_kvar_som_tva_rader(self):
        tabell = Sammanslagen(1, 1, 1, [["Nr", "Ärende"], ["1.1", "Början av"]])
        fortsattning = [["", "raden"], ["1.2", "Nästa"]]
        self.assertEqual(
            forlangd(tabell, 2, fortsattning).rader,
            [["Nr", "Ärende"], ["1.1", "Början av"], ["", "raden"], ["1.2", "Nästa"]],
        )


if __name__ == "__main__":
    unittest.main()
