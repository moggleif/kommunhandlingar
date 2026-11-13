"""Krav: K44 i docs/02-KRAV.md, ADR-0067. Kod: src/kommunhandlingar/webbplats/
sparslag.py."""

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.webbplats import spar
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.sparkort import Vy
from kommunhandlingar.webbplats.sparsida import sparsida
from kommunhandlingar.webbplats.sparslag import DETALJPLANER
from tests.test_mal import ROT
from tests.test_webbplats import REPO, TID, dokument, exempelby

RUBRIK = "organ,detaljplan,ar,fas,varde,text,kalla,tolkad\n"
NAMND = "bun/2024/2024-03-14/protokoll.md"
BESLUT = "fsn/2025/2025-02-11/protokoll.md"
TEXTER = {
    NAMND: "<!-- sida 1 -->\n\nSamråd av detaljplan för Skolan 1:2\n",
    BESLUT: "<!-- sida 1 -->\n\nAntagande av detaljplan för Skolan 1:2\n",
}
PLAN = "bun,Skola inom Skolan 1:2"
RADER = (
    f"{PLAN},2024,samrad,,Samråd av detaljplan för Skolan 1:2,{NAMND}#sida-1,\n"
    f"{PLAN},2025,antagande,,Antagande av detaljplan för Skolan 1:2,"
    f"{BESLUT}#sida-1,\n"
)


def sida(projekten: dict | None = None) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(RUBRIK + RADER, encoding="utf-8")
        for dok, text in TEXTER.items():
            organ, _, datum, _ = dok.split("/")
            (data / dok).parent.mkdir(parents=True, exist_ok=True)
            (data / dok).write_text(
                dokument(organ, datum, text=text, per_sida="[ok]"), encoding="utf-8"
            )
        stegen = spar.las(fil, exempelby(), data, DETALJPLANER)
    vy = replace(Vy.over(DETALJPLANER, exempelby(), stegen), projekt=projekten or {})
    return sparsida(Mall([exempelby()], REPO, TID), vy, stegen)


class TestSidan(unittest.TestCase):
    def test_planen_foljs_till_ett_annat_organs_beslut(self):
        html = sida()
        self.assertIn(">Skola inom Skolan 1:2</a></th>", html)
        self.assertIn("<dt>samråd</dt><dd>1</dd>", html)
        self.assertIn("<dt>antagen</dt><dd>1</dd>", html)
        self.assertIn(BESLUT.removesuffix(".md"), html)


class TestKungsbacka(unittest.TestCase):
    def test_filen_gar_ihop_med_kommunfilen_och_poolen(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        fil = ROT / "detaljplaner" / "kungsbacka.csv"
        stegen = spar.las(fil, kungsbacka, ROT / "data" / "kungsbacka", DETALJPLANER)
        self.assertEqual({s.organ for s in stegen}, {"bygg"})
        self.assertEqual(fil.read_bytes().count(b"\r"), 0)
