"""Krav: K14 och K73 i docs/02-KRAV.md. Testar känd inläsning på
statussidan i src/kommunhandlingar/webbplats/sidor.py."""

import unittest

from kommunhandlingar import frontmatter
from kommunhandlingar.webbplats import sidor
from kommunhandlingar.webbplats.mall import Mall
from tests.test_webbplats import REPO, TID, dokument, exempelby


def statussida(*texter: str) -> str:
    kommun = exempelby()
    dok = [frontmatter.las(text) for text in texter]
    return sidor.statussida(Mall([kommun], REPO, TID), kommun, dok)


class TestKandInlasningSida(unittest.TestCase):
    def test_overst_och_per_organ(self):
        html = statussida(
            dokument(per_sida="[ok, ej-konverterad, ointressant]"),
            dokument(per_sida="[ocr]", kvalitet="ocr"),
        )
        self.assertIn("<p>Känd inläsning: 3 av 4 sidor (75,00 %).</p>", html)
        self.assertIn("<h2>Sidor per organ</h2>", html)
        self.assertIn('<th scope="col">ointressant</th>', html)
        self.assertIn('<td class="tal">75,00 %</td></tr>', html)

    def test_pool_utan_sidor_har_ingen_andel(self):
        self.assertIn("(– %)", statussida())
