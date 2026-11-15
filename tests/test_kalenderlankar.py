"""Krav: K56 i docs/02-KRAV.md. Kod: src/kommunhandlingar/webbplats/
kalender.py och kalendervyer.py."""

import tempfile
import unittest
from pathlib import Path

from kommunhandlingar.webbplats import kalender
from kommunhandlingar.webbplats.kalendersida import kalendersida
from kommunhandlingar.webbplats.mall import Mall
from tests.test_kalender import REPO, TID, kommun, pool


class TestSammantradetsSida(unittest.TestCase):
    def test_ett_sammantrade_med_sida_lankas_i_bada_vyerna(self):
        with tempfile.TemporaryDirectory() as tmp, pool() as sammantraden:
            sidan = Path(tmp) / "fsn" / "2027" / "2027-01-14.html"
            sidan.parent.mkdir(parents=True)
            sidan.write_text("", encoding="utf-8")
            sammantraden = kalender.med_sidor(sammantraden, Path(tmp))
        self.assertEqual(
            [s.sida for s in sammantraden], ["fsn/2027/2027-01-14.html", "", ""]
        )
        html = kalendersida(Mall([kommun()], REPO, TID), kommun(), sammantraden)
        ruta = 'href="fsn/2027/2027-01-14.html">FSN 17:00</a>'
        self.assertIn(ruta, html)
        self.assertIn('<a href="fsn/2027/2027-01-14.html">', html)
        self.assertIn('data-organ="fsn-au">FSN-AU</span>', html)
