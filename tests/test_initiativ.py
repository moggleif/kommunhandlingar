"""Krav: K37 i docs/02-KRAV.md, ADR-0058. Kod: src/kommunhandlingar/webbplats/
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
from kommunhandlingar.webbplats.sparkort import Vy
from kommunhandlingar.webbplats.sparsida import sparsida
from kommunhandlingar.webbplats.sparslag import INITIATIV
from tests.test_mal import ROT
from tests.test_webbplats import FIXTURER, REPO, TID, dokument, exempelby

RUBRIK = "organ,arende,ar,fas,varde,text,kalla,tolkad\n"
VACKT = "fsn/2024/2024-03-14/protokoll.md"
BESLUT = "fsn/2025/2025-01-20/protokoll.md"
ANDRAS = "bun/2025/2025-09-01/protokoll.md"
VACKTS = """<!-- sida 1 -->

Initiativärende (S) Längre öppettider. Ärendet remitteras.

<!-- sida 2 -->

Alliansen väcker ett initiativärende om simskola.
"""
BESLUTETS = """<!-- sida 1 -->

Nämnden beslutar att avslå initiativärendet om öppettider.
Nämnden beslutar att bifalla initiativet om simskola.
"""
ANDRAS_TEXT = """<!-- sida 1 -->

Simskolan har startat.
"""
RADER = (
    f"fsn,Öppettider,2024,vackt,S,Initiativärende (S),{VACKT}#sida-1,\n"
    f"fsn,Öppettider,2024,beredning,,Ärendet remitteras.,{VACKT}#sida-1,\n"
    f"fsn,Öppettider,2025,avslag,,beslutar att avslå,{BESLUT}#sida-1,\n"
    f"fsn,Simskola,2024,vackt,Alliansen,väcker ett initiativärende,{VACKT}#sida-2,\n"
    f"fsn,Simskola,2025,bifall,,beslutar att bifalla,{BESLUT}#sida-1,\n"
    f"fsn,Simskola,2025,genomfort,,Simskolan har startat.,{ANDRAS}#sida-1,ja\n"
)


def skriv_pool(data: Path) -> None:
    for fil, text in ((VACKT, VACKTS), (BESLUT, BESLUTETS), (ANDRAS, ANDRAS_TEXT)):
        organ, _, datum, _ = fil.split("/")
        (data / fil).parent.mkdir(parents=True)
        (data / fil).write_text(
            dokument(organ, datum, text=text, per_sida="[ok, ok]"), encoding="utf-8"
        )


@contextmanager
def lasta(rader: str = RADER, rubrik: str = RUBRIK):
    """Läser en initiativfil mot en pool med två organs dokument."""
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(rubrik + rader, encoding="utf-8")
        skriv_pool(data)
        yield spar.las(fil, exempelby(), data, INITIATIV)


class TestLasning(unittest.TestCase):
    def stoppas(self, rader: str, rubrik: str = RUBRIK) -> str:
        with self.assertRaises(Datafel) as fel, lasta(rader, rubrik):
            pass
        return str(fel.exception)

    def test_raderna_lases_med_avsandaren_som_varde(self):
        with lasta() as stegen:
            self.assertEqual(len(stegen), 6)
            self.assertEqual(stegen[3].varde, "Alliansen")
            self.assertEqual(stegen[5].kallans_organ, "bun")

    def test_fel_som_stoppar(self):
        rad = f"fsn,Öppettider,2024,vackt,S,Initiativärende (S),{VACKT}#sida-1,\n"
        for andrad, fel in [
            (rad.replace(",S,", ",,"), "inte en avsändare"),
            (rad.replace(",S,", ",KD,"), "värdet står inte"),
            (rad.replace(",vackt,", ",beslut,"), "'beslut'"),
            (rad.replace(",Öppettider,", ",,"), "arende och texten"),
        ]:
            self.assertIn(fel, self.stoppas(andrad))
        self.assertIn("organ,arende", self.stoppas(RADER, "organ,behov\n"))


class TestSidan(unittest.TestCase):
    def sida(self) -> str:
        with lasta() as stegen:
            vy = Vy.over(INITIATIV, exempelby(), stegen)
            return sparsida(Mall([exempelby()], REPO, TID), vy, stegen)

    def test_ett_arende_per_rad_med_avsandaren(self):
        html = self.sida()
        self.assertEqual(html.count("<tr data-mal"), 2)
        rad = html.split('<tr data-mal="0"')[1].split("</tr>")[0]
        self.assertIn(">Öppettider</a> <small>S</small></th>", rad)
        for fas in ("vackt", "beredning", "avslag"):
            self.assertIn(f'class="fas {fas}"', rad)
        self.assertIn('class="fas genomfort tolkad"', html)

    def test_urval_och_sammandrag_per_avsandare(self):
        html = self.sida()
        self.assertIn('data-slag="vackt beredning avslag av-s"', html)
        self.assertIn('data-urval="av-alliansen">Alliansen</button>', html)
        self.assertIn('data-urval="bifall">Bifall</button>', html)
        self.assertNotIn('data-urval="senaste"', html)
        self.assertIn("<h3>Ärenden per avsändare</h3>", html)
        self.assertIn("<dt>S</dt><dd>1</dd>", html)
        self.assertIn("<dt>bifall</dt><dd>1</dd>", html)

    def test_kortet_namnger_avsandaren(self):
        kort = self.sida().split('<article id="sak-1"')[1].split("</article>")[0]
        self.assertIn("<span>2024–2025</span><span>Alliansen</span>", kort)
        self.assertIn("Senast: genomfört 2025 <small>tolkad</small>", kort)
        self.assertIn('href="../bun/2025/2025-09-01/protokoll.html#sida-1"', kort)


class TestBygg(unittest.TestCase):
    def test_sidan_byggs_och_lankas_fran_organets_sida(self):
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        rot, ut = tmp / "repo", tmp / "ut"
        (rot / "kommuner").mkdir(parents=True)
        shutil.copy(FIXTURER / "exempelby.toml", rot / "kommuner")
        skriv_pool(rot / "data" / "exempelby")
        (rot / "initiativ").mkdir()
        (rot / "initiativ" / "exempelby.csv").write_text(RUBRIK + RADER)
        bygg(rot, ut, REPO, TID)
        sidan = ut / "exempelby" / "fsn" / "initiativ.html"
        self.assertIn("Initiativärenden – ", sidan.read_text())
        lank = 'href="fsn/initiativ.html">Initiativärenden över tid'
        self.assertIn(lank, (ut / "exempelby" / "fsn.html").read_text())
        self.assertFalse((ut / "exempelby" / "fsn" / "lokalbehov.html").exists())


class TestKungsbacka(unittest.TestCase):
    def test_filen_gar_ihop_med_kommunfilen_och_poolen(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        fil = ROT / "initiativ" / "kungsbacka.csv"
        stegen = spar.las(fil, kungsbacka, ROT / "data" / "kungsbacka", INITIATIV)
        self.assertEqual({s.organ for s in stegen}, {"ga"})
        self.assertTrue(all(s.varde for s in stegen if s.fas == "vackt"))
        self.assertEqual(fil.read_bytes().count(b"\r"), 0)
