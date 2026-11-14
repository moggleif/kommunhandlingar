"""Krav: K51 i docs/02-KRAV.md, ADR-0074. Kod: src/kommunhandlingar/webbplats/
mall.py, tema.js och stilarna i samma katalog."""

import re
import unittest
from pathlib import Path

from kommunhandlingar import webbplats
from kommunhandlingar.webbplats import sidor
from kommunhandlingar.webbplats.mall import STIL, Mall
from tests.test_webbplats import REPO, TID, exempelby

KATALOG = Path(webbplats.__file__).parent
FARG = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b")


class TestTemat(unittest.TestCase):
    def test_sidan_har_knappen_och_skriptet_i_head(self):
        html = sidor.startsida(Mall([exempelby()], REPO, TID))
        head = html.split("</head>")[0]
        self.assertIn("localStorage", head)
        self.assertIn("color-scheme: light dark", head)
        self.assertIn(
            '<button type="button" class="tema" hidden>Mörkt tema</button>', html
        )

    def test_farger_bara_i_variablerna(self):
        filer = [
            f for monster in ("*.py", "*.css", "*.js") for f in KATALOG.glob(monster)
        ]
        rader = [
            (fil.name, rad)
            for fil in sorted(filer)
            for rad in fil.read_text(encoding="utf-8").splitlines()
            if FARG.search(rad)
        ]
        self.assertTrue(rader)
        self.assertEqual(
            [r for r in rader if r[0] != "mall.py" or "--" not in r[1]], []
        )

    def test_reserven_har_de_ljusa_vardena(self):
        ljusa = dict(re.findall(r"(--[a-z]+): light-dark\((#\w+), #\w+\)", STIL))
        reserv = STIL.split("@supports not")[1].split("} }")[0]
        self.assertEqual(dict(re.findall(r"(--[a-z]+): (#\w+);", reserv + ";")), ljusa)
        self.assertEqual(len(ljusa), 11)
