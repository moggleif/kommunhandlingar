"""Krav: K60 i docs/02-KRAV.md, ADR-0086. Kod:
src/kommunhandlingar/webbplats/arspann.py, mall.py, malsida.py,
malstatistik.py och sparkort.py."""

import re
import tempfile
import unittest
from pathlib import Path

from kommunhandlingar.webbplats.arspann import arspann, poolens_ar, radernas_ar
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


def malsidan(aren: dict, dokumentar=(2022, 2024)) -> str:
    with pool(GRUPPER) as malen:
        mall = Mall([exempelby()], REPO, TID, aren=aren)
        return malsida(mall, exempelby(), malen, protokoll(*dokumentar))


class TestSpannet(unittest.TestCase):
    def test_poolens_ar_ar_arskatalogerna(self):
        with tempfile.TemporaryDirectory() as tmp:
            for katalog in ("fsn/2019", "fsn/2020", "bn/2021", "bn/arkiv"):
                (Path(tmp) / katalog).mkdir(parents=True)
            self.assertEqual(sorted(poolens_ar(Path(tmp))), [2019, 2020, 2021])

    def test_spannet_fyller_mellan_forsta_och_sista(self):
        self.assertEqual(arspann([2026, 2019]), range(2019, 2027))
        self.assertEqual(arspann([2019, 2026, 2027]), range(2019, 2028))

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

    def test_rutan_galler_och_forvalet_ar_malens_senaste_ar(self):
        html = malsidan({"exempelby": range(2018, 2028)})
        self.assertIn('<div class="ruta"><h3>2026</h3>', html)
        self.assertIn('<tr><th scope="row">2027</th><td class="tal">–</td>', html)
        self.assertIn('data-forval="2026"', html)
        self.assertIn('data-urval="aktiv">Gäller 2026', html)
        self.assertIn(
            'class="urval" role="group" aria-label="Visa" data-sista="2026"', html
        )

    def test_malens_forsta_ar_ar_det_forsta_i_ett_ar_i_taget(self):
        html = malsidan(KOMMUNENS, range(2018, 2027))
        aret = html.split('<section class="aret" data-ar="2022">')[1]
        self.assertIn("Det första året med mål på sidan.", aret.split("</section>")[0])
        self.assertNotIn("<span>nytt</span>", aret.split("</section>")[0])

    def test_sparsidan_visar_kommunens_ar(self):
        mall = Mall([exempelby()], REPO, TID, aren=KOMMUNENS)
        stegen = steg()
        html = sparsida(mall, Vy(REDOVISNINGAR, exempelby(), range(2018, 2027)), stegen)
        aren = [ar for _, ar in kolumner(html)]
        self.assertEqual(aren, [str(a) for a in range(2018, 2027)])
