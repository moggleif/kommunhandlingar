"""Krav: K71 i docs/02-KRAV.md, ADR-0098. Kod:
src/kommunhandlingar/webbplats/mal.py och malstatistik.py."""

import unittest

from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.malsida import malsida
from tests.aren import aren
from tests.test_mal import RADER, pool
from tests.test_webbplats import REPO, TID, exempelby, protokoll

REGIONMAL = RADER.replace("nämndmål", "regionmål")


class TestRegionmal(unittest.TestCase):
    def test_regionmal_ar_ett_slag(self):
        with pool(REGIONMAL) as malen:
            self.assertEqual(malen[0].slag, "regionmål")

    def test_regionmal_heter_regionmal_pa_sidan(self):
        with pool(REGIONMAL) as malen:
            mall = Mall([exempelby()], REPO, TID, aren=aren(malen))
            html = malsida(mall, exempelby(), malen, protokoll(2023, 2025))
        self.assertIn('data-urval="regionmål">Regionmål</button>', html)
        self.assertIn("<dt>regionmål</dt>", html)
        for slag in ("Kommunmål", "kommunmål", "Nämndmål", "nämndmål"):
            self.assertNotIn(f">{slag}<", html)
