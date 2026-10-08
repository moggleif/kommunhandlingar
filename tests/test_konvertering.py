"""Krav: K4–K6, ADR-0005 och ADR-0009. Kod: src/kommunhandlingar/konvertering/."""

import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pypdfium2 as pdfium

from kommunhandlingar.fel import Konfigurationsfel
from kommunhandlingar.konvertering import ocr
from kommunhandlingar.konvertering.dokument import konvertera, versioner
from kommunhandlingar.konvertering.kvalitet import dokumentets
from kommunhandlingar.konvertering.ocr import medelsakerhet
from kommunhandlingar.konvertering.tabeller import som_csv, som_markdown
from kommunhandlingar.konvertering.text import ar_talrad, stycken
from kommunhandlingar.konvertering.vag import langd_av, tackt_yta, vag

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
                "ok",  # tabell utan lodräta linjer, talen i linje
                "tom",  # tom sida
                "ej-konverterad",  # skanning av brus: OCR finner inga ord
                "ej-konverterad",  # brus med osynligt OCR-lager: läses om
                "ej-konverterad",  # brus med en stämpel i synlig text
                "ok",  # omslag: helsidesbild med mer än 50 synliga tecken
                "ej-konverterad",  # en ritad yta utan tecken
                "tom",  # bara ett streck
                "ocr",  # inskannad blankett
                "ok",  # tabell utan lodräta linjer med rubrikrad
                "tabell-osaker",  # tabell utan lodräta linjer, talen inte i linje
                "ok",  # linjer, men en cell rymmer två tal
                "tabell-osaker",  # en upphöjd fotnotssiffra direkt efter ett tal
                "tabell-osaker",  # linjer, men två priser i en cell
            ],
        )
        self.assertEqual(self.resultat.kvalitet, "delvis")
        self.assertEqual(self.resultat.tal_obekraftade, [5, 6, 7, 9, 11])

    def test_inskannad_blankett_lases_med_ocr(self):
        sida = self.resultat.sidor[10]
        self.assertIn("Ansökan om partistöd", sida.text)
        self.assertIn("Antal mandat i fullmäktige: 4", sida.text)
        self.assertEqual(sida.tabeller, [])

    def test_pipeline_namner_ocr_verktygen(self):
        verktyg = versioner(self.resultat)
        self.assertEqual(
            [v.split()[0] for v in verktyg],
            ["pdfplumber", "pdfminer.six", "pypdfium2", "tesseract"],
        )
        self.assertIn(" swe ", verktyg[-1])

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
        sida = self.resultat.sidor[12]
        self.assertTrue(sida.text.startswith("```osaker-tabell\nIntäkter"))
        self.assertIn("4 078        12", sida.text)
        self.assertEqual(sida.tabeller, [])


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

    def test_mer_an_en_procent_olasliga_tecken_ger_ocr(self):
        def sida(olasliga: int):
            tecken = ["(cid:3)"] * olasliga + ["a"] * (100 - olasliga)
            chars = [{"text": t} for t in tecken]
            return SimpleNamespace(chars=chars, images=[], width=595, height=842)

        self.assertEqual(vag(sida(1), lambda: 1.0), "text")
        self.assertEqual(vag(sida(2), lambda: 1.0), "ocr")
        self.assertEqual(
            vag(
                SimpleNamespace(
                    chars=[{"text": "\ufffd"}] * 2, images=[], width=1, height=1
                ),
                lambda: 1.0,
            ),
            "ocr",
        )


class TestOcrFel(unittest.TestCase):
    def test_tesseract_som_fallerar_marker_bara_sidan(self):
        with mock.patch.object(ocr, "tesseract", return_value=False):
            resultat = konvertera(PDF / "sidor.pdf")
        self.assertEqual(resultat.fel, None)
        self.assertEqual(resultat.kvalitet_per_sida[0], "ok")
        self.assertEqual(resultat.kvalitet_per_sida[10], "ej-konverterad")

    def test_sakerhet_under_troskeln_ger_ingen_text(self):
        sida = pdfium.PdfDocument(PDF / "sidor.pdf")[10]
        with mock.patch.object(ocr, "medelsakerhet", return_value=69.9):
            self.assertIsNone(ocr.las(sida))

    def test_saknad_tesseract_stoppar_innan_nagot_lases(self):
        with mock.patch.dict(os.environ, {"PATH": ""}):
            with self.assertRaises(Konfigurationsfel):
                ocr.kontrollera()
            self.assertEqual(ocr.modellversion(), "okänd")
        with (
            mock.patch.object(ocr, "SPRAK", "finns-inte"),
            self.assertRaises(Konfigurationsfel),
        ):
            ocr.kontrollera()
        ocr.kontrollera()


class TestOcrSakerhet(unittest.TestCase):
    def test_medelvardet_utan_poster_med_minus_ett(self):
        tsv = "level\tconf\ttext\n5\t-1\t\n5\t90\tord\n5\t50\tannat\n5\t-1\tx\n"
        self.assertEqual(medelsakerhet(tsv), 70)

    def test_inga_ord_ger_ingen_sakerhet(self):
        self.assertIsNone(medelsakerhet("level\tconf\ttext\n1\t-1\t\n"))


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
