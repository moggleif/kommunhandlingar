"""Krav: K22 i docs/02-KRAV.md, ADR-0032. Kod: src/kommunhandlingar/webbplats/
kalender.py, kalenderfarger.py, kalendervyer.py och kalendersida.py."""

import re
import shutil
import tempfile
import tomllib
import unittest
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.konfiguration import tolka
from kommunhandlingar.webbplats import kalender
from kommunhandlingar.webbplats.bygg import bygg
from kommunhandlingar.webbplats.kalenderfarger import farger
from kommunhandlingar.webbplats.kalendersida import kalendersida
from kommunhandlingar.webbplats.mall import Mall

FIXTURER = Path(__file__).parent / "fixtures"
ROT = Path(__file__).parent.parent
REPO = "https://github.com/exempel/kommunhandlingar"
TID = datetime(2026, 10, 7, 20, 15, tzinfo=UTC)
RUBRIK = "organ,datum,tid,plats,kalla,osakert\n"
PROTOKOLL = "fsn/2026/2026-09-17/protokoll.md"
RADER = (
    f"fsn,2027-01-14,17:00,Stadshuset,{PROTOKOLL},\n"
    f"fsn-au,2027-01-14,,,{PROTOKOLL},\n"
    "bun,2026-12-05,,,https://exempelby.se/bun,Källan säger lördag <5 dec>.\n"
)


def kommun():
    with (FIXTURER / "exempelby.toml").open("rb") as fil:
        data = tomllib.load(fil)
    data["organ"].append(
        {"id": "fsn-au", "namn": ["Arbetsutskottet"], "hor_till": "fsn"}
    )
    return tolka("exempelby", data)


@contextmanager
def pool(rader: str = RADER, rubrik: str = RUBRIK):
    """Läser en kalenderfil mot en pool med protokollet, i en temporär katalog."""
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(rubrik + rader, encoding="utf-8")
        (data / PROTOKOLL).parent.mkdir(parents=True)
        (data / PROTOKOLL).write_text("---\n---\n", encoding="utf-8")
        yield kalender.las(fil, kommun(), data)


class TestLasning(unittest.TestCase):
    def test_raderna_lases(self):
        with pool() as sammantraden:
            self.assertEqual(len(sammantraden), 3)
            self.assertEqual(sammantraden[0].tid, "17:00")
            self.assertEqual(sammantraden[2].osakert, "Källan säger lördag <5 dec>.")

    def stoppas(self, rader: str, rubrik: str = RUBRIK) -> str:
        with self.assertRaises(Datafel) as fel, pool(rader, rubrik):
            pass
        return str(fel.exception)

    def test_fel_rubriker(self):
        self.assertIn("rubrikerna", self.stoppas(RADER, "organ,datum\n"))

    def test_okant_organ(self):
        fel = self.stoppas(f"kun,2027-01-14,,,{PROTOKOLL},\n")
        self.assertIn("rad 2", fel)
        self.assertIn("'kun'", fel)

    def test_datum_som_inte_finns(self):
        self.assertIn("rad 2", self.stoppas(f"fsn,2027-02-30,,,{PROTOKOLL},\n"))

    def test_samma_organ_samma_dag(self):
        fel = self.stoppas(RADER + f"fsn,2027-01-14,,,{PROTOKOLL},\n")
        self.assertIn("rad 5", fel)

    def test_kalla_som_inte_ar_ett_dokument_i_poolen(self):
        for kalla in ("fsn/2027/protokoll.md", "fsn/2026/2026-09-17/saknas.md"):
            fel = self.stoppas(f"fsn,2027-01-14,,,{kalla},\n")
            self.assertIn("inget dokument i poolen", fel)

    def test_datum_i_annan_form(self):
        self.assertIn("ÅÅÅÅ-MM-DD", self.stoppas(f"fsn,20270114,,,{PROTOKOLL},\n"))

    def test_helgdag_som_inte_ar_markt(self):
        fel = self.stoppas("bun,2026-12-05,,,https://exempelby.se/bun,\n")
        self.assertIn("lördag eller söndag", fel)

    def test_fel_antal_falt(self):
        self.assertIn("rad 2", self.stoppas("fsn,2027-01-14\n"))


