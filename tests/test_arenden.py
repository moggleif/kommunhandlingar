"""Krav: K48, ADR-0071. Kod: src/kommunhandlingar/arenden.py, konverteringen i
src/kommunhandlingar/behandla.py och kontrollen i datakontroll.py."""

import unittest
from pathlib import Path
from unittest import mock

from kommunhandlingar import behandla
from kommunhandlingar.arenden import arenden, fyll
from kommunhandlingar.konvertering.dokument import Resultat
from kommunhandlingar.konvertering.las_sida import Sida
from tests.test_datakontroll import Pool
from tests.test_hamta import Steg2Fall, kandidat

PROTOKOLL = "§ 2 Dnr XN-2026-00067\nLokaler\n\n§ 1 Dnr XN-2026-00004\nJusterare\n"
PROTOKOLL += "\n§ 3 Dnr XN-2026-00004\nJusterare igen\n"


class TestArenden(unittest.TestCase):
    def test_sorterade_och_utan_dubbletter(self):
        self.assertEqual(
            arenden("protokoll", PROTOKOLL), ["XN-2026-00004", "XN-2026-00067"]
        )

    def test_paragrafer_utan_diarienummer(self):
        self.assertEqual(arenden("protokoll", "§ 1\nAnmälan av jäv\n"), [])

    def test_inga_paragrafer_eller_inget_protokoll(self):
        self.assertIsNone(arenden("protokoll", "Anteckningar\n"))
        self.assertIsNone(arenden("kallelse", PROTOKOLL))


class TestKonverteringen(Steg2Fall):
    def test_protokollet_far_sina_arenden(self):
        self.klient.filer["u1"] = "sidor.pdf"
        sida = Sida("ok", False, PROTOKOLL)
        with mock.patch.object(
            behandla, "konvertera", return_value=Resultat("full", None, [sida])
        ):
            self.kor(kandidat("s:1", "u1"))
        self.assertEqual(self.falt()["arenden"], "[XN-2026-00004, XN-2026-00067]")


class TestPoolen(Pool):
    DOKUMENT = "exempelby/ks/2025/2025-04-22/protokoll.md"

    def skriv_paragraf(self) -> Path:
        md = self.data / self.DOKUMENT
        md.write_text(md.read_text(encoding="utf-8") + "\n§ 4 Dnr KS-2025-00001\n")
        return md

    def test_kontrollen_hittar_fel_arenden(self):
        self.skriv_paragraf()
        self.assertEqual(
            self.fel(),
            [
                f"{self.DOKUMENT}: arenden borde vara [KS-2025-00001] "
                "(python -m kommunhandlingar.arenden)"
            ],
        )

    def test_kommandot_rattar_bara_raden_och_en_gang(self):
        md = self.skriv_paragraf()
        fore = md.read_text(encoding="utf-8")
        self.assertEqual(fyll(self.data), 1)
        efter = md.read_text(encoding="utf-8")
        vantat = fore.replace("\narenden: null\n", "\narenden: [KS-2025-00001]\n")
        self.assertEqual(efter, vantat)
        self.assertEqual((fyll(self.data), self.fel()), (0, []))


if __name__ == "__main__":
    unittest.main()
