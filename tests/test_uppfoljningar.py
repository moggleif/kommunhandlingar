"""Krav: K28 i docs/02-KRAV.md, ADR-0046. Kod: src/kommunhandlingar/webbplats/
uppfoljningar.py, malstatistik.py och bygg.py."""

import re
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.webbplats import uppfoljningar
from kommunhandlingar.webbplats.bygg import bygg
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.malsida import malsida
from tests.test_mal import BUDGET, HANDLINGAR, ROT, budget, pool
from tests.test_webbplats import FIXTURER, REPO, TID, exempelby, protokoll

RUBRIK = "organ,datum,paragraf,slag,rubrik,kalla\n"
RADER = (
    f"fsn,2024-05-02,5,uppföljning,Trygga miljöer,{BUDGET}#sida-1\n"
    f"fsn,2024-05-02,6,dragning,Läsfrämjande,{BUDGET}#sida-2\n"
)


@contextmanager
def lasta(rader: str = RADER):
    """Läser en uppföljningsfil mot en pool med mötets protokoll och handlingar."""
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(RUBRIK + rader, encoding="utf-8")
        (data / BUDGET).parent.mkdir(parents=True)
        for dokument in (BUDGET, HANDLINGAR):
            (data / dokument).write_text(budget(), encoding="utf-8")
        yield uppfoljningar.las(fil, exempelby(), data)


class TestLasning(unittest.TestCase):
    def stoppas(self, rader: str) -> str:
        with self.assertRaises(Datafel) as fel, lasta(rader):
            pass
        return str(fel.exception)

    def test_raderna_lases(self):
        with lasta() as rader:
            self.assertEqual([r.slag for r in rader], ["uppföljning", "dragning"])
            self.assertEqual(rader[0].ar, 2024)

    def test_fel_som_stoppar(self):
        rad = f"fsn,2024-05-02,5,uppföljning,Trygga miljöer,{BUDGET}#sida-1\n"
        for andrad, fel in [
            (rad.replace(",5,", ",§ 5,"), "paragrafen"),
            (rad.replace("uppföljning", "beslut"), "'beslut'"),
            (rad.replace("fsn,", "kun,", 1), "'kun'"),
            (rad.replace("2024-05-02,", "2 maj,", 1), "'2 maj'"),
            (rad.replace("2024-05-02,", "2024-13-45,", 1), "'2024-13-45'"),
            (rad.replace(BUDGET, HANDLINGAR), "inte mötets protokoll"),
            (rad.replace("Trygga", "Otrygga"), "rubriken"),
            (rad + rad, "rad 3: paragrafen står redan"),
        ]:
            self.assertIn(fel, self.stoppas(andrad))


class TestTabellen(unittest.TestCase):
    def tabell(self, organets: list[dict]) -> dict[str, list[str]]:
        with pool() as malen, lasta() as uppfoljda:
            mall = Mall(
                [exempelby()], REPO, TID, uppfoljningar={"exempelby": uppfoljda}
            )
            html = malsida(mall, exempelby(), malen, organets)
        tabell = html[html.index('id="antal"') : html.index('id="ar-')]
        rader = re.findall(r'<tr><th scope="row">(\d+)</th>(.*?)</tr>', tabell)
        return {ar: re.findall(r'"tal">(.*?)<', celler) for ar, celler in rader}

    def test_uppfoljningar_och_dragningar_pa_motets_ar(self):
        tal = self.tabell(protokoll(2024, 2025))
        self.assertEqual(tal["2024"][4:], ["1", "1"])
        self.assertEqual(tal["2025"][4:], ["0", "0"])

    def test_ar_utan_protokoll_med_text_ar_tomt(self):
        handlingar = dict(datum="2024-05-02", typ="handlingar", kvalitet="full")
        for organets in (
            protokoll(2024, kvalitet="ej-hamtad"),
            protokoll(2024, kvalitet="ej-konverterad"),
            [handlingar],
        ):
            tal = self.tabell(organets)
            self.assertEqual(tal["2024"][4:], ["–", "–"])
            self.assertEqual(tal["2025"][4:], ["–", "–"])


class TestKungsbacka(unittest.TestCase):
    def test_uppfoljningarna_gar_ihop_med_kommunfilen_och_poolen(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        fil = ROT / "uppfoljningar" / "kungsbacka.csv"
        rader = uppfoljningar.las(fil, kungsbacka, ROT / "data" / "kungsbacka")
        self.assertEqual({r.organ for r in rader}, {"ga"})
        self.assertEqual(fil.read_bytes().count(b"\r"), 0)


class TestBygg(unittest.TestCase):
    def test_uppfoljningsfil_utan_kommunfil_stoppar_bygget(self):
        rot = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (rot / "kommuner").mkdir()
        shutil.copy(FIXTURER / "exempelby.toml", rot / "kommuner")
        (rot / "uppfoljningar").mkdir()
        (rot / "uppfoljningar" / "exempelbyn.csv").write_text(RUBRIK)
        with self.assertRaises(Datafel) as fel:
            bygg(rot, rot / "ut", REPO, TID)
        self.assertIn(
            "uppfoljningar/exempelbyn.csv har ingen kommunfil", str(fel.exception)
        )
