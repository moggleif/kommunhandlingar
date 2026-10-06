"""Krav: "Ren kod – strikt" i AGENTS.md. Kod: scripts/kontrollera_storlek.py."""

import tempfile
import unittest
from pathlib import Path

from scripts.kontrollera_storlek import MAX_RADER_FIL, MAX_RADER_FUNKTION, brott


def funktion(rader: int, undantag: str = "") -> str:
    kropp = "".join("    x = 1\n" for _ in range(rader - 1))
    return f"def f():{undantag}\n{kropp}"


class TestKontrolleraStorlek(unittest.TestCase):
    def kontrollera(self, kallkod: str) -> list[str]:
        with tempfile.TemporaryDirectory() as katalog:
            fil = Path(katalog) / "modul.py"
            fil.write_text(kallkod, encoding="utf-8")
            return brott([fil])

    def test_funktion_vid_gransen_godkanns(self):
        self.assertEqual(self.kontrollera(funktion(MAX_RADER_FUNKTION)), [])

    def test_funktion_over_gransen_underkanns(self):
        self.assertEqual(len(self.kontrollera(funktion(MAX_RADER_FUNKTION + 1))), 1)

    def test_funktion_med_undantag_godkanns(self):
        kallkod = funktion(MAX_RADER_FUNKTION + 1, "  # undantag: tabell")
        self.assertEqual(self.kontrollera(kallkod), [])

    def test_fil_over_gransen_underkanns(self):
        kallkod = "x = 1\n" * (MAX_RADER_FIL + 1)
        self.assertEqual(len(self.kontrollera(kallkod)), 1)

    def test_fil_med_undantag_godkanns(self):
        kallkod = "# undantag: genererad\n" + "x = 1\n" * MAX_RADER_FIL
        self.assertEqual(self.kontrollera(kallkod), [])


if __name__ == "__main__":
    unittest.main()
