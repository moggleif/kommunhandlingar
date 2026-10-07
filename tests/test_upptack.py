"""Krav: K2 och K13, ADR-0013. Kod: src/kommunhandlingar/upptack.py."""

import json
import tempfile
import unittest
from pathlib import Path

from kommunhandlingar.fel import Hamtfel, Konfigurationsfel
from kommunhandlingar.konfiguration import las
from kommunhandlingar.upptack import sammanfattning, skriv, upptack, utanfor_repot
from tests.test_konfiguration import FIXTURER, ROT
from tests.test_sitevision import lank, sida


class Klient:
    def __init__(self, sidor: dict[str, str]):
        self.sidor = sidor

    def text(self, url: str) -> str:
        if url not in self.sidor:
            raise Hamtfel("http-404")
        return self.sidor[url]


BUN = sida(
    ("3 maj 2022", lank("b1", "Kallelse%202022-05-03.pdf")),
    ("2 maj 2022", lank("b2", "Protokoll%202022-05-02.pdf")),
    ("4 maj 2022", lank("b3", "Budget%202022.pdf")),
)
FSN = sida(("1 mars 2023", lank("f1", "Protokoll%202023-03-01.pdf")))


class TestUpptack(unittest.TestCase):
    def setUp(self):
        self.kommun = las(FIXTURER / "exempelby.toml")

    def test_kandidaterna_ordnas_och_avvisade_syns(self):
        klient = Klient(
            {"https://exempelby.se/bun": BUN, "https://exempelby.se/fsn": FSN}
        )
        kandidater, avvisade = upptack(self.kommun, klient)
        self.assertEqual([k.kallnyckel[-2:] for k in kandidater], ["b2", "b1", "f1"])
        text = sammanfattning(self.kommun, kandidater, avvisade)
        self.assertIn("3 kandidater, 1 filer utan kandidat", text)
        self.assertIn("  bun: 2", text)
        self.assertIn("Budget 2022.pdf (inget mönster matchar)", text)

    def test_en_sida_som_inte_gar_att_hamta_stoppar(self):
        klient = Klient({"https://exempelby.se/bun": BUN})
        with self.assertRaisesRegex(Hamtfel, "https://exempelby.se/fsn: http-404"):
            upptack(self.kommun, klient)

    def test_kandidatlistan_som_json(self):
        klient = Klient(
            {"https://exempelby.se/bun": BUN, "https://exempelby.se/fsn": FSN}
        )
        kandidater, _ = upptack(self.kommun, klient)
        with tempfile.TemporaryDirectory() as katalog:
            fil = Path(katalog) / "exempelby.kandidater.json"
            skriv(kandidater, fil)
            poster = json.loads(fil.read_text("utf-8"))
        self.assertEqual(len(poster), 3)
        self.assertEqual(poster[0]["datum"], "2022-05-02")
        self.assertEqual(poster[0]["filnamn"], "Protokoll 2022-05-02.pdf")
        self.assertEqual(
            set(poster[0]),
            {"organ", "datum", "typ", "url", "kalla", "kallnyckel", "filnamn"},
        )

    def test_arbetskatalogen_ligger_utanfor_repot(self):
        with self.assertRaisesRegex(Konfigurationsfel, "ligger i repot"):
            utanfor_repot(ROT / "arbete", ROT)
        with tempfile.TemporaryDirectory() as katalog:
            self.assertEqual(utanfor_repot(Path(katalog), ROT), Path(katalog))
