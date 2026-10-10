"""Krav: K19, ADR-0024. Kod: src/kommunhandlingar/konvertering/skarv.py,
konvertering/flersidiga.py och skrivning.py."""

import csv
import io
import unittest
from pathlib import Path

from kommunhandlingar import skrivning
from kommunhandlingar.konvertering.dokument import konvertera
from kommunhandlingar.konvertering.flersidiga import Tabell, forlangd
from kommunhandlingar.konvertering.skarv import Skarv, ar_marginal

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
            sorted(self.filer), ["1-3-1.csv", "3-1.csv", "4-1.csv", "5-1.csv"]
        )

    def test_sammanslagen_tabell_har_rubriken_en_gang(self):
        tabell = rader(self.filer["1-3-1.csv"])
        self.assertEqual(tabell[0], RUBRIK)
        self.assertNotIn(RUBRIK, tabell[1:])
        nummer = [rad[0] for rad in tabell[1:]]
        avsnitt = ((1, 30), (2, 5), (3, 3))
        forvantat = [f"{a}.{i}" for a, n in avsnitt for i in range(1, n + 1)]
        self.assertEqual(nummer, forvantat)

    def test_text_emellan_eller_annan_bredd_skiljer(self):
        for namn, forsta in (
            ("3-1.csv", "4.1"),
            ("4-1.csv", "5.1"),
            ("5-1.csv", "6.1"),
        ):
            self.assertEqual(rader(self.filer[namn])[1][0], forsta, namn)

    def test_tabellen_star_efter_forsta_sidans_text(self):
        text = skrivning.brodtext(self.sidor, "skarvar.tabeller")
        sida1, resten = text.split("<!-- sida 2 -->")
        self.assertIn("[Tabell 1-3-1](skarvar.tabeller/1-3-1.csv)", sida1)
        self.assertNotIn("1-3-1", resten)
        self.assertIn("[Tabell 3-1](skarvar.tabeller/3-1.csv)", resten)


class TestRegler(unittest.TestCase):
    def test_sidnummer_och_sidhuvud_ar_marginal(self):
        granne = Skarv((0, 0), (0, 0), [], [], frozenset({"Exempelby kommun ()"}))
        for rad in ("8", "2 (4)", "Exempelby kommun 3(4)"):
            self.assertTrue(ar_marginal(rad, granne), rad)
        self.assertFalse(ar_marginal("Avsnitt 4 Ekonomi", granne))

    def test_bruten_rad_star_kvar_som_tva_rader(self):
        tabell = Tabell(1, 1, 1, [["Nr", "Ärende"], ["1.1", "Början av"]])
        fortsattning = [["", "raden"], ["1.2", "Nästa"]]
        self.assertEqual(
            forlangd(tabell, 2, fortsattning).rader,
            [["Nr", "Ärende"], ["1.1", "Början av"], ["", "raden"], ["1.2", "Nästa"]],
        )


if __name__ == "__main__":
    unittest.main()
