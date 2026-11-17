"""Krav: K60 i docs/02-KRAV.md, ADR-0086. Kod:
src/kommunhandlingar/webbplats/arspann.py, mall.py, malsida.py,
malstatistik.py och sparkort.py."""

import re
import tempfile
import unittest
from pathlib import Path

from kommunhandlingar.webbplats.arspann import arspann, radernas_ar
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.malsida import malsida
from kommunhandlingar.webbplats.sparkort import Vy
from kommunhandlingar.webbplats.sparsida import sparsida
from kommunhandlingar.webbplats.sparslag import REDOVISNINGAR
from tests.test_mal import pool
from tests.test_malkort import GRUPPER
from tests.test_redovisningar import steg
from tests.test_webbplats import REPO, TID, exempelby, protokoll

KOMMUNENS = {"exempelby": range(2018, 2027)}


def kolumner(html: str) -> list[str]:
    tidslinje = html.split('<h2 id="tidslinje">')[1].split("</thead>")[0]
    return re.findall(r'<th scope="col"( class="lucka")?>(\d{4})', tidslinje)


def malsidan(aren: dict) -> str:
    with pool(GRUPPER) as malen:
        mall = Mall([exempelby()], REPO, TID, aren=aren)
        return malsida(mall, exempelby(), malen, protokoll(2022, 2024))


class TestSpannet(unittest.TestCase):
    def test_fran_poolens_forsta_ar_till_byggaret(self):
        with tempfile.TemporaryDirectory() as tmp:
            for katalog in ("fsn/2019", "fsn/2020", "bn/2021"):
                (Path(tmp) / katalog).mkdir(parents=True)
            self.assertEqual(arspann(Path(tmp), [], 2026), range(2019, 2027))
            self.assertEqual(arspann(Path(tmp), [2027], 2026), range(2019, 2028))

    def test_radernas_ar_ur_mal_uppfoljningar_och_spar(self):
        class Rad:
            def __init__(self, ar):
                self.ar = ar

        aren = radernas_ar(
            "exempelby",
            {"exempelby": [Rad(2017)], "annan": [Rad(2001)]},
            {"exempelby": [Rad(2020)]},
            {"initiativ": {"exempelby": [Rad(2010)]}},
        )
        self.assertEqual(sorted(aren), [2010, 2017, 2020])

    def test_sidans_egna_ar_ryms_alltid(self):
        mall = Mall([exempelby()], REPO, TID, aren=KOMMUNENS)
        self.assertEqual(mall.arspann("exempelby", [2022]), range(2018, 2027))
        self.assertEqual(mall.arspann("exempelby", [2015, 2028]), range(2015, 2029))


class TestSidorna(unittest.TestCase):
    def test_malsidan_visar_kommunens_ar(self):
        aren = [ar for _, ar in kolumner(malsidan(KOMMUNENS))]
        self.assertEqual(aren, [str(a) for a in range(2018, 2027)])

    def test_ar_utan_dokument_fore_byggaret_ar_luckor(self):
        luckor = [ar for lucka, ar in kolumner(malsidan(KOMMUNENS)) if lucka]
        self.assertEqual(luckor, ["2018", "2019", "2020", "2021", "2023"])

    def test_ett_ar_efter_byggaret_ar_ingen_lucka(self):
        html = malsidan({"exempelby": range(2018, 2028)})
        self.assertEqual(kolumner(html)[-1], ("", "2027"))
        self.assertIn('<th scope="col">2027<br><small>inga mål</small></th>', html)

    def test_rutan_galler_malens_senaste_ar(self):
        html = malsidan({"exempelby": range(2018, 2028)})
        self.assertIn('<div class="ruta"><h3>2026</h3>', html)
        self.assertIn('<tr><th scope="row">2027</th><td class="tal">–</td>', html)

    def test_sparsidan_visar_kommunens_ar(self):
        mall = Mall([exempelby()], REPO, TID, aren=KOMMUNENS)
        stegen = steg()
        html = sparsida(mall, Vy.over(mall, REDOVISNINGAR, exempelby(), stegen), stegen)
        aren = [ar for _, ar in kolumner(html)]
        self.assertEqual(aren, [str(a) for a in range(2018, 2027)])
