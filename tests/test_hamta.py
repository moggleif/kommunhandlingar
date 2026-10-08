"""Krav: K4, K6, K8 och K9, ADR-0003 och ADR-0004.
Kod: src/kommunhandlingar/behandla.py, hamta.py, pool.py och skrivning.py."""

import shutil
import tempfile
import unittest
from datetime import UTC, date, datetime
from pathlib import Path

from kommunhandlingar import frontmatter, pool
from kommunhandlingar.behandla import Steg2, behandla
from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.hamta import las_kandidater
from kommunhandlingar.kandidat import Kandidat
from kommunhandlingar.upptack import skriv

PDF = Path(__file__).parent / "fixtures" / "pdf"
TID = datetime(2026, 10, 8, 2, 0, tzinfo=UTC)


class Klient:
    """Lämnar ut fixturen som står för adressen, eller felet."""

    def __init__(self):
        self.filer: dict[str, str] = {}
        self.anrop: list[str] = []

    def fil(self, url: str, mal: Path) -> None:
        self.anrop.append(url)
        if self.filer[url].startswith("fel:"):
            raise Hamtfel(self.filer[url][4:])
        shutil.copy(PDF / self.filer[url], mal)


def kandidat(nyckel: str, url: str, typ: str = "protokoll", filnamn: str = "P.pdf"):
    return Kandidat("ks", date(2025, 4, 22), typ, url, "sida", nyckel, filnamn)


