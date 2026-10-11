"""Krav: K21 i docs/02-KRAV.md, ADR-0026. Kod: src/kommunhandlingar/webbplats/."""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from kommunhandlingar.webbplats import sidor
from kommunhandlingar.webbplats.bygg import bygg
from kommunhandlingar.webbplats.dokumentsida import dokumentsida
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.sok import soksida
from tests.test_webbplats import FIXTURER, REPO, TID, dokument, exempelby
from tests.test_webbplats_dokument import las


def dokumentsidan(text: str) -> str:
    kommun = exempelby()
    return dokumentsida(Mall([kommun], REPO, TID), kommun, las(text), text)


class TestDokumentsidanIndexeras(unittest.TestCase):
    def test_bara_texten_ar_sokbar(self):
        html = dokumentsidan(dokument())
        self.assertLess(html.index("Härkomst"), html.index("data-pagefind-body"))
        self.assertLess(html.index("data-pagefind-body"), html.index('id="sida-1"'))

    def test_titeln_utan_kvalitet_nar_den_ar_full(self):
        html = dokumentsidan(dokument())
        self.assertIn(
            '<span data-pagefind-meta="title">'
            "Förskole- och skolnämnden 2024-05-02: protokoll</span>",
            html,
        )

    def test_titeln_med_kvalitet_nar_den_inte_ar_full(self):
        html = dokumentsidan(dokument(kvalitet="ocr", per_sida="[ok, ocr]"))
        self.assertIn("2024-05-02: protokoll – kvalitet: ocr</span>", html)

    def test_filter_for_organ_ar_typ_och_kvalitet(self):
        html = dokumentsidan(dokument(kvalitet="ocr", per_sida="[ok, ocr]"))
        for filter_, varde in (
            ("Organ", "Förskole- och skolnämnden"),
            ("År", "2024"),
            ("Typ", "protokoll"),
            ("Kvalitet", "ocr"),
        ):
            self.assertIn(
                f'<span data-pagefind-filter="{filter_}">{varde}</span>', html
            )

    def test_obekraftade_tal_i_sidans_rubrik(self):
        html = dokumentsidan(dokument(per_sida="[ok, ok]", tal="[2]"))
        self.assertIn('<h2 id="sida-1">Sida 1</h2>', html)
        self.assertIn('<h2 id="sida-2">Sida 2 – obekräftade tal</h2>', html)


class TestSoksidan(unittest.TestCase):
    def test_soksidan_med_pagefind_och_utan_javascript(self):
        html = soksida(Mall([exempelby()], REPO, TID))
        self.assertIn('<script src="pagefind/pagefind-ui.js"></script>', html)
        self.assertIn("Sök kräver JavaScript", html)
        self.assertIn("<noscript><p>Sök kräver JavaScript.", html)
        self.assertIn('<a href="exempelby.html">Exempelby kommun</a>', html)

    def test_menyn_lankar_till_soksidan_och_bara_den_har_javascript(self):
        mall = Mall([exempelby()], REPO, TID)
        for html in (sidor.startsida(mall), dokumentsidan(dokument())):
            self.assertIn("sok.html", html)
            self.assertNotIn("<script", html)


class TestPagefind(unittest.TestCase):
    def test_bara_dokumenten_indexeras_med_filtren(self):
        with tempfile.TemporaryDirectory() as tmp:
            rot, ut = Path(tmp) / "repo", Path(tmp) / "ut"
            (rot / "kommuner").mkdir(parents=True)
            shutil.copy(FIXTURER / "exempelby.toml", rot / "kommuner")
            for datum in ("2023-02-01", "2024-05-02"):
                mote = rot / "data" / "exempelby" / "fsn" / datum[:4] / datum
                mote.mkdir(parents=True)
                (mote / "protokoll.md").write_text(dokument(datum=datum))
            bygg(rot, ut, REPO, TID)
            utskrift = subprocess.run(
                [sys.executable, "-m", "pagefind", "--site", str(ut)],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        self.assertIn("Indexed 2 pages", utskrift)
        self.assertEqual(re.findall(r"Indexed (\d+) filters", utskrift), ["4"])
