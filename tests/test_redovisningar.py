"""Krav: K42 i docs/02-KRAV.md, ADR-0065. Kod: src/kommunhandlingar/webbplats/
sparslag.py."""

import csv
import re
import tempfile
import unittest
from pathlib import Path

from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.webbplats import spar
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.sparkort import Vy
from kommunhandlingar.webbplats.sparsida import sparsida
from kommunhandlingar.webbplats.sparslag import REDOVISNINGAR
from tests.test_mal import ROT
from tests.test_webbplats import REPO, TID, dokument, exempelby

RUBRIK = "organ,redovisning,ar,fas,varde,text,kalla,tolkad\n"
BUDGET = "fsn/2024/2024-01-17/handlingar.md"
PROTOKOLL = "fsn/2024/2024-05-15/protokoll.md"
TEXTER = {
    BUDGET: "<!-- sida 1 -->\n\nRedovisning av simskolan\n",
    PROTOKOLL: "<!-- sida 1 -->\n\nSimskolan redovisas\n\nTillsynsrapport 2023\n",
}
SIM = "fsn,Redovisning av simskolan,2024"
RADER = (
    f"{SIM},direktiv,,Redovisning av simskolan,{BUDGET}#sida-1,\n"
    f"{SIM},redovisad,,Simskolan redovisas,{PROTOKOLL}#sida-1,ja\n"
    f"fsn,Tillsyn,2024,aterkommande,,Tillsynsrapport 2023,{PROTOKOLL}#sida-1,\n"
)
# Källans egna ord för ett direktiv som beställer en redovisning (ADR-0065).
BESTALLNING = re.compile(r"(Redovisning|Utredning|Information)\b")


def sida() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(RUBRIK + RADER, encoding="utf-8")
        for dok, text in TEXTER.items():
            organ, _, datum, _ = dok.split("/")
            (data / dok).parent.mkdir(parents=True, exist_ok=True)
            (data / dok).write_text(
                dokument(organ, datum, text=text, per_sida="[ok]"), encoding="utf-8"
            )
        stegen = spar.las(fil, exempelby(), data, REDOVISNINGAR)
    vy = Vy.over(REDOVISNINGAR, exempelby(), stegen)
    return sparsida(Mall([exempelby()], REPO, TID), vy, stegen)


class TestSidan(unittest.TestCase):
    def test_bestallda_och_aterkommande_redovisningar_star_med(self):
        html = sida()
        self.assertIn(">Redovisning av simskolan</a></th>", html)
        self.assertIn(">Tillsyn</a></th>", html)
        self.assertIn("<dt>redovisad för nämnden</dt><dd>1</dd>", html)
        self.assertIn("<dt>återkommande redovisning</dt><dd>1</dd>", html)


class TestKungsbacka(unittest.TestCase):
    def test_filen_gar_ihop_med_kommunfilen_och_poolen(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        fil = ROT / "redovisningar" / "kungsbacka.csv"
        stegen = spar.las(fil, kungsbacka, ROT / "data" / "kungsbacka", REDOVISNINGAR)
        self.assertEqual({s.organ for s in stegen}, {"fg", "vo"})
        self.assertEqual(fil.read_bytes().count(b"\r"), 0)

    def test_bestallda_redovisningar_star_inte_bland_malen(self):
        with (ROT / "mal" / "kungsbacka.csv").open(encoding="utf-8") as f:
            rader = list(csv.DictReader(f))
        bestallda = [
            r["rubrik"]
            for r in rader
            if r["slag"] == "direktiv" and BESTALLNING.match(r["rubrik"])
        ]
        self.assertEqual(bestallda, [])
