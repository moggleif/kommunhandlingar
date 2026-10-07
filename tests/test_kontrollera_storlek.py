"""Krav: "Ren kod – strikt" i AGENTS.md. Kod: scripts/kontrollera_storlek.py."""

import tempfile
import unittest
from pathlib import Path

from scripts.kontrollera_storlek import (
    MAX_RADER_FIL,
    MAX_RADER_FUNKTION,
    ROT,
    brott_i_fil,
    pythonfiler,
)


def funktion(rader: int, huvud: str = "def f():") -> str:
    kropp = "".join("    x = 1\n" for _ in range(rader - 1))
    return f"{huvud}\n{kropp}"


class TestKontrolleraStorlek(unittest.TestCase):
    def kontrollera(self, kallkod: str) -> list[str]:
        with tempfile.TemporaryDirectory() as katalog:
            fil = Path(katalog) / "modul.py"
            fil.write_text(kallkod, encoding="utf-8")
            return brott_i_fil(fil)

    def test_funktion_vid_gransen_godkanns(self):
        self.assertEqual(self.kontrollera(funktion(MAX_RADER_FUNKTION)), [])

    def test_funktion_over_gransen_underkanns(self):
        self.assertEqual(len(self.kontrollera(funktion(MAX_RADER_FUNKTION + 1))), 1)

    def test_async_funktion_over_gransen_underkanns(self):
        kallkod = funktion(MAX_RADER_FUNKTION + 1, "async def f():")
        self.assertEqual(len(self.kontrollera(kallkod)), 1)

    def test_undantag_med_skal_godkanns(self):
        kallkod = funktion(MAX_RADER_FUNKTION + 1, "def f():  # undantag: tabell")
        self.assertEqual(self.kontrollera(kallkod), [])

    def test_undantag_utan_skal_underkanns(self):
        kallkod = funktion(MAX_RADER_FUNKTION + 1, "def f():  # undantag:")
        self.assertEqual(len(self.kontrollera(kallkod)), 1)

    def test_fil_vid_gransen_godkanns(self):
        self.assertEqual(self.kontrollera("x = 1\n" * MAX_RADER_FIL), [])

    def test_fil_over_gransen_underkanns(self):
        kallkod = "x = 1\n" * (MAX_RADER_FIL + 1)
        self.assertEqual(len(self.kontrollera(kallkod)), 1)

    def test_fil_med_undantag_godkanns(self):
        kallkod = "# undantag: genererad\n" + "x = 1\n" * MAX_RADER_FIL
        self.assertEqual(self.kontrollera(kallkod), [])

    def test_sidbrytning_i_strang_gor_inte_fel(self):
        self.assertEqual(self.kontrollera('s = "a\x0cb"\n'), [])

    def test_src_kontrolleras(self):
        self.assertIn(ROT / "src" / "kommunhandlingar" / "monster.py", pythonfiler())


if __name__ == "__main__":
    unittest.main()
