"""Krav: K14 i docs/02-KRAV.md. Kod: src/kommunhandlingar/webbplats/mall.py."""

import unittest

from kommunhandlingar.webbplats.mall import STIL


class TestSmalSkarm(unittest.TestCase):
    """K14: sidan rullar aldrig i sidled på en smal skärm."""

    def test_tabellens_ruta_haller_det_som_ligger_absolut_i_tabellen(self):
        # Utan position i rutan räknades de dolda texterna i översiktens celler
        # mot hela sidan, och den blev 1 147 punkter bred på en mobil.
        self.assertIn(".tabell, .sida { overflow-x: auto; position: relative; }", STIL)

    def test_sidfotens_langa_adress_bryts(self):
        sidfot = STIL.split("footer {")[1].split("}")[0]
        self.assertIn("overflow-wrap: anywhere", sidfot)

    def test_rubrikernas_langa_ord_bryts(self):
        # "Byggnadsnämndens" fick inte plats på 320 punkter.
        self.assertIn("h1, h2 { overflow-wrap: break-word; hyphens: auto; }", STIL)
