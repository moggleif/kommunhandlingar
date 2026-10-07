"""Krav: K4–K6, ADR-0005 och ADR-0009. Kod: src/kommunhandlingar/konvertering/."""

import unittest
from pathlib import Path

from kommunhandlingar.konvertering.dokument import konvertera
from kommunhandlingar.konvertering.kvalitet import dokumentets
from kommunhandlingar.konvertering.tabeller import som_csv, som_markdown
from kommunhandlingar.konvertering.text import ar_talrad, stycken
from kommunhandlingar.konvertering.vag import langd_av, tackt_yta

PDF = Path(__file__).parent / "fixtures" / "pdf"


class TestSidorna(unittest.TestCase):
    """Varje sida i sidor.pdf är ett fall; se tests/fixtures/pdf/skapa.py."""

    @classmethod
    def setUpClass(cls):
        cls.resultat = konvertera(PDF / "sidor.pdf")

    def test_kvalitet_per_sida(self):
        self.assertEqual(
            self.resultat.kvalitet_per_sida,
            [
                "ok",  # löptext med datum och diarienummer
                "ok",  # tabell med linjer och en färgad rad
                "tabell-osaker",  # tabell utan lodräta linjer
                "tom",  # tom sida
                "ej-konverterad",  # skanning utan text; OCR kommer i #36
                "ej-konverterad",  # skanning med osynligt OCR-lager
                "ej-konverterad",  # skanning med en stämpel i synlig text
                "ok",  # omslag: helsidesbild med mer än 50 synliga tecken
                "ej-konverterad",  # text omgjord till kurvor
                "tom",  # bara ett streck
            ],
        )
        self.assertEqual(self.resultat.kvalitet, "delvis")
        self.assertEqual(self.resultat.tal_obekraftade, [5, 6, 7, 9])

    def test_loptext(self):
        self.assertEqual(
            self.resultat.sidor[0].text,
            "Protokoll 2026-08-11\nDnr KS 2023-00686\nParagraf 12 beslutades.",
        )

    def test_saker_tabell_blir_rader_och_inte_text(self):
        sida = self.resultat.sidor[1]
        self.assertEqual(
            sida.tabeller,
            [[["Post", "2027"], ["Intäkter", "4 078"], ["Kostnader", "-1 845"]]],
        )
        self.assertNotIn("4 078", sida.text)

    def test_osaker_tabell_behaller_uppstallningen(self):
        text = self.resultat.sidor[2].text
        self.assertTrue(text.startswith("```osaker-tabell\nIntäkter"))
        self.assertIn("4 078         4 054", text)
        self.assertEqual(self.resultat.sidor[2].tabeller, [])


class TestFilerSomInteGarAttOppna(unittest.TestCase):
    def test_orsaker(self):
        for fil, orsak in (
            ("krypterad.pdf", "krypterad"),
            ("trasig.pdf", "trasig-pdf"),
            ("inte.pdf", "inte-pdf"),
        ):
            resultat = konvertera(PDF / fil)
            self.assertEqual(
                (resultat.kvalitet, resultat.fel), ("ej-konverterad", orsak)
            )
            self.assertIsNone(resultat.kvalitet_per_sida)
            self.assertIsNone(resultat.tal_obekraftade)

    def test_losenord_som_bara_begransar_hindrar_inte(self):
        self.assertEqual(konvertera(PDF / "begransad.pdf").kvalitet, "delvis")


class TestRegler(unittest.TestCase):
    def test_dokumentets_kvalitet(self):
        for sidor, vantat in (
            (["ok", "tom"], "full"),
            (["ok", "tabell-osaker"], "text-utan-tabeller"),
            (["ok", "ocr", "tabell-osaker"], "ocr"),
            (["ocr", "ej-konverterad"], "delvis"),
            (["tom", "ej-konverterad"], "ej-konverterad"),
            (["tom"], "ej-konverterad"),
        ):
            self.assertEqual(dokumentets(sidor), vantat, sidor)

    def test_talrader(self):
        self.assertTrue(ar_talrad("Netto      2 233     -1 845"))
        self.assertTrue(ar_talrad("Andel   21,33   53 %   53%"))
        self.assertFalse(ar_talrad("Datum   2026-08-11   2023-00686"))
        self.assertFalse(ar_talrad("Belopp 2027 och 2028"))

    def test_tva_talrader_ar_ingen_tabell(self):
        text, osaker = stycken("A   1   2\nB   3   4\nText")
        self.assertFalse(osaker)
        self.assertEqual(text, "A   1   2\nB   3   4\nText")

    def test_tomma_rader_far_sta_inom_foljden(self):
        text, osaker = stycken("Rubrik\n  A   1   2\n\n  B   3   4\n  C   5   6\nSlut")
        self.assertTrue(osaker)
        self.assertEqual(
            text,
            "Rubrik\n\n```osaker-tabell\nA   1   2\n\nB   3   4\nC   5   6\n```"
            "\n\nSlut",
        )

    def test_tackt_yta_raknar_overlapp_en_gang(self):
        self.assertEqual(tackt_yta([(0, 0, 10, 10), (5, 5, 15, 15)]), 175)
        self.assertEqual(langd_av([(0, 4), (2, 6), (8, 9)]), 7)


class TestTabellformat(unittest.TestCase):
    def test_csv_enligt_rfc_4180_med_lf(self):
        self.assertEqual(
            som_csv([["a,b", "rad\nbrytning"], ["", "21,5"]]),
            '"a,b","rad\nbrytning"\n,"21,5"\n',
        )

    def test_markdown(self):
        self.assertEqual(
            som_markdown([["a|b", "c"], ["rad\nbrytning", ""]]),
            "| a\\|b | c |\n| --- | --- |\n| rad<br>brytning |  |",
        )