class TestSteg2(unittest.TestCase):
    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.data = Path(katalog.name)
        self.klient = Klient()

    def kor(self, *kandidater: Kandidat) -> list[str]:
        steg = Steg2(
            self.data,
            "exempelby",
            pool.las(self.data, "exempelby"),
            self.klient,
            frozenset(k.kallnyckel for k in kandidater),
            lambda: TID,
            "kommunhandlingar 0.2.0",
        )
        return [behandla(steg, k) for k in kandidater]

    def md(self, namn: str = "protokoll") -> Path:
        return self.data / "exempelby/ks/2025/2025-04-22" / f"{namn}.md"

    def falt(self, namn: str = "protokoll") -> dict[str, str]:
        return frontmatter.las(self.md(namn).read_text(encoding="utf-8"))

    def test_nytt_dokument_med_tabeller(self):
        self.klient.filer["u1"] = "sidor.pdf"
        self.assertEqual(self.kor(kandidat("s:1", "u1")), ["konverterad"])
        falt = self.falt()
        self.assertEqual(falt["kvalitet"], "delvis")
        self.assertEqual(falt["sidor"], "15")
        self.assertEqual(falt["tal_obekraftade"], "[5, 6, 7, 9, 11]")
        self.assertTrue(
            falt["pipeline"].startswith("kommunhandlingar 0.2.0 / pdfplumber ")
        )
        csv = self.md().with_suffix(".tabeller") / "2-1.csv"
        self.assertEqual(
            csv.read_text(), "Post,2027\nIntäkter,4 078\nKostnader,-1 845\n"
        )
        text = self.md().read_text()
        self.assertIn("[Tabell 2-1](protokoll.tabeller/2-1.csv)", text)
        self.assertIn("<!-- sida 11 -->\n\nAnsökan om partistöd", text)
        self.assertEqual(list(self.md().parent.glob("*.tmp")), [])

    def test_samma_adress_hamtas_inte_igen(self):
        self.klient.filer["u1"] = "sidor.pdf"
        self.kor(kandidat("s:1", "u1"))
        fore = self.md().read_text()
        self.assertEqual(self.kor(kandidat("s:1", "u1")), ["oförändrad"])
        self.assertEqual(self.klient.anrop, ["u1"])
        self.assertEqual(self.md().read_text(), fore)

    def test_ny_adress_med_samma_innehall_andrar_bara_adressen(self):
        self.klient.filer |= {
            "u1": "sidor.pdf",
            "u2": "begransad.pdf",
            "u3": "sidor.pdf",
        }
        self.kor(kandidat("s:1", "u1"))
        fore = self.md().read_text()
        self.assertEqual(self.kor(kandidat("s:1", "u3")), ["ny adress, samma innehåll"])
        self.assertEqual(
            self.md().read_text(), fore.replace("kalla_url: u1", "kalla_url: u3")
        )
        self.assertEqual(self.kor(kandidat("s:1", "u2")), ["konverterad"])
        self.assertEqual(self.falt()["kalla_url"], "u2")

    def test_misslyckat_forsok(self):
        self.klient.filer["u1"] = "fel:http-404"
        self.assertEqual(self.kor(kandidat("s:1", "u1")), ["ej hämtad (http-404)"])
        falt = self.falt()
        self.assertEqual(
            (falt["kvalitet"], falt["fel"], falt["sha256"]),
            ("ej-hamtad", "http-404", "null"),
        )
        self.assertEqual(falt["pipeline"], "kommunhandlingar 0.2.0")
        fore = self.md().read_text()
        self.assertEqual(
            self.kor(kandidat("s:1", "u1")), ["ej hämtad (http-404), oförändrad"]
        )
        self.assertEqual(self.md().read_text(), fore)
        self.klient.filer["u1"] = "fel:tomt-svar"
        self.assertEqual(self.kor(kandidat("s:1", "u1")), ["ej hämtad (tomt-svar)"])
        self.assertEqual(self.falt()["hamtad"], falt["hamtad"])
        self.klient.filer["u1"] = "sidor.pdf"
        self.assertEqual(self.kor(kandidat("s:1", "u1")), ["konverterad"])

    def test_misslyckat_forsok_skriver_aldrig_over_en_fullstandig_md(self):
        self.klient.filer |= {"u1": "sidor.pdf", "u2": "fel:http-503"}
        self.kor(kandidat("s:1", "u1"))
        fore = self.md().read_text()
        self.assertEqual(
            self.kor(kandidat("s:1", "u2")),
            ["ej hämtad (http-503), fullständig .md orörd"],
        )
        self.assertEqual(self.md().read_text(), fore)

    def test_tva_dokument_pa_samma_plats_far_namn(self):
        self.klient.filer |= {"u1": "sidor.pdf", "u2": "begransad.pdf"}
        self.kor(
            kandidat("s:1", "u1"), kandidat("s:2", "u2", filnamn="Protokoll § 5.pdf")
        )
        self.assertEqual(self.falt("protokoll-protokoll-5")["namn"], "protokoll-5")

    def test_ny_kallnyckel_pa_platsen_blir_ny_version(self):
        self.klient.filer |= {"u1": "sidor.pdf", "u2": "begransad.pdf"}
        self.kor(kandidat("s:1", "u1"))
        self.assertEqual(self.kor(kandidat("s:2", "u2")), ["konverterad"])
        falt = self.falt()
        self.assertEqual(
            (falt["kallnyckel"], falt["tidigare_kallnycklar"]), ("s:2", "[s:1]")
        )
        self.assertEqual(self.kor(kandidat("s:1", "u1")), ["tidigare källnyckel"])

    def test_tabellkatalogen_ersatts_som_helhet(self):
        self.klient.filer |= {"u1": "sidor.pdf", "u2": "inte.pdf"}
        self.kor(kandidat("s:1", "u1"))
        self.kor(kandidat("s:1", "u2"))
        self.assertFalse(self.md().with_suffix(".tabeller").exists())
        self.assertEqual(self.falt()["fel"], "inte-pdf")
        self.assertEqual(self.falt()["sidor"], "null")

    def test_ny_adress_skriver_om_ej_hamtad(self):
        self.klient.filer |= {"u1": "fel:http-404", "u2": "fel:http-404"}
        self.kor(kandidat("s:1", "u1"))
        self.assertEqual(self.kor(kandidat("s:1", "u2")), ["ej hämtad (http-404)"])
        self.assertEqual(self.falt()["kalla_url"], "u2")

    def test_avbruten_korning_gors_fardig(self):
        self.klient.filer |= {"u1": "sidor.pdf", "u2": "begransad.pdf"}
        self.kor(kandidat("s:1", "u1"))
        katalog = self.md().with_suffix(".tabeller")
        (katalog.parent / "protokoll.tabeller.ny").mkdir()
        (katalog.parent / "protokoll.tabeller.ny" / "9-9.csv").write_text("x\n")
        self.md().with_name("protokoll.md.tmp").write_text("halv")
        self.assertEqual(self.kor(kandidat("s:1", "u2")), ["konverterad"])
        rester = sorted(p.name for p in self.md().parent.iterdir())
        self.assertEqual(rester, ["protokoll.md", "protokoll.tabeller"])
        self.assertEqual(
            sorted(p.name for p in katalog.iterdir()),
            ["12-1.csv", "14-1.csv", "2-1.csv", "3-1.csv"],
        )

    def test_bilaga_har_alltid_namn(self):
        self.klient.filer["u1"] = "sidor.pdf"
        self.kor(kandidat("s:1", "u1", "bilaga", "Bilaga 1 Karta.pdf"))
        self.assertEqual(self.falt("bilaga-bilaga-1-karta")["namn"], "bilaga-1-karta")


class TestKandidatlistan(unittest.TestCase):
    def test_lases_tillbaka(self):
        kandidater = [kandidat("s:1", "u1"), kandidat("s:2", "u2", "kallelse")]
        with tempfile.TemporaryDirectory() as katalog:
            fil = Path(katalog) / "k.json"
            skriv(kandidater, fil)
            self.assertEqual(las_kandidater(fil), kandidater)
