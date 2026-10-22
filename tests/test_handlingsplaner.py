"""Krav: K38 i docs/02-KRAV.md, ADR-0059. Kod: src/kommunhandlingar/webbplats/
spar.py, sparslag.py, sparsida.py, sparkort.py och bygg.py."""

import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.webbplats import spar
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.sparkort import Vy
from kommunhandlingar.webbplats.sparsida import sparsida
from kommunhandlingar.webbplats.sparslag import HANDLINGSPLANER
from tests.test_mal import ROT
from tests.test_webbplats import REPO, TID, dokument, exempelby

RUBRIK = "organ,plan,ar,fas,varde,text,kalla,tolkad\n"
HANDLINGAR = "fsn/2024/2024-03-14/handlingar.md"
PROTOKOLL = "fsn/2024/2024-03-14/protokoll.md"
HANDLINGARNAS = """<!-- sida 1 -->

Motion (S) om en plan för simskolan.

<!-- sida 2 -->

HANDLINGSPLAN Simskolan
"""
PROTOKOLLETS = """<!-- sida 1 -->

Nämnden godkänner handlingsplanen för simskolan.
Nämnden ger uppdrag att ta fram en plan för öppettider.
"""
RADER = (
    f"fsn,Simskolan,2024,uppdrag,S,Motion (S),{HANDLINGAR}#sida-1,\n"
    f"fsn,Simskolan,2024,plan,,HANDLINGSPLAN Simskolan,{HANDLINGAR}#sida-2,\n"
    f"fsn,Simskolan,2024,antagen,Nämnden,godkänner,{PROTOKOLL}#sida-1,\n"
    f"fsn,Öppettider,2024,uppdrag,,ger uppdrag att ta fram,{PROTOKOLL}#sida-1,\n"
)


@contextmanager
def lasta():
    """Läser en fil med handlingsplaner mot en pool med två dokument."""
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(RUBRIK + RADER, encoding="utf-8")
        for dok, text in ((HANDLINGAR, HANDLINGARNAS), (PROTOKOLL, PROTOKOLLETS)):
            organ, _, datum, _ = dok.split("/")
            (data / dok).parent.mkdir(parents=True, exist_ok=True)
            (data / dok).write_text(
                dokument(organ, datum, text=text, per_sida="[ok, ok]"),
                encoding="utf-8",
            )
        yield spar.las(fil, exempelby(), data, HANDLINGSPLANER)


class TestSidan(unittest.TestCase):
    def sida(self) -> str:
        with lasta() as stegen:
            vy = Vy.over(HANDLINGSPLANER, exempelby(), stegen)
            return sparsida(Mall([exempelby()], REPO, TID), vy, stegen)

    def test_en_plan_utan_avsandare_far_ingen(self):
        html = self.sida()
        self.assertIn(">Öppettider</a></th>", html)
        self.assertIn("<dt>S</dt><dd>1</dd>", html)
        self.assertNotIn("<dt></dt>", html)

    def test_kortet_lankar_till_sjalva_planen(self):
        kort = self.sida().split('<article id="sak-0"')[1].split("</article>")[0]
        self.assertIn(
            '<p>Planen: <a href="../fsn/2024/2024-03-14/handlingar.html#sida-2">',
            kort,
        )
        utan = self.sida().split('<article id="sak-1"')[1].split("</article>")[0]
        self.assertNotIn("Planen:", utan)

    def test_historiken_och_kallorna_under_las_mer(self):
        self.assertIn("<summary>Läs mer: historiken och källorna, 3 steg", self.sida())


class TestKungsbacka(unittest.TestCase):
    def test_filen_gar_ihop_med_kommunfilen_och_poolen(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        fil = ROT / "handlingsplaner" / "kungsbacka.csv"
        stegen = spar.las(fil, kungsbacka, ROT / "data" / "kungsbacka", HANDLINGSPLANER)
        self.assertEqual({s.organ for s in stegen}, {"ga"})
        self.assertEqual(fil.read_bytes().count(b"\r"), 0)
