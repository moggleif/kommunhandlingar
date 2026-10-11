"""Krav: K21 i docs/02-KRAV.md, ADR-0026. Kod: src/kommunhandlingar/webbplats/."""

import gzip
import json
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
from tests.test_webbplats_dokument import TABELL, las

OCR = {"kvalitet": "ocr", "per_sida": "[ok, ocr]", "tal": "[2]"}


def dokumentsidan(text: str) -> str:
    kommun = exempelby()
    return dokumentsida(Mall([kommun], REPO, TID), kommun, las(text), text)


# Bygger webbplatsen ur dokumenten, kör Pagefind och ger det som indexerades
# för varje sida, ur Pagefinds fragment.
def indexera(*texter: str) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        rot, ut = Path(tmp) / "repo", Path(tmp) / "ut"
        (rot / "kommuner").mkdir(parents=True)
        shutil.copy(FIXTURER / "exempelby.toml", rot / "kommuner")
        for nr, text in enumerate(texter):
            mote = rot / "data" / "exempelby" / "fsn" / "2024" / f"2024-05-0{nr + 1}"
            mote.mkdir(parents=True)
            (mote / "protokoll.md").write_text(text, encoding="utf-8")
        bygg(rot, ut, REPO, TID)
        pagefind = [sys.executable, "-m", "pagefind", "--site", str(ut)]
        subprocess.run(pagefind, capture_output=True, check=True)
        return [fragment(f) for f in (ut / "pagefind" / "fragment").iterdir()]


def fragment(fil: Path) -> dict:
    data = gzip.decompress(fil.read_bytes()).decode()
    return json.loads(data[data.index("{") :])


class TestPagefind(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sidor = indexera(dokument(datum="2024-05-01", **OCR), dokument(text=TABELL))
        cls.ocr = next(s for s in cls.sidor if "2024-05-01" in s["url"])

    def test_bara_dokumenten_indexeras(self):
        self.assertEqual(len(self.sidor), 2)

    def test_bara_dokumentets_text_ar_sokbar(self):
        innehall = " ".join(s["content"] for s in self.sidor)
        for text in ("Text", "Mer text", "Belopp", "Exempel"):
            self.assertIn(text, innehall)
        for egen in ("Kvalitet", "obekräftade.", "Osäker tabell", "3f9a", "Start"):
            self.assertNotIn(egen, innehall)

    def test_traffen_leder_till_sidan_med_markeringen(self):
        self.assertEqual(
            [(a["id"], a["text"]) for a in self.ocr["anchors"]],
            [("sida-1", "Sida 1"), ("sida-2", "Sida 2 – obekräftade tal")],
        )

    def test_titeln_med_kvalitet_och_filtren(self):
        self.assertEqual(
            self.ocr["meta"]["title"],
            "Förskole- och skolnämnden 2024-05-01: protokoll – kvalitet: ocr",
        )
        self.assertEqual(
            self.ocr["filters"],
            {
                "Organ": ["Förskole- och skolnämnden"],
                "År": ["2024"],
                "Typ": ["protokoll"],
                "Kvalitet": ["ocr"],
            },
        )


class TestDokumentsidan(unittest.TestCase):
    def test_titeln_utan_kvalitet_nar_den_ar_full(self):
        self.assertIn(
            '<span data-pagefind-meta="title">'
            "Förskole- och skolnämnden 2024-05-02: protokoll</span>",
            dokumentsidan(dokument()),
        )

    def test_dokument_utan_text_ar_inte_sokbart(self):
        html = dokumentsidan(dokument(text=""))
        self.assertIn("<p data-pagefind-ignore>Dokumentet har ingen text.</p>", html)


class TestSoksidan(unittest.TestCase):
    def test_soksidan_med_pagefind_och_utan_javascript(self):
        html = soksida(Mall([exempelby()], REPO, TID))
        self.assertIn('<script src="pagefind/pagefind-ui.js"></script>', html)
        self.assertIn(
            "<noscript><p>Sök kräver JavaScript. Utan det nås dokumenten från "
            'kommunernas sidor: <a href="exempelby.html">Exempelby kommun</a>.',
            html,
        )

    def test_menyn_lankar_till_soksidan_som_ensam_har_javascript(self):
        mall = Mall([exempelby()], REPO, TID)
        for html in (sidor.startsida(mall), dokumentsidan(dokument())):
            self.assertIn('<a href="sok.html">Sök</a>', html.replace("../", ""))
            self.assertNotIn("<script", html)
