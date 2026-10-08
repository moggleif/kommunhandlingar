"""Krav: K2, K13 och K16, ADR-0013 och ADR-0018.
Kod: src/kommunhandlingar/upptack.py."""

import argparse
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path

from kommunhandlingar.fel import Hamtfel, Konfigurationsfel
from kommunhandlingar.konfiguration import las
from kommunhandlingar.tidsbudget import Tidsgrans
from kommunhandlingar.upptack import (
    main,
    sammanfattning,
    skriv,
    upptack,
    upptack_arkiv,
    utanfor_repot,
)
from tests.test_konfiguration import FIXTURER, ROT
from tests.test_sitevision import lank, sida
from tests.test_sitevision_arkiv import arkivet


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


class TestArkivet(unittest.TestCase):
    def setUp(self):
        exempelby = las(FIXTURER / "exempelby.toml")
        self.utan_arkiv = exempelby
        kalla = replace(exempelby.kallor[0], wayback=True)
        self.kommun = replace(exempelby, kallor=(kalla,))

    def test_utan_arkiv_i_konfigurationen_fragas_inget(self):
        self.assertEqual(upptack_arkiv(self.utan_arkiv, Klient({}), None), ([], [], []))

    def test_arkivets_lista_nyast_forst(self):
        kandidater, _, noteringar = upptack_arkiv(self.kommun, arkivet(), None)
        self.assertEqual(
            [str(k.datum) for k in kandidater], ["2022-05-03", "2022-05-02"]
        )
        self.assertEqual(
            noteringar, ["arkivets lista för https://exempelby.se/fsn: anslutning"]
        )

    def test_noteringarna_star_i_sammanfattningen(self):
        text = sammanfattning(self.kommun, [], [], ["https://a: anslutning"])
        self.assertIn("\nArkivet: https://a: anslutning", text)

    def test_den_harda_gransen_ger_en_tom_lista(self):
        class Avbryter:
            def text(self, url):
                raise Tidsgrans

        resultat = upptack_arkiv(self.kommun, Avbryter(), datetime.now(UTC))
        self.assertEqual(resultat, ([], [], ["avbrutet vid tidsbudgetens hårda gräns"]))

    def test_arkivet_fragas_inte_efter_den_mjuka_gransen(self):
        with tempfile.TemporaryDirectory() as katalog:
            arg = argparse.Namespace(
                kommunfil=ROT / "kommuner" / "kungsbacka.toml",
                arbetskatalog=Path(katalog),
                arkiv=True,
                start=datetime(2026, 1, 1, tzinfo=UTC),
            )
            with redirect_stdout(StringIO()) as utskrift:
                main(arg)
            lista = Path(katalog) / "kungsbacka.arkiv.kandidater.json"
            self.assertEqual(json.loads(lista.read_text("utf-8")), [])
        self.assertIn(
            "Arkivet: väntar på nästa körning; tidsbudgeten är slut",
            utskrift.getvalue(),
        )
