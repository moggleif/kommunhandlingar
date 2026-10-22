"""Krav: K36 i docs/02-KRAV.md, ADR-0057. Kod: src/kommunhandlingar/webbplats/
spar.py, sparslag.py, sparsida.py, sparkort.py, sparikon.py, organsida.py
och bygg.py."""

import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.webbplats import spar
from kommunhandlingar.webbplats.bygg import bygg
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.sparkort import Vy, kalla
from kommunhandlingar.webbplats.sparsida import sparsida
from kommunhandlingar.webbplats.sparslag import LOKALBEHOV
from tests.test_mal import BUDGET, ROT
from tests.test_webbplats import FIXTURER, REPO, TID, dokument, exempelby

RUBRIK = "organ,behov,ar,fas,varde,text,kalla,tolkad\n"
ANDRAS = "bun/2025/2025-06-10/protokoll.md"
NAMNDENS = """<!-- sida 1 -->

Följande behov finns;
\\- Ny idrottshall
\\- Större matsal

<!-- sida 2 -->

Nämnden prioriterar 1. Ny idrottshall
"""
BUDGETENS = """<!-- sida 1 -->

1412 Idrottshall i Exempelby

<!-- sida 2 -->

Projektet har avslutats.
"""
RADER = (
    f"fsn,Idrottshall,2024,lokalbehov,,Ny idrottshall,{BUDGET}#sida-1,\n"
    f"fsn,Idrottshall,2024,prioritet,1,1. Ny idrottshall,{BUDGET}#sida-2,\n"
    f"fsn,Idrottshall,2025,lokalplan,1412,1412 Idrottshall,{ANDRAS}#sida-1,\n"
    f"fsn,Idrottshall,2025,utfort,,Projektet har avslutats.,{ANDRAS}#sida-2,ja\n"
    f"fsn,Matsal,2024,lokalbehov,,Större matsal,{BUDGET}#sida-1,\n"
)


def skriv_pool(data: Path) -> None:
    for fil, text in ((BUDGET, NAMNDENS), (ANDRAS, BUDGETENS)):
        organ, _, datum, _ = fil.split("/")
        (data / fil).parent.mkdir(parents=True)
        (data / fil).write_text(
            dokument(organ, datum, text=text, per_sida="[ok, ok]"), encoding="utf-8"
        )


@contextmanager
def lasta(rader: str = RADER, rubrik: str = RUBRIK):
    """Läser en lokalbehovsfil mot en pool med två organs dokument."""
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(rubrik + rader, encoding="utf-8")
        skriv_pool(data)
        yield spar.las(fil, exempelby(), data, LOKALBEHOV)


class TestLasning(unittest.TestCase):
    def stoppas(self, rader: str, rubrik: str = RUBRIK) -> str:
        with self.assertRaises(Datafel) as fel, lasta(rader, rubrik):
            pass
        return str(fel.exception)

    def test_raderna_lases_med_kallor_fran_andra_organ(self):
        with lasta() as stegen:
            self.assertEqual(len(stegen), 5)
            self.assertEqual(stegen[2].kallans_organ, "bun")
            self.assertEqual(stegen[3].tolkad, "ja")

    def test_fel_som_stoppar(self):
        rad = f"fsn,Idrottshall,2025,lokalplan,1412,1412 Idrottshall,{ANDRAS}#sida-1,\n"
        for andrad, fel in [
            ("fsn,Idrottshall,2025\n", "rad 2: 3 fält"),
            (rad.replace(",2025,", ",25,"), "'25'"),
            (rad.replace("fsn,", "kun,", 1), "'kun'"),
            (rad.replace(",lokalplan,", ",beslut,"), "'beslut'"),
            (rad.replace(",1412,", ",ett,", 1), "inte ett löpnummer"),
            (rad.replace(",Idrottshall,", ",,", 1), "tomma"),
            (rad.replace("1412 Idrottshall,", ",", 1), "tomma"),
            (rad.replace(",\n", ",kanske\n"), "'kanske'"),
            (rad.replace("bun/", "kun/"), "inget organs dokument"),
            (rad.replace("sida-1", "sida-2"), "texten står inte"),
            (rad.replace("#sida-1", ""), "ingen sida"),
            (rad.replace(",1412,", ",1413,", 1), "värdet står inte"),
            (rad + rad, "rad 3: steget står redan"),
        ]:
            self.assertIn(fel, self.stoppas(andrad))
        prioritet = (
            f"fsn,Idrottshall,2024,prioritet,,1. Ny idrottshall,{BUDGET}#sida-2,\n"
        )
        self.assertIn("inte en prioritet", self.stoppas(prioritet))
        self.assertIn("rubrikerna", self.stoppas(RADER, "organ,behov\n"))


