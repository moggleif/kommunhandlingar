"""Krav: K73 i docs/02-KRAV.md, ADR-0100. Testar
src/kommunhandlingar/kand_inlasning.py med påhittade dokument."""

import tempfile
import unittest
from collections import Counter
from pathlib import Path

from kommunhandlingar import kand_inlasning


def dokument(katalog: Path, namn: str, per_sida: str) -> None:
    katalog.mkdir(parents=True, exist_ok=True)
    text = f"---\nkommun: x\nkvalitet_per_sida: {per_sida}\n---\n"
    (katalog / f"{namn}.md").write_text(text, encoding="utf-8")


class TestKandInlasning(unittest.TestCase):
    def test_sidorna_raknas_per_kvalitet(self):
        with tempfile.TemporaryDirectory() as t:
            kommun = Path(t) / "kommunen"
            dokument(kommun / "ks", "a", "[ok, ej-konverterad, ointressant]")
            dokument(kommun / "kf", "b", "[ocr, bild]")
            dokument(kommun / "kf", "c", "null")
            sidor, utan_sidor = kand_inlasning.rakna(kommun)
        self.assertEqual(sum(sidor.values()), 5)
        self.assertEqual((sidor["ej-konverterad"], utan_sidor), (1, 1))

    def test_raden_ger_andelen_kanda_sidor(self):
        sidor = Counter({"ok": 3, "ointressant": 4, "ej-konverterad": 1})
        rad = kand_inlasning.rad("kommunen", sidor, 2)
        self.assertTrue(rad.startswith("kommunen: 7 av 8 sidor"))
        self.assertIn("(87,50 %)", rad)
        self.assertIn("ointressant 4", rad)
        self.assertTrue(rad.endswith("2 dokument utan sidor"))

    def test_kommun_utan_sidor_har_ingen_andel(self):
        self.assertIn("(– %)", kand_inlasning.rad("kommunen", Counter(), 3))
