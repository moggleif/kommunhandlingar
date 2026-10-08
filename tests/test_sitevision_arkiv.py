"""Krav: K16 i docs/02-KRAV.md, ADR-0018.
Kod: src/kommunhandlingar/adaptrar/sitevision_arkiv.py."""

import json
import unittest
from dataclasses import replace
from urllib.parse import parse_qs, urlsplit

from kommunhandlingar.adaptrar.sitevision_arkiv import upptack
from kommunhandlingar.adaptrar.wayback import CDX
from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.konfiguration import las
from tests.test_konfiguration import FIXTURER
from tests.test_sitevision import lank, sida

BUN = "https://exempelby.se/bun"
FSN = "https://exempelby.se/fsn"
FILER = ("exempelby.se/download/", "mimetype:application/pdf")


def bild(tid: str, adress: str) -> str:
    return f"https://web.archive.org/web/{tid}id_/{adress}"


def fil(nod: str, version: int, namn: str) -> str:
    return f"https://exempelby.se/download/18.{nod}/{version}/{namn}"


class Klient:
    """CDX-svaren per adress och mimetyp, och ögonblicksbildernas HTML."""

    def __init__(self, cdx: dict, sidor: dict[str, str]):
        self.cdx, self.sidor = cdx, sidor

    def text(self, url: str) -> str:
        if url.startswith(CDX):
            fragan = parse_qs(urlsplit(url).query)
            svar = self.cdx.get((fragan["url"][0], fragan["filter"][1]), [])
            if isinstance(svar, Hamtfel):
                raise svar
            return json.dumps([["timestamp", "original", "length"], *svar])
        if url not in self.sidor:
            raise Hamtfel("http-404")
        return self.sidor[url]


NY_BILD = sida(
    ("2 maj 2022", lank("a1", "Protokoll%202022-05-02.pdf")),
    ("3 maj 2022", lank("a2", "Kallelse%202022-05-03.pdf")),
)
GAMMAL_BILD = sida(
    ("2 maj 2022", lank("a1", "Protokoll%202022-05-09.pdf")),
    ("1 april 2021", lank("a3", "Protokoll%202021-04-01.pdf")),
)
SIDKOPIOR = [
    ["20231201000000", BUN, "10"],
    ["20230101000000", BUN, "10"],
    ["20221115000000", BUN, "10"],
]
FILKOPIOR = [
    ["20220601000000", fil("a1", 1, "P.pdf"), "100"],
    ["20230601000000", fil("a1", 1, "P.pdf"), "900"],
    ["20230701000000", fil("a1", 2, "P.pdf"), "50"],
    ["20230601000000", fil("a2", 1, "K.pdf"), "300"],
    ["20230105000000", fil("a2", 1, "K.pdf"), "300"],
    ["20230105000000", "https://exempelby.se/download/bild.png", "1"],
]


def arkivet() -> Klient:
    """Två ögonblicksbilder av bun, och en fsn som arkivet inte svarar för."""
    cdx = {
        FILER: FILKOPIOR,
        (BUN, "mimetype:text/html"): SIDKOPIOR,
        (FSN, "mimetype:text/html"): Hamtfel("anslutning"),
    }
    sidor = {
        bild("20231201000000", BUN): NY_BILD,
        bild("20221115000000", BUN): GAMMAL_BILD,
    }
    return Klient(cdx, sidor)


class TestArkivetsUpptackt(unittest.TestCase):
    def setUp(self):
        self.kalla = replace(las(FIXTURER / "exempelby.toml").kallor[0], wayback=True)
        self.klient = arkivet()
        self.cdx, self.sidor = self.klient.cdx, self.klient.sidor

    def upptack(self):
        return upptack(self.kalla, self.klient)

    def test_nyaste_versionen_och_storsta_kopian(self):
        kandidater, _, _ = self.upptack()
        adresser = {k.kallnyckel: k.url for k in kandidater}
        self.assertEqual(
            adresser,
            {
                "sitevision:18.a1": bild("20230701000000", fil("a1", 2, "P.pdf")),
                "sitevision:18.a2": bild("20230105000000", fil("a2", 1, "K.pdf")),
            },
        )

    def test_den_nyaste_ogonblicksbilden_galler(self):
        kandidater, _, _ = self.upptack()
        protokoll = next(k for k in kandidater if k.kallnyckel == "sitevision:18.a1")
        self.assertEqual(str(protokoll.datum), "2022-05-02")
        self.assertEqual(protokoll.kalla, bild("20231201000000", BUN))

    def test_fil_utan_kopia_blir_ingen_kandidat(self):
        _, avvisade, _ = self.upptack()
        self.assertEqual(
            [(a.filnamn, a.orsak, a.kalla) for a in avvisade],
            [
                (
                    "Protokoll 2021-04-01.pdf",
                    "ingen kopia i arkivet",
                    bild("20221115000000", BUN),
                )
            ],
        )

    def test_obesvarade_fragor_hoppas_over(self):
        del self.sidor[bild("20221115000000", BUN)]
        kandidater, _, obesvarade = self.upptack()
        self.assertEqual(len(kandidater), 2)
        self.assertEqual(
            obesvarade,
            [
                f"{bild('20221115000000', BUN)}: http-404",
                f"arkivets lista för {FSN}: anslutning",
            ],
        )

    def test_utan_fillistan_blir_det_inga_kandidater(self):
        self.cdx[FILER] = Hamtfel("tidsgrans")
        self.assertEqual(
            self.upptack(),
            ([], [], ["arkivets lista för exempelby.se/download/: tidsgrans"]),
        )

    def test_en_motessida_utan_kopior_noteras(self):
        self.cdx[(FSN, "mimetype:text/html")] = []
        _, _, noteringar = self.upptack()
        self.assertEqual(noteringar, [f"{FSN}: ingen kopia av mötessidan i arkivet"])
