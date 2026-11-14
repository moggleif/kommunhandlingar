"""Krav: K51 i docs/02-KRAV.md, ADR-0074. Kod: src/kommunhandlingar/webbplats/
mall.py, tema.js och stilarna i samma katalog."""

import re
import unittest
from pathlib import Path

from kommunhandlingar import webbplats
from kommunhandlingar.webbplats import sidor
from kommunhandlingar.webbplats.mall import Mall
from tests.test_webbplats import REPO, TID, exempelby

KATALOG = Path(webbplats.__file__).parent
FARG = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b")


class TestTemat(unittest.TestCase):
    def test_varje_sida_har_knappen_och_skriptet_i_head(self):
        html = sidor.startsida(Mall([exempelby()], REPO, TID))
        head = html.split("</head>")[0]
        self.assertIn("localStorage", head)
        self.assertIn("color-scheme: light dark", head)
        self.assertIn(
            '<button type="button" class="tema" hidden>Mörkt tema</button>', html
        )

    def test_farger_bara_i_variablerna(self):
        rader = [
            (fil.name, rad)
            for fil in sorted(KATALOG.glob("*.[cjp][sy]*"))
            for rad in fil.read_text(encoding="utf-8").splitlines()
            if FARG.search(rad)
        ]
        self.assertTrue(rader)
        self.assertEqual([r for r in rader if "light-dark(" not in r[1]], [])