class TestSidan(unittest.TestCase):
    def sida(self) -> str:
        with lasta() as stegen:
            vy = Vy.over(LOKALBEHOV, exempelby(), stegen)
            return sparsida(Mall([exempelby()], REPO, TID), vy, stegen)

    def test_ett_behov_per_rad_och_ett_ar_per_kolumn(self):
        html = self.sida()
        self.assertEqual(html.count("<tr data-mal"), 2)
        self.assertEqual(html.count("<article"), 2)
        for ar in ("2024", "2025"):
            self.assertIn(f'<th scope="col">{ar}</th>', html)

    def test_faserna_som_ikoner_som_lankar_till_kallan(self):
        html = self.sida()
        rad = html.split('<tr data-mal="0"')[1].split("</tr>")[0]
        for fas in ("lokalbehov", "prioritet", "lokalplan", "utfort tolkad"):
            self.assertIn(f'class="fas {fas}"', rad)
        self.assertIn('href="../bun/2025/2025-06-10/protokoll.html#sida-1"', rad)
        self.assertIn(">1</text>", rad)
        self.assertIn('<ul class="teckenforklaring">', html)

    def test_kortet_har_historiken_med_text_och_kalla(self):
        html = self.sida()
        kort = html.split('<article id="sak-0"')[1].split("</article>")[0]
        self.assertIn("<h3>Idrottshall</h3>", kort)
        self.assertIn("Senast: utfört 2025", kort)
        self.assertIn("<q>1412 Idrottshall</q>", kort)
        self.assertIn("Senast: utfört 2025 <small>tolkad</small>", kort)

    def test_urvalet_och_sammandraget(self):
        html = self.sida()
        self.assertIn('data-slag="lokalbehov prioritet lokalplan utfort senaste"', html)
        self.assertIn('data-urval="senaste">I lokalbehov 2024', html)
        self.assertIn("<dt>i lokalplanen</dt><dd>1</dd>", html)
        self.assertIn("<script>", html)

    def test_kallan_namnger_organet_och_sidorna(self):
        adress, text = kalla(f"{ANDRAS}#sida-1-2", exempelby())
        self.assertEqual(adress, "../bun/2025/2025-06-10/protokoll.html#sida-1")
        self.assertTrue(text.endswith("protokoll 2025-06-10, sida 1–2"))


class TestBygg(unittest.TestCase):
    def bygg(self, rader: str | None, namn: str = "exempelby") -> Path:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        rot, ut = tmp / "repo", tmp / "ut"
        (rot / "kommuner").mkdir(parents=True)
        shutil.copy(FIXTURER / "exempelby.toml", rot / "kommuner")
        skriv_pool(rot / "data" / "exempelby")
        if rader is not None:
            (rot / "lokalbehov").mkdir()
            (rot / "lokalbehov" / f"{namn}.csv").write_text(
                RUBRIK + rader, encoding="utf-8"
            )
        bygg(rot, ut, REPO, TID)
        return ut / "exempelby"

    def test_sidan_byggs_och_lankas_fran_organets_sida(self):
        ut = self.bygg(RADER)
        self.assertIn("Idrottshall", (ut / "fsn" / "lokalbehov.html").read_text())
        self.assertIn('href="fsn/lokalbehov.html"', (ut / "fsn.html").read_text())
        self.assertNotIn("lokalbehov.html", (ut / "bun.html").read_text())

    def test_fil_utan_kommunfil_stoppar_bygget(self):
        with self.assertRaises(Datafel):
            self.bygg(RADER, namn="exempelbyn")

    def test_utan_fil_ingen_sida(self):
        ut = self.bygg(None)
        self.assertFalse((ut / "fsn" / "lokalbehov.html").exists())


class TestKungsbacka(unittest.TestCase):
    def test_filen_gar_ihop_med_kommunfilen_och_poolen(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        fil = ROT / "lokalbehov" / "kungsbacka.csv"
        stegen = spar.las(fil, kungsbacka, ROT / "data" / "kungsbacka", LOKALBEHOV)
        self.assertEqual({s.organ for s in stegen}, {"ga"})
        self.assertEqual(fil.read_bytes().count(b"\r"), 0)
