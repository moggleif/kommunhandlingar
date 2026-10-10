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
    hor_ihop,
)
from kommunhandlingar.konvertering.las_sida import Sida
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
        enkla = [f"{sida}-1.csv" for sida in range(3, 9)]
        self.assertEqual(
            sorted(self.filer), sorted(["1-3-1.csv", *enkla, "9-10-1.csv"])
        )

    def test_sammanslagen_tabell_har_rubriken_en_gang(self):
        tabell = rader(self.filer["1-3-1.csv"])
        self.assertEqual(tabell[0], RUBRIK)
        self.assertNotIn(RUBRIK, tabell[1:])
        avsnitt = ((1, 30), (2, 31), (3, 3))
        forvantat = [f"{a}.{i}" for a, n in avsnitt for i in range(1, n + 1)]
        self.assertEqual([rad[0] for rad in tabell[1:]], forvantat)

    def test_text_emellan_eller_andra_kolumner_skiljer(self):
        """Tabellen slutar mitt på sidan (3), rubrik i sidans text med en
        annan siffra på samma höjd (4–7) och andra kolumner (8)."""
        for sida in range(3, 9):
            with self.subTest(sida):
                tabell = rader(self.filer[f"{sida}-1.csv"])
                self.assertEqual(tabell[1][0], f"{sida + 1}.1")

    def test_tabell_utan_lodrata_linjer(self):
        tabell = rader(self.filer["9-10-1.csv"])
        self.assertEqual(
            (len(tabell), tabell[0][0], tabell[-1][0]), (36, "Post ab", "Post bk")
        )

    def test_tabellen_star_efter_forsta_sidans_text(self):
        text = skrivning.brodtext(self.sidor, "skarvar.tabeller")
        sida1, resten = text.split("<!-- sida 2 -->")
        self.assertIn("[Tabell 1-3-1](skarvar.tabeller/1-3-1.csv)", sida1)
        self.assertNotIn("1-3-1", resten)
        self.assertIn("[Tabell 3-1](skarvar.tabeller/3-1.csv)", resten)


class TestRegler(unittest.TestCase):
    def test_sida_utan_skarv_slas_aldrig_ihop(self):
        """En OCR-sida och en tom sida har ingen skarv."""
        tabell = Skarv(frozenset(), (60.0, 535.0), (60.0, 535.0), sista_nederst=True)
        self.assertTrue(fortsatter(tabell, tabell, set()))
        self.assertFalse(fortsatter(tabell, None, set()))
        self.assertFalse(fortsatter(None, tabell, set()))

    def test_tabell_som_slutar_mitt_pa_sidan_fortsatter_inte(self):
        mitt = Skarv(frozenset(), (60.0, 535.0), (60.0, 535.0))
        self.assertFalse(fortsatter(mitt, mitt, set()))

    def test_obekraftade_tal_slas_inte_ihop_med_bekraftade(self):
        skarv = Skarv(frozenset(), (60.0, 535.0), (60.0, 535.0), sista_nederst=True)
        tabell = [[["Nr"], ["1"]]]
        bekraftad = Sida("ok", False, tabeller=tabell, skarv=skarv)
        obekraftad = Sida("ok", True, tabeller=tabell, skarv=skarv)
        self.assertTrue(hor_ihop(bekraftad, bekraftad, set()))
        self.assertFalse(hor_ihop(bekraftad, obekraftad, set()))

    def test_bruten_rad_star_kvar_som_tva_rader(self):
        tabell = Sammanslagen(1, 1, 1, [["Nr", "Ärende"], ["1.1", "Början av"]])
        fortsattning = [["", "raden"], ["1.2", "Nästa"]]
        self.assertEqual(
            forlangd(tabell, 2, fortsattning).rader,
            [["Nr", "Ärende"], ["1.1", "Början av"], ["", "raden"], ["1.2", "Nästa"]],
        )


if __name__ == "__main__":
    unittest.main()