class TestFarger(unittest.TestCase):
    def test_utskottet_far_namndens_farg_ljusare(self):
        farg = farger(kommun(), {"bun", "fsn", "fsn-au"})
        ton = {o: re.findall(r"hsl\((\d+) \d+% (\d+)%\)", farg[o][0])[0] for o in farg}
        self.assertEqual(ton["fsn"][0], ton["fsn-au"][0])
        self.assertGreater(int(ton["fsn-au"][1]), int(ton["fsn"][1]))
        self.assertEqual(farg["fsn"][1], farg["fsn-au"][1])
        self.assertNotEqual(ton["bun"][0], ton["fsn"][0])

    def test_bara_organ_i_kalendern(self):
        self.assertEqual(list(farger(kommun(), {"fsn"})), ["fsn"])


class TestSidan(unittest.TestCase):
    def setUp(self):
        with pool() as sammantraden:
            self.html = kalendersida(
                Mall([kommun()], REPO, TID), kommun(), sammantraden
            )

    def test_en_ruta_per_sammantrade_med_forkortning(self):
        self.assertIn('data-organ="fsn">FSN 17:00</span>', self.html)
        self.assertIn('data-organ="fsn-au">FSN-AU</span>', self.html)

    def test_osakert_mark_i_text_och_skalet_i_listan(self):
        self.assertIn("ruta o-bun osakert", self.html)
        self.assertIn(">BUN ?</span>", self.html)
        self.assertIn("Osäkert: Källan säger lördag &lt;5 dec&gt;.", self.html)

    def test_alla_manader_och_rader_star_i_sidan(self):
        self.assertIn('data-manad="2026-12"', self.html)
        self.assertIn('data-manad="2027-01"', self.html)
        self.assertEqual(self.html.count('class="manad"'), 2)
        self.assertEqual(self.html.count("<tr data-organ="), 3)

    def test_kallan_ar_en_lank(self):
        self.assertIn(
            'href="fsn/2026/2026-09-17/protokoll.html">FSN 2026-09-17', self.html
        )
        self.assertIn('href="https://exempelby.se/bun">exempelby.se</a>', self.html)

    def test_tid_plats_och_urval(self):
        self.assertIn("<td>17:00</td><td>Stadshuset</td>", self.html)
        self.assertEqual(self.html.count('type="checkbox" checked'), 3)
        self.assertIn("<script>", self.html)

    def test_manad_utan_sammantraden_far_en_tabell(self):
        with pool(f"fsn,2027-03-10,,,{PROTOKOLL},\n" + RADER) as sammantraden:
            html = kalendersida(Mall([kommun()], REPO, TID), kommun(), sammantraden)
        self.assertIn('data-manad="2027-02"', html)
        self.assertEqual(html.count('class="manad"'), 4)


class TestBygg(unittest.TestCase):
    def bygg(self, med_kalender: bool, namn: str = "exempelby") -> Path:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        rot, ut = tmp / "repo", tmp / "ut"
        (rot / "kommuner").mkdir(parents=True)
        shutil.copy(FIXTURER / "exempelby.toml", rot / "kommuner")
        if med_kalender:
            (rot / "kalender").mkdir()
            rad = "bun,2026-12-07,,,https://exempelby.se/bun,\n"
            (rot / "kalender" / f"{namn}.csv").write_text(RUBRIK + rad)
        bygg(rot, ut, REPO, TID)
        return ut

    def test_kalendern_byggs_och_lankas_fran_statussidan(self):
        ut = self.bygg(med_kalender=True)
        self.assertIn("BUN", (ut / "exempelby" / "kalender.html").read_text())
        self.assertIn(
            'href="exempelby/kalender.html"', (ut / "exempelby.html").read_text()
        )

    def test_kalenderfil_utan_kommunfil_stoppar_bygget(self):
        with self.assertRaises(Datafel):
            self.bygg(med_kalender=True, namn="exempelbyn")

    def test_utan_kalenderfil_ingen_sida(self):
        ut = self.bygg(med_kalender=False)
        self.assertFalse((ut / "exempelby" / "kalender.html").exists())
        self.assertNotIn("kalender.html", (ut / "exempelby.html").read_text())


class TestKungsbacka(unittest.TestCase):
    def test_filen_gar_ihop_med_kommunfilen_och_poolen(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        fil = ROT / "kalender" / "kungsbacka.csv"
        sammantraden = kalender.las(fil, kungsbacka, ROT / "data" / "kungsbacka")
        self.assertNotIn("revision", {s.organ for s in sammantraden})
        self.assertEqual(fil.read_bytes().count(b"\r"), 0)
