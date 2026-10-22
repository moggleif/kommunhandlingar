"""Krav: K34, ADR-0055.
Kod: src/kommunhandlingar/behandla.py, datakontroll.py och konvertering/ocr.py."""

import unittest
from dataclasses import replace

from kommunhandlingar import frontmatter
from kommunhandlingar.behandla import Steg2
from kommunhandlingar.konvertering.ocr import rensa
from tests.test_datakontroll import DOKUMENT, EJ_HAMTAD, Pool
from tests.test_hamta import Steg2Fall, kandidat


class TestOmkonverteringen(Steg2Fall):
    def steg(self, kandidater, version: str = "kommunhandlingar 0.2.0") -> Steg2:
        return replace(super().steg(kandidater, version), omkonvertera=True)

    def granskat(self) -> str:
        self.klient.filer["u1"] = "sidor.pdf"
        self.kor(kandidat("s:1", "u1"), version="kommunhandlingar 0.1.0")
        _, huvud, kropp = self.md().read_text(encoding="utf-8").split("---\n", 2)
        falt = frontmatter.las(f"---\n{huvud}---\n") | {"granskad": "2026-10-22"}
        text = frontmatter.skriv(falt) + kropp + "\nRättad för hand.\n"
        self.md().write_text(text, encoding="utf-8")
        return text

    def test_granskat_dokument_konverteras_inte_om(self):
        text = self.granskat()
        self.assertEqual(self.kor(kandidat("s:1", "u1")), ["oförändrad"])
        self.assertEqual(self.klient.anrop, ["u1"])
        self.assertEqual(self.md().read_text(encoding="utf-8"), text)

    def test_granskat_dokument_under_ny_adress_behaller_rattningen(self):
        text = self.granskat()
        self.klient.filer["u3"] = "sidor.pdf"
        self.assertEqual(self.kor(kandidat("s:1", "u3")), ["ny adress, samma innehåll"])
        self.assertEqual(
            self.md().read_text(encoding="utf-8"),
            text.replace("kalla_url: u1", "kalla_url: u3"),
        )

    def test_nytt_original_blir_en_ny_version_utan_granskning(self):
        self.granskat()
        self.klient.filer["u2"] = "begransad.pdf"
        self.assertEqual(self.kor(kandidat("s:1", "u2")), ["konverterad"])
        self.assertEqual(self.falt()["granskad"], "null")
        self.assertNotIn("Rättad för hand.", self.md().read_text(encoding="utf-8"))


class TestDatakontrollen(Pool):
    def test_granskad_ocr_sida_far_bekraftade_tal(self):
        self.andra(DOKUMENT, granskad="2026-10-22", tal_obekraftade="[5, 6, 7, 9]")
        self.assertEqual(self.fel(), [])

    def test_granskad_ar_ett_datum(self):
        self.andra(DOKUMENT, granskad="ja")
        self.assertEqual(self.fel(), [f"{DOKUMENT}: granskad 'ja' är inte ÅÅÅÅ-MM-DD"])

    def test_ej_hamtad_ar_aldrig_granskad(self):
        self.andra(EJ_HAMTAD, granskad="2026-10-22")
        self.assertEqual(self.fel(), [f"{EJ_HAMTAD}: granskad ska vara null"])


class TestOcrTexten(unittest.TestCase):
    def test_paragraftecken(self):
        self.assertEqual(rensa("$ 159 Dnr"), "§ 159 Dnr")
        self.assertEqual(rensa("protokollet $159"), "protokollet §159")
        self.assertEqual(rensa("3 $ Områden"), "3 § Områden")
        self.assertEqual(rensa("1-2 $$ Föreskrifternas"), "1-2 §§ Föreskrifternas")

    def test_dollar_utan_siffra_star_kvar(self):
        self.assertEqual(rensa("$ kungsbacka.se"), "$ kungsbacka.se")
        self.assertEqual(rensa("(S$)"), "(S$)")

    def test_punktutfyllnad(self):
        self.assertEqual(
            rensa("Delegeringsbeslut 2026..........sssssersressrerrrrsrererrnn 11"),
            "Delegeringsbeslut 2026 .... 11",
        )
        self.assertEqual(
            rensa("Förvaltningschef informerar (2025) ..ssss.....rr rn rn nn 25"),
            "Förvaltningschef informerar (2025) .... 25",
        )
        self.assertEqual(rensa("Året som gått ........ 3"), "Året som gått .... 3")

    def test_punkter_utan_sidnummer_star_kvar(self):
        rad = "Hon sa.... och sedan gick hon"
        self.assertEqual(rensa(rad), rad)
        self.assertEqual(rensa("men... sedan 5"), "men... sedan 5")
